from flask import Flask, render_template, request, jsonify, make_response, send_file
from dotenv import load_dotenv
import re
import os
import requests
import json
import tempfile
import io
from datetime import datetime
from models.invitation_model import Invitation
from models.place_model import Place
from models.event_plan_model import EventPlan
from agno.agent import Agent
from agno.models.google import Gemini
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

load_dotenv()
app = Flask(__name__)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
gemini_api_key = os.getenv('GEMINI_API_KEY')
gemini_model = Gemini(api_key=gemini_api_key)
planner_agent = Agent(model=gemini_model)

# Próba rejestracji czcionki DejaVu (bezpieczna czcionka dla polskich znaków)
try:
    pdfmetrics.registerFont(TTFont('DejaVu', 'DejaVuSans.ttf'))
    FONT_NAME = 'DejaVu'
except:
    FONT_NAME = 'Helvetica'  # Fallback do domyślnej czcionki


def search_places(location, event_type):
    query = f"{event_type} in {location}"
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&key={GOOGLE_API_KEY}"
    try:
        response = requests.get(url)
        results = response.json().get('results', [])
        print(results)
        return [
            Place(
                name=place['name'],
                address=place.get('formatted_address', 'Brak adresu'),
                rating=str(place.get('rating', 'Brak oceny'))
            ).model_dump()
            for place in results[:10]
        ]
    except Exception as e:
        return [Place(name="Brak wyników", address="Nie znaleziono", rating="N/A").model_dump()]


def extract_json(text):
    match = re.search(r"```json\n(.+?)\n```", text, re.DOTALL)
    if match:
        return match.group(1)
    return text


def generate_event_description(event_schedule):
    prompt = f"""
        Jesteś AI asystentem wspomagającym planowanie wydarzeń.
        Na podstawie harmonogramu: {event_schedule} wygeneruj zwięzły opis planowanego wydarzenia w 2-3 zdaniach.
    """
    try:
        result = planner_agent.run(prompt)
        return result.content.strip()
    except Exception as e:
        return f"Błąd podczas generowania opisu: {str(e)}"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/plan_event', methods=['POST'])
def plan_event():
    data = request.form
    event_type = data.get('event_type')
    event_description = data.get('event_description')
    num_people = data.get('num_people')
    budget = data.get('budget')
    location = data.get('location')
    preferences = data.get('preferences', 'Brak')
    start_time = data.get('start_time', '')
    end_time = data.get('end_time', '')

    places = search_places(location, event_type)
    print(places)

    # Dodajemy informacje o czasie do promptu
    time_info = ""
    if start_time and end_time:
        time_info = f"Planowany czas wydarzenia: od {start_time} do {end_time}. "
    elif start_time:
        time_info = f"Planowana godzina rozpoczęcia: {start_time}. "
    elif end_time:
        time_info = f"Planowana godzina zakończenia: {end_time}. "

    prompt = f"""
        Jesteś AI asystentem do planowania wydarzeń.

        Zorganizuj wydarzenie typu: "{event_type}" dla {num_people} osób w lokalizacji "{location}".
        Budżet: {budget} PLN
        Preferencje uczestników: {preferences}
        {time_info}
        Dostępne miejsca:
        {json.dumps(places, indent=2)}

        Zaproponuj:
        - nazwę i adres wybranego miejsca
        - harmonogram (godziny) - {time_info and "uwzględnij podane godziny" or "zaproponuj odpowiednie godziny"}
        - listę proponowanych aktywności

        ZASADY ODPOWIEDZI:
        1. Jeżeli podane oczekiwania użytkownika, są nierealne (np. budżet), zaproponuj alternatywę wpasującą się we wzór odpowiedzi.
        2. Wśród aktywności zawieraj tylko aktywności dodatkowe, które nie mają powiązania z naturą wydarzenia (np. nie na wesele nie wpisuj jako aktywności ceremonii zaślubin)
        3. Komentarz od asystenta powinien zawierać nie więcej niż 3 zdania i być zwięzły
        4. Jeśli podano godziny rozpoczęcia/zakończenia, uwzględnij je w harmonogramie

        Odpowiedź w formacie JSON:
        {{
          "comment_from_assistant": "...",
          "venue_name": "...",
          "venue_address": "...",
          "schedule": [
            {{ "hour": "...", "description": "..." }},
            ...
          ],
          "activities": ["...", "..."]
        }}
        """

    try:
        result = planner_agent.run(prompt)
        print(result.content)
        response = extract_json(result.content)
        parsed_response = json.loads(response)
        event_plan = EventPlan.model_validate(parsed_response)
        event_description = generate_event_description(event_plan.schedule)
        print(event_plan)
        suggestions = (
            f"Miejsce: {event_plan.venue_name}\n"
            f"Adres: {event_plan.venue_address}\n"
            f"Harmonogram: {event_plan.schedule}\n"
            f"Aktywności: {', '.join(event_plan.activities)}\n"
        )
    except Exception as e:
        suggestions = f"Błąd: {str(e)}"
        event_plan = None

    return render_template('suggestions_page.html',
                           suggestions=suggestions,
                           places=places,
                           event_plan=event_plan,
                           event_type=event_type,
                           event_description=event_description,
                           start_time=start_time,
                           end_time=end_time)


@app.route('/generate_invitation', methods=['POST'])
def generate_invitation():
    event_details = request.form.get('event_details', '')
    tone = request.form.get('tone', 'neutralny')
    organizers = request.form.get('organizers', '')
    event_type = request.form.get('event_type', '')
    length = request.form.get('length', 'średni')
    date = request.form.get('date', '')
    time = request.form.get('time', '')
    venue = request.form.get('venue', '')

    prompt = f"""
        Stwórz zaproszenie od {organizers} na wydarzenie zawarte w tym opisie: "{event_details}"
        Styl zaproszenia: {tone}
        Długość zaproszenia: {length} (krótki - do 3 zdań, średni - 3-6 zdań, długi - ponad 6 zdań)
        Data: {date}
        Godzina: {time}
        Miejsce: {venue}
        Zaproszenie ma być dopasowane do stylu oraz do typu wydarzenia: {event_type}.

        Format JSON:
        {{
          "invitation_text": "..."
        }}
        """
    try:
        result = planner_agent.run(prompt)
        response = extract_json(result.content)
        parsed_response = json.loads(response)
        invitation = Invitation.model_validate(parsed_response)

        return jsonify({'invitation': invitation.invitation_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/update_event_plan', methods=['POST'])
def update_event_plan():
    """Endpoint do aktualizacji planu wydarzenia"""
    data = request.get_json()

    # Tu możesz dodać logikę do zapisywania zmian w bazie danych
    # Na razie zwracamy sukces
    return jsonify({'success': True, 'message': 'Plan został zaktualizowany'})


@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    """Endpoint do generowania i pobierania PDF z harmonogramem"""
    try:
        data = request.get_json()
        event_type = data.get('event_type', 'Wydarzenie')
        venue_name = data.get('venue_name', '')
        venue_address = data.get('venue_address', '')
        schedule = data.get('schedule', [])
        activities = data.get('activities', [])
        start_time = data.get('start_time', '')
        end_time = data.get('end_time', '')

        # Przygotowanie bufora dla PDF
        buffer = io.BytesIO()

        # Tworzenie dokumentu PDF
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            title=f'Plan wydarzenia: {event_type}',
            author='Planer Wydarzeń'
        )

        # Style
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Title'],
            fontName=FONT_NAME,
            fontSize=16,
            textColor=colors.purple
        )
        heading_style = ParagraphStyle(
            'Heading',
            parent=styles['Heading2'],
            fontName=FONT_NAME,
            fontSize=14,
            textColor=colors.purple
        )
        normal_style = ParagraphStyle(
            'Normal',
            parent=styles['Normal'],
            fontName=FONT_NAME,
            fontSize=10
        )

        # Elementy dokumentu
        elements = []

        # Tytuł
        elements.append(Paragraph(f'Plan wydarzenia: {event_type}', title_style))
        elements.append(Paragraph(f'Wygenerowano: {datetime.now().strftime("%d.%m.%Y")}', normal_style))
        elements.append(Spacer(1, 20))

        # Informacja o czasie
        if start_time or end_time:
            elements.append(Paragraph('Planowany czas wydarzenia', heading_style))
            time_text = ''
            if start_time and end_time:
                time_text = f'Od {start_time} do {end_time}'
            elif start_time:
                time_text = f'Rozpoczęcie: {start_time}'
            elif end_time:
                time_text = f'Zakończenie: {end_time}'
            elements.append(Paragraph(time_text, normal_style))
            elements.append(Spacer(1, 15))

        # Miejsce wydarzenia
        elements.append(Paragraph('Miejsce wydarzenia', heading_style))
        elements.append(Paragraph(f'<b>Nazwa:</b> {venue_name}', normal_style))
        elements.append(Paragraph(f'<b>Adres:</b> {venue_address}', normal_style))
        elements.append(Spacer(1, 15))

        # Harmonogram
        elements.append(Paragraph('Harmonogram', heading_style))

        # Tabela harmonogramu
        if schedule:
            schedule_data = [['Godzina', 'Opis']]
            for item in schedule:
                schedule_data.append([item.get('hour', ''), item.get('description', '')])

            schedule_table = Table(schedule_data, colWidths=[80, 350])
            schedule_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lavender),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), FONT_NAME),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 1), (-1, -1), FONT_NAME),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white])
            ]))
            elements.append(schedule_table)
        else:
            elements.append(Paragraph('Brak pozycji w harmonogramie', normal_style))

        elements.append(Spacer(1, 15))

        # Aktywności
        elements.append(Paragraph('Aktywności dodatkowe', heading_style))
        if activities:
            for i, activity in enumerate(activities):
                elements.append(Paragraph(f"• {activity}", normal_style))
        else:
            elements.append(Paragraph('Brak dodatkowych aktywności', normal_style))

        elements.append(Spacer(1, 30))

        # Stopka
        elements.append(Paragraph('Wygenerowano przez Planer Wydarzeń',
                                  ParagraphStyle('Footer', parent=styles['Normal'],
                                                 alignment=1, textColor=colors.grey)))

        # Generowanie PDF
        doc.build(elements)

        # Przygotowanie odpowiedzi
        buffer.seek(0)
        response = make_response(buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers[
            'Content-Disposition'] = f'attachment; filename=Plan-{event_type}-{datetime.now().strftime("%Y%m%d")}.pdf'

        return response

    except Exception as e:
        print(f"Błąd podczas generowania PDF: {str(e)}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)

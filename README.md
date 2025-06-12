# 🎉 Eventful - AI-assistance app for event planning - aplikacja z asystentem AI do planowania wydarzeń

Aplikacja wykorzystująca asystenta AI do  planowania wydarzeń, generowania harmonogramów i tworzenia spersonalizowanych zaproszeń.
Projekt łączy zaawansowane modele AI z intuicyjnym interfejsem użytkownika, aby uprościć proces organizacji wydarzeń.

Aplikacja stworzona tylko na podstawie działania asystentów AI.

## 🎯 Opis
Eventful to aplikacja webowa, która automatyzuje proces planowania wydarzeń poprzez:
- Generowanie szczegółowych harmonogramów na podstawie preferencji użytkownika
- Wyszukiwanie i rekomendowanie odpowiednich miejsc
- Tworzenie spersonalizowanych zaproszeń
- Generowanie profesjonalnych dokumentów PDF z planami wydarzeń

## 📖 Użytkowanie

### Wprowadź podstawowe informacje o wydarzeniu:
   
1. Typ wydarzenia (np. urodziny, konferencja, wesele)
2. Liczba uczestników
3. Budżet
4. Lokalizacja
5. Preferencje (opcjonalnie)

### 2. Otrzymaj wygenerowany plan wydarzenia z:

1. Rekomendowanym miejscem
2. Szczegółowym harmonogramem
3. Listą proponowanych aktywności

### 3. Edytuj plan w czasie rzeczywistym:

1. Modyfikuj elementy harmonogramu
2. Dodawaj lub usuwaj aktywności
3. Wybieraj alternatywne miejsca

### 4. Generuj i pobieraj dokumenty:

1. Eksportuj plan jako PDF
2. Twórz spersonalizowane treści zaproszeń z możliwością skopiowania

## 🎯 Biznes Case

Organizatorzy wydarzeń i firmy eventowe borykają się z następującymi wyzwaniami:

- **Czasochłonność** – Planowanie wydarzenia zajmuje kilka godzin pracy
- **Powtarzalność** – Wiele zadań przy planowaniu podobnych wydarzeń się powtarza
- **Personalizacja** – Trudność w szybkim dostosowaniu planów do specyficznych wymagań
- **Koordynacja** – Zarządzanie wieloma elementami jednocześnie (miejsce, catering, rozrywka)

Eventful AI rozwiązuje te problemy, redukując czas planowania i zwiększając jakość organizowanych wydarzeń.

## 📸 Wygląd
![image](https://github.com/user-attachments/assets/22a1bccc-057d-41ee-b83d-a65b0b75d561)
![image](https://github.com/user-attachments/assets/18c83340-4ca4-400e-a72b-ec12053eb955)
![image](https://github.com/user-attachments/assets/94de12ad-a162-4d33-ab01-0876d7d281c8)
![image](https://github.com/user-attachments/assets/99f7686d-d5bd-43cf-89ca-6813274bfcb7)
![image](https://github.com/user-attachments/assets/557e8f8d-4b15-4e3b-b73c-6dc2ecf6a5b6)

## ✨ Wygenerowany PDF
![image](https://github.com/user-attachments/assets/1c4dcf17-7234-4be3-a4fe-bc162dd6651d)

## 🛠️ Technologie
### Backend:
- Flask (Python)
- ReportLab (generowanie PDF)
- Jinja2 (szablony HTML)
- Pydantic (walidacja danych)

### AI / ML:
- Google Gemini API (generowanie treści)
- Agno Agent (framework dla agentów AI)
- Google Places API (wyszukiwanie lokalizacji)

### Frontend:
- HTML5/CSS3
- JavaScript
- Tailwind CSS
- Fetch API


## 📋 Wymagania
- Python: 3.8+

### Główne zależności:

```plaintext
flask==2.3.3
python-dotenv==1.0.0
requests==2.31.0
google-generativeai==0.5.0
pydantic==2.11.5
reportlab==4.0.4
agno~=1.6.0
Jinja2==3.1.2
```

## ▶️ Uruchom aplikację
1. Sklonuj repozytorium:
```shellscript
git clone https://github.com/mtorzynska/eventful-app.git
cd eventful-app
```
2. Zainstaluj zależności:
```shellscript
pip install -r requirements.txt
```
3. Skonfiguruj zmienne środowiskowe (skopiuj `.env.example` do `.env` i uzupełnij klucze API)
4. Uruchom aplikację:
```shellscript
python main.py
```
Aplikacja będzie dostępna pod adresem: [http://localhost:5000](http://localhost:5000)

## 🔧 Konfiguracja
### Zmienne środowiskowe
- `GOOGLE_API_KEY` – Klucz API Google Places (wymagany)
- `GEMINI_API_KEY` – Klucz API Google Gemini (wymagany)


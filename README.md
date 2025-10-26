🌤️ Weather App — Step-by-Step Project Walkthrough

A Python GUI app that fetches live weather data for any city using the WeatherAPI service. 
Built for our class project to demonstrate API integration, GUI development with Tkinter/CustomTkinter, 
and event-driven programming.



1) Overview

The Weather App provides a clean, interactive dashboard that shows:
	•	Current temperature, humidity, wind speed, and “feels-like” readings
	•	3-day weather forecast with icons and conditions
	•	°C/°F toggle and automatic day/night theme

💡 Goal: Strengthen Python skills in API requests, JSON parsing, UI layout, and modular class design.

⸻

2) Architecture (Layered & Portable)

User Interface (Tkinter/CustomTkinter)
│
├── WeatherApp class (GUI + event logic)
│     ├── get_weather() – fetches JSON via requests
│     ├── update_display() – updates all UI labels/icons
│     ├── display_forecast() – renders 3-day forecast cards
│     └── toggle_unit() – switches °C / °F dynamically
│
└── WeatherAPI (external service)
        ↳ https://api.weatherapi.com/v1/forecast.json

Notes:

Uses the Model–View–Controller idea in a single class.

Keeps API logic separate from the rendering logic.

Easily portable to Windows, macOS, or Linux.

3) Repo Layout
weather-app/
├── weather.py              # main application
├── assets/                 # optional icons or theme files
├── README.md               # overview & setup
└── video.txt               # YouTube demo link placeholder

4) Data Model

From WeatherAPI JSON:

location.name — city name

location.country — country

location.localtime — local date/time

current.temp_c, current.temp_f — current temp

current.condition.text — weather description

current.humidity, current.wind_kph, current.feelslike_c/f

forecast.forecastday — 3-day forecast array

Internal data handled in:

self.last_data = data  # cached JSON for reuse

5) UI Components
Component	Widget Type	Purpose
City Entry	CTkEntry	Input for city name
Search Button	CTkButton	Triggers API request
Unit Toggle	CTkButton	Switches between °C/°F
City/Date Labels	CTkLabel	Display location & time
Icon Label	CTkLabel (Emoji)	Shows condition (☀️, 🌧️, etc.)
Forecast Frame	CTkFrame	Displays 3-day forecast cards

6) Step-by-Step Flow
1️⃣ Launch

Run:
bash python weather.py

App window loads (600×750) with default light theme.

2️⃣ Search for a city

User types a city name and presses Enter or clicks Search 🔍.

3️⃣ Fetch weather

get_weather() sends an API request with:

params = {"key": API_KEY, "q": city, "days": 3}

4️⃣ Parse data

On success:

Extracts location, current, and forecast info.

Saves it in self.last_data.

5️⃣ Update UI

update_display() updates:

Labels for city, date/time, temp, humidity, wind, and “feels like”

Icon from get_icon() (☀️, ☁️, 🌧️, ❄️, etc.)

Forecast cards via display_forecast()

6️⃣ Toggle Units

Click “Switch to °F” or “Switch to °C.”
App instantly converts all temps by switching to the stored JSON values.

7️⃣ Error Handling

If:

City is blank → messagebox.showwarning("Error", "...")

Invalid name or key → handled via data["error"]["message"]

No internet → caught in a try/except block

7) Visual Layout

✅ Responsive frame with rounded corners
✅ Emoji icons for intuitive conditions
✅ Clean typography (Segoe UI)
✅ Day/night palette toggle ready via ctk.set_appearance_mode()

(Insert your “README/Features” style screenshot here — it mirrors this section perfectly.)

8) Key Features Recap

🌤️ Live weather data via WeatherAPI

🔍 City search with validation

🌡️ Unit toggle (°C ↔ °F)

📅 3-Day forecast preview

⚡ Error handling and feedback

🎨 Modern CustomTkinter UI
Favorites & recent searches	Saved to ~/.weathera.json for persistence
⚡ Async API requests	Prevents UI freezing during slow network calls

🌑 Dark Theme + Modern look	Set via ctk.set_appearance_mode("dark")

🧠 Safe threading	UI updates scheduled through root.after()

🧪 Quick Setup

Dependencies

pip install requests customtkinter pillow


Run the app

python weather.py


API Key Setup
Sign up on weatherapi.com
 and replace in the script:

API_KEY = "YOUR_API_KEY"

9) Final Checklist

☑️ README.md includes setup instructions & screenshots
☑️ Verified on Windows and macOS
☑️ video.txt contains demo link (if recorded)
☑️ Code formatted, comments added
☑️ Handles missing input & API errors gracefully

10) Reflection / Learning Outcomes

Through this project, we learned to:

Integrate a REST API using Python’s requests module

Design an event-driven GUI in Tkinter

Manage state updates efficiently between UI and data

Implement user feedback and validation

Apply readable design principles in Python OOP

Future Enhancements:

Add a 7-day forecast view

Include weather icons from an image API

Implement auto-location detection

Save last searched city to a local file

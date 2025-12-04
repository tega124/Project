🌦️ Weather App

A simple Python application that fetches real-time weather data using the OpenWeatherMap API.

📌 Overview

This Weather App allows users to enter the name of any city in the world and instantly receive:

Current temperature

Weather conditions (clear, cloudy, rain, etc.)

Humidity

Wind speed

It uses the OpenWeatherMap REST API and the requests library to retrieve and parse live weather data.

This project demonstrates:

API integration

JSON parsing

Error handling

Command-line user interaction

📁 Project Structure
weather_app/
│
├── weather.py         # Main Python script that fetches API data
├── weather.json       # (Optional) Stored sample API response
├── requirements.txt   # Dependencies for running the project
└── README.md          # Project documentation

⚙️ Installation & Setup
1. Install Python

Make sure you have Python 3.10+ installed.

2. Install Dependencies

In the project folder, run:

pip install -r requirements.txt

3. Get an API Key

Go to: https://openweathermap.org/api

Create a free account

Copy your API Key

4. Add Your API Key

Open weather.py and replace:

API_KEY = "YOUR_API_KEY_HERE"


with your actual key.

▶️ How to Run the App

Run the script:

python weather.py


Then enter a city name when prompted:

Enter a city name: Toronto
Temperature: 5°C
Description: overcast clouds
Humidity: 81%
Wind speed: 4.1 m/s

🛠️ How It Works

User inputs a city

The script sends a request to OpenWeatherMap’s /weather endpoint

The API responds with JSON data

The script extracts weather details and prints them

Errors (invalid city, network issues, bad API key) are handled gracefully

⚠️ Error Handling

The app will show helpful error messages when:

The city does not exist

The API key is invalid or missing

The network connection fails

The API response is malformed

Example:

Error: City not found. Check the spelling and try again.

🌱 Future Improvements

Planned or possible upgrades:

GUI version (Tkinter / PyQt)

Displaying 5-day and hourly forecasts

Auto-detect user’s location (ip-api)

Saving weather history to JSON or database

Dark/Light terminal themes

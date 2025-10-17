import requests
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime

# ---------------------------- CONFIG ---------------------------------
API_KEY = "85b6ccf0c2bc401ba6904238251710"
BASE_URL = "https://api.weatherapi.com/v1/forecast.json"

# ---------------------------- APP CLASS -------------------------------
class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌤️ Weather App")
        self.root.geometry("600x750")
        self.unit = "C"
        self.last_data = None

        # Appearance
        ctk.set_appearance_mode("light")      # "light" or "dark"
        ctk.set_default_color_theme("green")  # can be "green", "dark-blue", etc.

        # Main Frame
        self.frame = ctk.CTkFrame(self.root, corner_radius=20)
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.create_ui()

    def create_ui(self):
        # Title
        self.title = ctk.CTkLabel(self.frame, text="🌤️ Live Weather Dashboard", font=("Segoe UI", 26, "bold"))
        self.title.pack(pady=(20, 10))

        # Search Entry
        self.search_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.search_frame.pack(pady=10)

        self.city_entry = ctk.CTkEntry(self.search_frame, width=280, placeholder_text="Enter city name...")
        self.city_entry.grid(row=0, column=0, padx=10)
        self.city_entry.bind("<Return>", lambda e: self.get_weather())

        self.search_btn = ctk.CTkButton(self.search_frame, text="Search 🔍", width=100, command=self.get_weather)
        self.search_btn.grid(row=0, column=1)

        # Unit Toggle
        self.unit_btn = ctk.CTkButton(self.frame, text="Switch to °F", width=120, command=self.toggle_unit)
        self.unit_btn.pack(pady=10)

        # Weather Display
        self.city_label = ctk.CTkLabel(self.frame, text="", font=("Segoe UI", 24, "bold"))
        self.city_label.pack(pady=(10, 5))

        self.date_label = ctk.CTkLabel(self.frame, text="", font=("Segoe UI", 14))
        self.date_label.pack(pady=(0, 10))

        self.icon_label = ctk.CTkLabel(self.frame, text="🌎", font=("Segoe UI Emoji", 90))
        self.icon_label.pack(pady=(10, 0))

        self.temp_label = ctk.CTkLabel(self.frame, text="", font=("Segoe UI", 48, "bold"), text_color="#00b4d8")
        self.temp_label.pack(pady=(5, 0))

        self.desc_label = ctk.CTkLabel(self.frame, text="", font=("Segoe UI", 18))
        self.desc_label.pack(pady=(0, 20))

        # Details
        self.details_label = ctk.CTkLabel(self.frame, text="", font=("Segoe UI", 14))
        self.details_label.pack()

        # Forecast Frame
        self.forecast_frame = ctk.CTkFrame(self.frame, corner_radius=15)
        self.forecast_frame.pack(pady=20, padx=20, fill="x")

    def get_weather(self):
        city = self.city_entry.get().strip()
        if not city:
            messagebox.showwarning("Error", "Please enter a city name.")
            return

        try:
            params = {"key": API_KEY, "q": city, "days": 3, "aqi": "no", "alerts": "no"}
            response = requests.get(BASE_URL, params=params, timeout=10)
            data = response.json()

            if "error" in data:
                messagebox.showerror("Error", data["error"]["message"])
                return

            self.last_data = data
            self.update_display()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_display(self):
        data = self.last_data
        loc = data["location"]
        cur = data["current"]
        forecast = data["forecast"]["forecastday"]

        self.city_label.configure(text=f"{loc['name']}, {loc['country']}")
        self.date_label.configure(text=f"🕓 {loc['localtime']}")
        self.icon_label.configure(text=self.get_icon(cur["condition"]["text"]))
        temp = cur["temp_c"] if self.unit == "C" else cur["temp_f"]
        feels = cur["feelslike_c"] if self.unit == "C" else cur["feelslike_f"]
        self.temp_label.configure(text=f"{temp}°{self.unit}")
        self.desc_label.configure(text=cur["condition"]["text"])
        self.details_label.configure(
            text=f"💧 Humidity: {cur['humidity']}%\n💨 Wind: {cur['wind_kph']} km/h\n🌡️ Feels like: {feels}°{self.unit}"
        )
        self.display_forecast(forecast)

    def display_forecast(self, days):
        for w in self.forecast_frame.winfo_children():
            w.destroy()

        for i, d in enumerate(days):
            frame = ctk.CTkFrame(self.forecast_frame, corner_radius=10)
            frame.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")

            date = datetime.strptime(d["date"], "%Y-%m-%d").strftime("%a, %b %d")
            icon = self.get_icon(d["day"]["condition"]["text"])
            avg_temp = d["day"]["avgtemp_c"] if self.unit == "C" else d["day"]["avgtemp_f"]

            ctk.CTkLabel(frame, text=date, font=("Segoe UI", 12, "bold")).pack(pady=(5, 0))
            ctk.CTkLabel(frame, text=icon, font=("Segoe UI Emoji", 40)).pack()
            ctk.CTkLabel(frame, text=f"{avg_temp}°{self.unit}", font=("Segoe UI", 16, "bold")).pack()
            ctk.CTkLabel(frame, text=d["day"]["condition"]["text"], font=("Segoe UI", 11)).pack(pady=(0, 5))

    def get_icon(self, cond):
        text = cond.lower()
        if "sun" in text or "clear" in text:
            return "☀️"
        elif "cloud" in text:
            return "☁️"
        elif "rain" in text or "drizzle" in text:
            return "🌧️"
        elif "snow" in text:
            return "❄️"
        elif "storm" in text or "thunder" in text:
            return "⛈️"
        elif "fog" in text or "mist" in text:
            return "🌫️"
        else:
            return "🌤️"

    def toggle_unit(self):
        self.unit = "F" if self.unit == "C" else "C"
        self.unit_btn.configure(text=f"Switch to °{'C' if self.unit == 'F' else 'F'}")
        if self.last_data:
            self.update_display()


# ---------------------------- RUN APP --------------------------------
if __name__ == "__main__":
    root = ctk.CTk()
    app = WeatherApp(root)
    root.mainloop()

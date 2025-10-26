import requests
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import threading
import json
import os
import pathlib

# ---------------------------- CONFIG ---------------------------------
API_KEY = os.getenv("WEATHER_API_KEY", "YOUR_API_KEY")
BASE_URL = "https://api.weatherapi.com/v1/forecast.json"
STORE = pathlib.Path.home() / ".weather.json"

# ---------------------------- APP CLASS -------------------------------
class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌤️ Weather App")
        self.root.geometry("600x800")
        self.unit = "C"
        self.last_data = None

        # Appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        # Main Frame
        self.frame = ctk.CTkFrame(self.root, corner_radius=20)
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.create_ui()
        self.load_favorites()

    # ---------------------------- UI SETUP ----------------------------
    def create_ui(self):
        # Title
        self.title = ctk.CTkLabel(
            self.frame,
            text="🌤️ Live Weather Dashboard",
            font=("Segoe UI", 26, "bold")
        )
        self.title.pack(pady=(20, 10))

        # Search Frame
        self.search_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.search_frame.pack(pady=10)

        self.city_entry = ctk.CTkEntry(
            self.search_frame, width=220, placeholder_text="Enter city name..."
        )
        self.city_entry.grid(row=0, column=0, padx=5)
        self.city_entry.bind("<Return>", lambda e: self.get_weather_async())

        self.search_btn = ctk.CTkButton(
            self.search_frame, text="Search 🔍", width=90, command=self.get_weather_async
        )
        self.search_btn.grid(row=0, column=1, padx=5)

        self.save_btn = ctk.CTkButton(
            self.search_frame, text="⭐ Save", width=70, command=self.save_favorite
        )
        self.save_btn.grid(row=0, column=2, padx=5)

        self.clear_btn = ctk.CTkButton(
            self.search_frame, text="🗑️ Clear", width=70, command=self.clear_favorites
        )
        self.clear_btn.grid(row=0, column=3, padx=5)

        # Favorites Dropdown
        self.recent_box = ctk.CTkComboBox(
            self.frame, values=[], width=250, command=self.load_city
        )
        self.recent_box.pack(pady=(5, 15))
        self.recent_box.set("Select a favorite city...")

        # Unit Toggle
        self.unit_btn = ctk.CTkButton(
            self.frame, text="Switch to °F", width=120, command=self.toggle_unit
        )
        self.unit_btn.pack(pady=10)

        # Weather Display
        self.city_label = ctk.CTkLabel(
            self.frame, text="", font=("Segoe UI", 24, "bold")
        )
        self.city_label.pack(pady=(10, 5))

        self.date_label = ctk.CTkLabel(self.frame, text="", font=("Segoe UI", 14))
        self.date_label.pack(pady=(0, 10))

        self.icon_label = ctk.CTkLabel(
            self.frame, text="🌎", font=("Segoe UI Emoji", 90)
        )
        self.icon_label.pack(pady=(10, 0))

        self.temp_label = ctk.CTkLabel(
            self.frame, text="", font=("Segoe UI", 48, "bold"), text_color="#00b4d8"
        )
        self.temp_label.pack(pady=(5, 0))

        self.desc_label = ctk.CTkLabel(self.frame, text="", font=("Segoe UI", 18))
        self.desc_label.pack(pady=(0, 20))

        self.details_label = ctk.CTkLabel(self.frame, text="", font=("Segoe UI", 14))
        self.details_label.pack()

        # Forecast Frame
        self.forecast_frame = ctk.CTkFrame(self.frame, corner_radius=15)
        self.forecast_frame.pack(pady=20, padx=20, fill="x")

        # Initial message
        self.show_initial_message()

    def show_initial_message(self):
        """Display initial welcome message"""
        self.city_label.configure(text="Welcome!")
        self.desc_label.configure(text="Enter a city to get started")
        self.details_label.configure(text="Search for any city worldwide\nto see live weather data")

    # ---------------------------- FAVORITES ----------------------------
    def save_favorite(self):
        """Save current city to favorites"""
        city = self.city_entry.get().strip()
        if not city:
            messagebox.showwarning("Warning", "Please enter a city name first.")
            return

        try:
            # Read existing data or create new
            if STORE.exists() and STORE.stat().st_size > 0:
                try:
                    data = json.loads(STORE.read_text())
                except json.JSONDecodeError:
                    data = {"favorites": []}
            else:
                data = {"favorites": []}

            # Add city if not already in favorites
            if city not in data["favorites"]:
                data["favorites"].append(city)
                STORE.write_text(json.dumps(data, indent=2))
                self.recent_box.configure(values=data["favorites"])
                messagebox.showinfo("Saved", f"✓ {city} added to favorites.")
            else:
                messagebox.showinfo("Info", f"{city} is already in favorites.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save favorite: {str(e)}")

    def load_city(self, city):
        """Load selected city from dropdown"""
        if city and city != "Select a favorite city...":
            self.city_entry.delete(0, "end")
            self.city_entry.insert(0, city)
            self.get_weather_async()

    def load_favorites(self):
        """Load saved favorites from file"""
        try:
            if STORE.exists() and STORE.stat().st_size > 0:
                try:
                    data = json.loads(STORE.read_text())
                    favorites = data.get("favorites", [])
                    if favorites:
                        self.recent_box.configure(values=favorites)
                except json.JSONDecodeError:
                    # Reset corrupted file
                    STORE.write_text(json.dumps({"favorites": []}, indent=2))
                    self.recent_box.configure(values=[])
        except Exception as e:
            print(f"Error loading favorites: {e}")

    def clear_favorites(self):
        """Clear all saved favorites"""
        result = messagebox.askyesno(
            "Confirm", "Are you sure you want to clear all favorites?"
        )
        if result:
            try:
                STORE.write_text(json.dumps({"favorites": []}, indent=2))
                self.recent_box.configure(values=[])
                self.recent_box.set("Select a favorite city...")
                messagebox.showinfo("Cleared", "All favorites removed.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear favorites: {str(e)}")

    # ---------------------------- ASYNC FETCH --------------------------
    def get_weather_async(self):
        """Start weather fetch in background thread"""
        threading.Thread(target=self.get_weather, daemon=True).start()

    # ---------------------------- FETCH WEATHER ------------------------
    def get_weather(self):
        """Fetch weather data from API"""
        city = self.city_entry.get().strip()
        if not city:
            messagebox.showwarning("Warning", "Please enter a city name.")
            return

        # Check API key
        if API_KEY == "YOUR_API_KEY_HERE":
            messagebox.showerror(
                "API Key Missing",
                "Please set your WeatherAPI.com API key!\n\n"
                "Get a free key at: https://www.weatherapi.com/signup.aspx\n\n"
                "Then set it as an environment variable:\n"
                "export WEATHER_API_KEY='your_key_here'"
            )
            return

        self.search_btn.configure(state="disabled", text="Loading...")

        try:
            params = {
                "key": API_KEY,
                "q": city,
                "days": 3,
                "aqi": "no",
                "alerts": "no"
            }
            response = requests.get(BASE_URL, params=params, timeout=10)
            data = response.json()

            if "error" in data:
                self.root.after(0, lambda: messagebox.showerror(
                    "Error", data["error"]["message"]
                ))
                return

            self.last_data = data
            self.root.after(0, self.update_display)

        except requests.exceptions.Timeout:
            self.root.after(0, lambda: messagebox.showerror(
                "Error", "Request timed out. Please try again."
            ))
        except requests.exceptions.ConnectionError:
            self.root.after(0, lambda: messagebox.showerror(
                "Error", "No internet connection. Please check your network."
            ))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(
                "Error", f"An error occurred: {str(e)}"
            ))
        finally:
            self.root.after(0, lambda: self.search_btn.configure(
                state="normal", text="Search 🔍"
            ))

    # ---------------------------- DISPLAY ------------------------------
    def update_display(self):
        """Update UI with weather data"""
        data = self.last_data
        loc = data["location"]
        cur = data["current"]
        forecast = data["forecast"]["forecastday"]

        # Update main display
        self.city_label.configure(text=f"{loc['name']}, {loc['country']}")
        self.date_label.configure(text=f"🕓 {loc['localtime']}")
        self.icon_label.configure(text=self.get_icon(cur["condition"]["text"]))

        # Temperature based on unit
        temp = cur["temp_c"] if self.unit == "C" else cur["temp_f"]
        feels = cur["feelslike_c"] if self.unit == "C" else cur["feelslike_f"]

        self.temp_label.configure(text=f"{temp}°{self.unit}")
        self.desc_label.configure(text=cur["condition"]["text"])
        self.details_label.configure(
            text=f"💧 Humidity: {cur['humidity']}%\n"
                 f"💨 Wind: {cur['wind_kph']} km/h\n"
                 f"🌡️ Feels like: {feels}°{self.unit}"
        )

        # Display forecast
        self.display_forecast(forecast)

    def display_forecast(self, days):
        """Display 3-day forecast"""
        # Clear existing forecast
        for widget in self.forecast_frame.winfo_children():
            widget.destroy()

        # Configure grid columns
        for i in range(len(days)):
            self.forecast_frame.grid_columnconfigure(i, weight=1)

        # Create forecast cards
        for i, day in enumerate(days):
            frame = ctk.CTkFrame(self.forecast_frame, corner_radius=10)
            frame.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")

            # Format date
            date = datetime.strptime(day["date"], "%Y-%m-%d").strftime("%a, %b %d")
            icon = self.get_icon(day["day"]["condition"]["text"])
            avg_temp = day["day"]["avgtemp_c"] if self.unit == "C" else day["day"]["avgtemp_f"]

            # Add labels
            ctk.CTkLabel(
                frame, text=date, font=("Segoe UI", 12, "bold")
            ).pack(pady=(10, 0))

            ctk.CTkLabel(
                frame, text=icon, font=("Segoe UI Emoji", 40)
            ).pack(pady=5)

            ctk.CTkLabel(
                frame, text=f"{avg_temp:.1f}°{self.unit}",
                font=("Segoe UI", 16, "bold")
            ).pack()

            ctk.CTkLabel(
                frame, text=day["day"]["condition"]["text"],
                font=("Segoe UI", 11)
            ).pack(pady=(0, 10))

    # ---------------------------- UTILITIES ----------------------------
    def get_icon(self, condition):
        """Get weather emoji based on condition"""
        text = condition.lower()
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
        """Toggle between Celsius and Fahrenheit"""
        self.unit = "F" if self.unit == "C" else "C"
        self.unit_btn.configure(
            text=f"Switch to °{'C' if self.unit == 'F' else 'F'}"
        )
        if self.last_data:
            self.update_display()


# ---------------------------- RUN APP --------------------------------
if __name__ == "__main__":
    root = ctk.CTk()
    app = WeatherApp(root)
    root.mainloop()

import os
import json
import pathlib
import threading
from datetime import datetime
from io import BytesIO

import requests
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk

# matplotlib (no seaborn; offscreen rendering)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------------------- CONFIG ---------------------------------
API_KEY = os.getenv("WEATHER_API_KEY", " YOUR_API_KEY")
BASE_URL = "https://api.weatherapi.com/v1/forecast.json"
STORE = pathlib.Path.home() / ".weather.json"

# ---------------------------- PERSISTENCE HELPERS --------------------
def _atomic_write(path: pathlib.Path, text: str):
    """Write text to a temp file then atomically replace target."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)

def _read_store() -> dict:
    """Read persisted store; auto-heal if missing/corrupt."""
    try:
        if STORE.exists() and STORE.stat().st_size > 0:
            return json.loads(STORE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {
        "favorites": [],
        "theme": "dark",
        "unit": "C",
        "last_city": "",
        "cache": {}
    }

def _write_store(data: dict):
    data.setdefault("favorites", [])
    data.setdefault("theme", "dark")
    data.setdefault("unit", "C")
    data.setdefault("last_city", "")
    data.setdefault("cache", {})
    _atomic_write(STORE, json.dumps(data, indent=2))

# ---------------------------- UTILITIES -------------------------------
def deg_to_compass(deg: float) -> str:
    """Convert wind degrees to compass direction."""
    dirs = ["N","NNE","NE","ENE","E","ESE","SE","SSE",
            "S","SSW","SW","WSW","W","WNW","NW","NNW"]
    return dirs[int((deg/22.5)+0.5) % 16]

# ---------------------------- APP CLASS -------------------------------
class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌤️ Weather App")
        self.root.geometry("720x1080")
        self.chart_photo = None
        self.last_data = None

        # Load persisted preferences
        self.store = _read_store()
        self.theme = self.store.get("theme", "dark")
        self.unit = self.store.get("unit", "C")
        self.last_city = self.store.get("last_city", "").strip()

        # Appearance
        ctk.set_appearance_mode(self.theme)
        ctk.set_default_color_theme("green")

        # Main Frame
        self.frame = ctk.CTkFrame(self.root, corner_radius=20)
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.create_ui()
        self.load_favorites()
        self.show_initial_message()

        # Auto-load last city if available
        if self.last_city:
            self.city_entry.insert(0, self.last_city)
            self.get_weather_async()

    # ---------------------------- UI SETUP ----------------------------
    def create_ui(self):
        # Title
        self.title = ctk.CTkLabel(
            self.frame, 
            text="🌤️ Live Weather Dashboard", 
            font=("Segoe UI", 26, "bold")
        )
        self.title.pack(pady=(16, 8))

        # Search Bar (centered)
        self.search_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.search_frame.pack(pady=8)

        self.city_entry = ctk.CTkEntry(
            self.search_frame, 
            width=400, 
            height=40,
            placeholder_text="Enter city name...",
            font=("Segoe UI", 14)
        )
        self.city_entry.grid(row=0, column=0, padx=8)
        self.city_entry.bind("<Return>", lambda e: self.get_weather_async())
        self.city_entry.bind("<KeyRelease>", lambda e: self._on_entry_change())

        self.search_btn = ctk.CTkButton(
            self.search_frame, 
            text="🔍 Search", 
            width=120,
            height=40,
            font=("Segoe UI", 13, "bold"),
            command=self.get_weather_async
        )
        self.search_btn.grid(row=0, column=1, padx=8)

        # Action Buttons Row (Save, Clear, Copy)
        self.action_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.action_frame.pack(pady=8)

        self.save_btn = ctk.CTkButton(
            self.action_frame, 
            text="⭐ Save Favorite", 
            width=140,
            command=self.save_favorite
        )
        self.save_btn.grid(row=0, column=0, padx=6)

        self.clear_btn = ctk.CTkButton(
            self.action_frame, 
            text="🗑️ Clear Favorites", 
            width=140,
            command=self.clear_favorites
        )
        self.clear_btn.grid(row=0, column=1, padx=6)

        self.copy_btn = ctk.CTkButton(
            self.action_frame, 
            text="📋 Copy Summary", 
            width=140,
            command=self.copy_summary
        )
        self.copy_btn.grid(row=0, column=2, padx=6)

        # Settings Row (Theme & Unit Toggle)
        self.settings_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.settings_frame.pack(pady=8)

        self.theme_btn = ctk.CTkButton(
            self.settings_frame, 
            text=f"🎨 Theme: {self.theme.title()}", 
            width=160,
            command=self.toggle_theme
        )
        self.theme_btn.grid(row=0, column=0, padx=8)

        self.unit_btn = ctk.CTkButton(
            self.settings_frame, 
            text=f"🌡️ Switch to °{'F' if self.unit=='C' else 'C'}", 
            width=160,
            command=self.toggle_unit
        )
        self.unit_btn.grid(row=0, column=1, padx=8)

        # Favorites Dropdown
        self.recent_box = ctk.CTkComboBox(
            self.frame, 
            values=[], 
            width=340,
            height=35,
            font=("Segoe UI", 12),
            command=self.load_city
        )
        self.recent_box.pack(pady=10)
        self.recent_box.set("📍 Select a favorite city...")

        # Divider
        ctk.CTkFrame(self.frame, height=2, fg_color="gray40").pack(fill="x", padx=40, pady=10)

        # Current Weather Block
        self.city_label = ctk.CTkLabel(
            self.frame, 
            text="", 
            font=("Segoe UI", 24, "bold")
        )
        self.city_label.pack(pady=(8, 4))

        self.date_label = ctk.CTkLabel(
            self.frame, 
            text="", 
            font=("Segoe UI", 14)
        )
        self.date_label.pack(pady=(0, 8))

        self.icon_label = ctk.CTkLabel(
            self.frame, 
            text="🌎", 
            font=("Segoe UI Emoji", 96)
        )
        self.icon_label.pack(pady=(6, 0))

        self.temp_label = ctk.CTkLabel(
            self.frame, 
            text="", 
            font=("Segoe UI", 52, "bold"), 
            text_color="#00b4d8"
        )
        self.temp_label.pack(pady=(4, 0))

        self.desc_label = ctk.CTkLabel(
            self.frame, 
            text="", 
            font=("Segoe UI", 18)
        )
        self.desc_label.pack(pady=(0, 6))

        self.details_label = ctk.CTkLabel(
            self.frame, 
            text="", 
            font=("Segoe UI", 14), 
            justify="center"
        )
        self.details_label.pack()

        # Astro info
        self.astro_label = ctk.CTkLabel(
            self.frame, 
            text="", 
            font=("Segoe UI", 13), 
            justify="center"
        )
        self.astro_label.pack(pady=(6, 6))

        # Hourly forecast title
        self.hourly_title = ctk.CTkLabel(
            self.frame, 
            text="📊 Next 12 Hours", 
            font=("Segoe UI", 16, "bold")
        )
        self.hourly_title.pack(pady=(14, 4))

        # Hourly grid
        self.hourly_frame = ctk.CTkFrame(self.frame, corner_radius=15)
        self.hourly_frame.pack(fill="x", padx=20)

        # Chart
        self.chart_label = ctk.CTkLabel(self.frame, text="")
        self.chart_label.pack(pady=(10, 4))

        # 3-Day forecast title
        self.forecast_title = ctk.CTkLabel(
            self.frame, 
            text="📅 3-Day Forecast", 
            font=("Segoe UI", 16, "bold")
        )
        self.forecast_title.pack(pady=(14, 4))

        # 3-Day forecast grid
        self.forecast_frame = ctk.CTkFrame(self.frame, corner_radius=15)
        self.forecast_frame.pack(pady=8, padx=20, fill="x")

        # Status line
        self.status = ctk.CTkLabel(
            self.frame, 
            text="", 
            font=("Segoe UI", 12),
            text_color="gray60"
        )
        self.status.pack(pady=(8, 0))

        self._on_entry_change()

    def show_initial_message(self):
        """Display welcome message"""
        self.city_label.configure(text="Welcome to Weather Dashboard!")
        self.desc_label.configure(text="Search any city to get live weather")
        self.details_label.configure(
            text="💾 Favorites saved locally\n"
                 "🎨 Theme & units remembered\n"
                 "📋 Copy weather summary with one click"
        )
        self.astro_label.configure(text="")

    # ---------------------------- FAVORITES / STORE --------------------
    def load_favorites(self):
        """Load favorites into dropdown"""
        favs = self.store.get("favorites", [])
        if favs:
            self.recent_box.configure(values=favs)

    def save_favorite(self):
        """Save current city to favorites"""
        city = self.city_entry.get().strip()
        if not city:
            messagebox.showwarning("Warning", "Please enter a city name first.")
            return
        
        favs = self.store.setdefault("favorites", [])
        if city not in favs:
            favs.append(city)
            _write_store(self.store)
            self.recent_box.configure(values=favs)
            self.status.configure(text=f"✓ {city} added to favorites")
            messagebox.showinfo("Saved", f"✓ {city} added to favorites.")
        else:
            messagebox.showinfo("Info", f"{city} is already in favorites.")

    def clear_favorites(self):
        """Clear all favorites with confirmation"""
        if messagebox.askyesno("Confirm", "Clear all saved favorites?"):
            self.store["favorites"] = []
            _write_store(self.store)
            self.recent_box.configure(values=[])
            self.recent_box.set("📍 Select a favorite city...")
            self.status.configure(text="All favorites cleared")
            messagebox.showinfo("Cleared", "All favorites removed.")

    def load_city(self, city):
        """Load weather for selected favorite city"""
        if city and not city.startswith("📍"):
            self.city_entry.delete(0, "end")
            self.city_entry.insert(0, city)
            self.get_weather_async()

    # ---------------------------- THEME / UNIT -------------------------
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        self.theme = "light" if self.theme == "dark" else "dark"
        self.store["theme"] = self.theme
        _write_store(self.store)
        ctk.set_appearance_mode(self.theme)
        self.theme_btn.configure(text=f"🎨 Theme: {self.theme.title()}")
        self.status.configure(text=f"Theme changed to {self.theme}")

    def toggle_unit(self):
        """Toggle between Celsius and Fahrenheit"""
        self.unit = "F" if self.unit == "C" else "C"
        self.store["unit"] = self.unit
        _write_store(self.store)
        self.unit_btn.configure(text=f"🌡️ Switch to °{'C' if self.unit == 'F' else 'F'}")
        if self.last_data:
            self.update_display()
            self.status.configure(text=f"Unit changed to °{self.unit}")

    # ---------------------------- ASYNC FETCH --------------------------
    def get_weather_async(self):
        """Start weather fetch in background thread"""
        threading.Thread(target=self.get_weather, daemon=True).start()

    # ---------------------------- FETCH WEATHER ------------------------
    def get_weather(self):
        """Fetch weather data from API"""
        city = self.city_entry.get().strip()
        if not city:
            self.root.after(0, lambda: messagebox.showwarning("Warning", "Please enter a city name."))
            return
        
        if API_KEY == "YOUR_API_KEY_HERE":
            self.root.after(0, lambda: messagebox.showerror(
                "API Key Missing",
                "Please set your WeatherAPI key!\n\n"
                "Get free key at: https://www.weatherapi.com/signup.aspx\n\n"
                "Set environment variable:\n"
                "Windows: setx WEATHER_API_KEY \"your_key\"\n"
                "Mac/Linux: export WEATHER_API_KEY=\"your_key\""
            ))
            return

        self.root.after(0, lambda: (
            self.search_btn.configure(state="disabled", text="Loading..."),
            self.status.configure(text="🔄 Fetching weather data...")
        ))

        try:
            params = {
                "key": API_KEY, 
                "q": city, 
                "days": 3, 
                "aqi": "no", 
                "alerts": "no"
            }
            resp = requests.get(BASE_URL, params=params, timeout=10)
            resp.raise_for_status()
            
            try:
                data = resp.json()
            except ValueError:
                self.root.after(0, lambda: messagebox.showerror(
                    "Error", "Unexpected response from weather service."
                ))
                return
            
            if "error" in data:
                self.root.after(0, lambda: messagebox.showerror(
                    "Error", data["error"]["message"]
                ))
                return

            self.last_data = data

            # Save to cache and update last_city
            self.last_city = city
            self.store["last_city"] = city
            cache = self.store.setdefault("cache", {})
            cache[city] = data
            _write_store(self.store)

            self.root.after(0, self.update_display)
            self.root.after(0, lambda: self.status.configure(text="✓ Weather updated successfully"))

        except requests.exceptions.Timeout:
            self.root.after(0, lambda: self._handle_offline(city, "Request timed out"))
        except requests.exceptions.HTTPError as e:
            code = e.response.status_code if e.response else "Unknown"
            self.root.after(0, lambda: self._handle_offline(city, f"HTTP error: {code}"))
        except requests.exceptions.ConnectionError:
            self.root.after(0, lambda: self._handle_offline(city, "No internet connection"))
        except Exception as e:
            self.root.after(0, lambda: self._handle_offline(city, str(e)))
        finally:
            self.root.after(0, lambda: self.search_btn.configure(
                state="normal", text="🔍 Search"
            ))

    def _handle_offline(self, city, error_msg):
        """Handle offline scenarios with cached data"""
        messagebox.showwarning("Connection Error", f"{error_msg}\n\nShowing cached data if available.")
        data = self.store.get("cache", {}).get(city)
        if data:
            self.last_data = data
            self.update_display()
            self.status.configure(text="⚠️ Offline — showing cached data")
        else:
            self.status.configure(text="⚠️ No cached data available")

    # ---------------------------- DISPLAY ------------------------------
    def update_display(self):
        """Update UI with weather data"""
        data = self.last_data
        loc = data["location"]
        cur = data["current"]
        days = data["forecast"]["forecastday"]

        # Header info
        self.city_label.configure(text=f"{loc['name']}, {loc['country']}")
        self.date_label.configure(text=f"🕓 {loc['localtime']}")
        self.icon_label.configure(text=self.get_icon(cur["condition"]["text"]))

        # Temperature and conditions
        temp = cur["temp_c"] if self.unit == "C" else cur["temp_f"]
        feels = cur["feelslike_c"] if self.unit == "C" else cur["feelslike_f"]
        wind = cur["wind_kph"] if self.unit == "C" else cur["wind_mph"]
        wind_unit = "km/h" if self.unit == "C" else "mph"
        wind_dir = deg_to_compass(cur.get("wind_degree", 0))

        self.temp_label.configure(text=f"{int(round(temp))}°{self.unit}")
        self.desc_label.configure(text=cur["condition"]["text"])
        self.details_label.configure(
            text=(
                f"💧 Humidity: {cur['humidity']}%\n"
                f"💨 Wind: {wind} {wind_unit} ({wind_dir})\n"
                f"🌡️ Feels like: {int(round(feels))}°{self.unit}"
            )
        )

        # Astro data
        astro = days[0].get("astro", {})
        sunrise = astro.get("sunrise", "--")
        sunset = astro.get("sunset", "--")
        self.astro_label.configure(
            text=f"🌅 Sunrise: {sunrise}   🌇 Sunset: {sunset}"
        )

        # Hourly forecast and chart
        self.display_hourly_and_chart(days, loc["localtime"])

        # 3-day forecast
        self.display_forecast(days)

    def display_hourly_and_chart(self, days, localtime_str):
        """Display hourly forecast grid and temperature chart"""
        # Clear existing
        for w in self.hourly_frame.winfo_children():
            w.destroy()

        # Collect hourly data
        hours = []
        for d in days[:2]:
            for hr in d["hour"]:
                hours.append({
                    "dt": datetime.strptime(hr["time"], "%Y-%m-%d %H:%M"),
                    "temp_c": hr["temp_c"],
                    "temp_f": hr["temp_f"],
                    "cond": hr["condition"]["text"],
                })

        now = datetime.strptime(localtime_str, "%Y-%m-%d %H:%M")
        future = [h for h in hours if h["dt"] >= now][:12] or hours[:12]

        # Display hourly cards
        for i, h in enumerate(future):
            frame = ctk.CTkFrame(self.hourly_frame, corner_radius=10)
            frame.grid(row=i // 6, column=i % 6, padx=8, pady=8, sticky="nsew")

            hour_txt = h["dt"].strftime("%I%p").lstrip("0")
            icon = self.get_icon(h["cond"])
            t = h["temp_c"] if self.unit == "C" else h["temp_f"]

            ctk.CTkLabel(frame, text=hour_txt, font=("Segoe UI", 12, "bold")).pack(pady=(8, 0))
            ctk.CTkLabel(frame, text=icon, font=("Segoe UI Emoji", 28)).pack(pady=2)
            ctk.CTkLabel(frame, text=f"{int(round(t))}°{self.unit}", font=("Segoe UI", 14, "bold")).pack(pady=(0, 8))

        # Create temperature chart
        times = [h["dt"].strftime("%I%p").lstrip("0") for h in future]
        temps = [h["temp_c"] if self.unit == "C" else h["temp_f"] for h in future]

        fig = plt.figure(figsize=(6.4, 2.2), dpi=120)
        ax = fig.add_subplot(111)
        ax.plot(range(len(temps)), temps, marker="o", linewidth=2, markersize=6, color="#00b4d8")
        ax.set_xticks(range(len(times)))
        ax.set_xticklabels(times, rotation=0, fontsize=8)
        ax.set_ylabel(f"Temperature (°{self.unit})", fontsize=9)
        ax.set_title("Hourly Temperature Trend", fontsize=11, fontweight="bold")
        ax.grid(True, alpha=0.3, linestyle="--")
        fig.tight_layout()

        buf = BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", facecolor="white")
        plt.close(fig)
        buf.seek(0)

        img = Image.open(buf)
        self.chart_photo = ImageTk.PhotoImage(img)
        self.chart_label.configure(image=self.chart_photo)

    def display_forecast(self, days):
        """Display 3-day forecast"""
        for w in self.forecast_frame.winfo_children():
            w.destroy()

        for i, d in enumerate(days):
            frame = ctk.CTkFrame(self.forecast_frame, corner_radius=10)
            frame.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            self.forecast_frame.grid_columnconfigure(i, weight=1)

            date = datetime.strptime(d["date"], "%Y-%m-%d").strftime("%a, %b %d")
            icon = self.get_icon(d["day"]["condition"]["text"])
            avg_temp = d["day"]["avgtemp_c"] if self.unit == "C" else d["day"]["avgtemp_f"]

            ctk.CTkLabel(frame, text=date, font=("Segoe UI", 12, "bold")).pack(pady=(10, 0))
            ctk.CTkLabel(frame, text=icon, font=("Segoe UI Emoji", 40)).pack(pady=4)
            ctk.CTkLabel(frame, text=f"{int(round(avg_temp))}°{self.unit}", font=("Segoe UI", 16, "bold")).pack()
            ctk.CTkLabel(frame, text=d["day"]["condition"]["text"], font=("Segoe UI", 11)).pack(pady=(0, 10))

    # ---------------------------- UTILITIES ----------------------------
    def get_icon(self, condition: str) -> str:
        """Get weather emoji based on condition"""
        t = condition.lower()
        if "sun" in t or "clear" in t:
            return "☀️"
        if "cloud" in t:
            return "☁️"
        if "rain" in t or "drizzle" in t:
            return "🌧️"
        if "snow" in t:
            return "❄️"
        if "storm" in t or "thunder" in t:
            return "⛈️"
        if "fog" in t or "mist" in t:
            return "🌫️"
        return "🌤️"

    def copy_summary(self):
        """Copy weather summary to clipboard"""
        if not self.last_data:
            messagebox.showinfo("Info", "No weather data to copy yet.")
            return
        
        loc = self.last_data["location"]
        cur = self.last_data["current"]
        city = f"{loc['name']}, {loc['country']}"
        temp = cur["temp_c"] if self.unit == "C" else cur["temp_f"]
        cond = cur["condition"]["text"]
        
        summary = f"Weather in {city}: {int(round(temp))}°{self.unit}, {cond}"
        
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(summary)
            self.status.configure(text="✓ Weather summary copied to clipboard")
            messagebox.showinfo("Copied", f"Copied to clipboard:\n\n{summary}")
        except Exception:
            messagebox.showinfo("Weather Summary", summary)

    def _on_entry_change(self):
        """Enable/disable save button based on text entry"""
        has_text = bool(self.city_entry.get().strip())
        self.save_btn.configure(state=("normal" if has_text else "disabled"))

# ---------------------------- RUN APP --------------------------------
if __name__ == "__main__":
    root = ctk.CTk()
    app = WeatherApp(root)
    root.mainloop()

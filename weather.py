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
API_KEY = os.getenv("WEATHER_API_KEY", " 85b6ccf0c2bc401ba6904238251710")
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
        self.root.title("Weather Dashboard")
        self.root.geometry("900x1100")
        self.chart_photo = None
        self.last_data = None

        # Load persisted preferences
        self.store = _read_store()
        self.theme = self.store.get("theme", "dark")
        self.unit = self.store.get("unit", "C")
        self.last_city = self.store.get("last_city", "").strip()

        # Appearance
        ctk.set_appearance_mode(self.theme)
        ctk.set_default_color_theme("blue")

        # Scrollable main frame
        self.scroll_frame = ctk.CTkScrollableFrame(self.root, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=0, pady=0)

        self.create_ui()
        self.load_favorites()
        self.show_initial_message()

        # Auto-load last city if available
        if self.last_city:
            self.city_entry.insert(0, self.last_city)
            self.get_weather_async()

    # ---------------------------- UI SETUP ----------------------------
    def create_ui(self):
        # Header with gradient effect
        header = ctk.CTkFrame(self.scroll_frame, height=180, corner_radius=0, 
                             fg_color=("#3b82f6", "#1e40af"))
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)

        # Title
        title = ctk.CTkLabel(header, text="Weather Dashboard", 
                            font=("Helvetica", 36, "bold"),
                            text_color="white")
        title.pack(pady=(30, 5))

        subtitle = ctk.CTkLabel(header, text="Real-time weather information worldwide", 
                               font=("Helvetica", 14),
                               text_color=("white", "#e0e7ff"))
        subtitle.pack()

        # Search card
        search_card = ctk.CTkFrame(self.scroll_frame, corner_radius=20, 
                                  fg_color=("#ffffff", "#1e293b"))
        search_card.pack(fill="x", padx=30, pady=(20, 15))

        search_inner = ctk.CTkFrame(search_card, fg_color="transparent")
        search_inner.pack(fill="x", padx=25, pady=20)

        # Search input
        search_label = ctk.CTkLabel(search_inner, text="Search Location", 
                                   font=("Helvetica", 14, "bold"))
        search_label.pack(anchor="w", pady=(0, 8))

        input_frame = ctk.CTkFrame(search_inner, fg_color="transparent")
        input_frame.pack(fill="x")

        self.city_entry = ctk.CTkEntry(input_frame, height=45, 
                                      placeholder_text="Enter city name...",
                                      font=("Helvetica", 14),
                                      border_width=2,
                                      corner_radius=10)
        self.city_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.city_entry.bind("<Return>", lambda e: self.get_weather_async())

        self.search_btn = ctk.CTkButton(input_frame, text="Search", 
                                       height=45, width=120,
                                       font=("Helvetica", 14, "bold"),
                                       corner_radius=10,
                                       command=self.get_weather_async)
        self.search_btn.pack(side="left")

        # Quick actions
        actions_frame = ctk.CTkFrame(search_card, fg_color="transparent")
        actions_frame.pack(fill="x", padx=25, pady=(0, 20))

        self.recent_box = ctk.CTkComboBox(actions_frame, height=35,
                                         font=("Helvetica", 12),
                                         corner_radius=8,
                                         command=self.load_city)
        self.recent_box.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.recent_box.set("Favorites")

        btn_style = {"height": 35, "width": 35, "corner_radius": 8, "text": ""}
        
        self.save_btn = ctk.CTkButton(actions_frame, **btn_style, 
                                     command=self.save_favorite)
        self.save_btn.pack(side="left", padx=2)
        ctk.CTkLabel(self.save_btn, text="⭐", font=("Helvetica", 18)).place(relx=0.5, rely=0.5, anchor="center")

        self.copy_btn = ctk.CTkButton(actions_frame, **btn_style,
                                     command=self.copy_summary)
        self.copy_btn.pack(side="left", padx=2)
        ctk.CTkLabel(self.copy_btn, text="📋", font=("Helvetica", 18)).place(relx=0.5, rely=0.5, anchor="center")

        self.clear_btn = ctk.CTkButton(actions_frame, **btn_style,
                                      command=self.clear_favorites)
        self.clear_btn.pack(side="left", padx=2)
        ctk.CTkLabel(self.clear_btn, text="🗑️", font=("Helvetica", 18)).place(relx=0.5, rely=0.5, anchor="center")

        # Settings row
        settings_frame = ctk.CTkFrame(search_card, fg_color="transparent")
        settings_frame.pack(fill="x", padx=25, pady=(0, 15))

        self.unit_btn = ctk.CTkSegmentedButton(settings_frame, 
                                               values=["°C", "°F"],
                                               command=self.unit_changed,
                                               corner_radius=8,
                                               height=32)
        self.unit_btn.set("°C" if self.unit == "C" else "°F")
        self.unit_btn.pack(side="left", padx=(0, 8))

        self.theme_btn = ctk.CTkSegmentedButton(settings_frame,
                                                values=["☀️ Light", "🌙 Dark"],
                                                command=self.theme_changed,
                                                corner_radius=8,
                                                height=32)
        self.theme_btn.set("🌙 Dark" if self.theme == "dark" else "☀️ Light")
        self.theme_btn.pack(side="left")

        # Main weather card (hero)
        self.weather_hero = ctk.CTkFrame(self.scroll_frame, corner_radius=20,
                                        fg_color=("#ffffff", "#1e293b"))
        self.weather_hero.pack(fill="x", padx=30, pady=15)

        self.hero_content = ctk.CTkFrame(self.weather_hero, fg_color="transparent")
        self.hero_content.pack(fill="both", expand=True, padx=30, pady=30)

        # City and date
        self.city_label = ctk.CTkLabel(self.hero_content, text="", 
                                      font=("Helvetica", 32, "bold"))
        self.city_label.pack(pady=(0, 5))

        self.date_label = ctk.CTkLabel(self.hero_content, text="",
                                      font=("Helvetica", 14),
                                      text_color="gray60")
        self.date_label.pack(pady=(0, 20))

        # Weather icon and temp
        main_display = ctk.CTkFrame(self.hero_content, fg_color="transparent")
        main_display.pack()

        self.icon_label = ctk.CTkLabel(main_display, text="🌍",
                                      font=("Helvetica", 100))
        self.icon_label.pack(side="left", padx=20)

        temp_frame = ctk.CTkFrame(main_display, fg_color="transparent")
        temp_frame.pack(side="left", padx=20)

        self.temp_label = ctk.CTkLabel(temp_frame, text="",
                                       font=("Helvetica", 72, "bold"),
                                       text_color=("#3b82f6", "#60a5fa"))
        self.temp_label.pack()

        self.desc_label = ctk.CTkLabel(temp_frame, text="",
                                       font=("Helvetica", 18))
        self.desc_label.pack()

        # Stats grid
        stats_grid = ctk.CTkFrame(self.hero_content, fg_color="transparent")
        stats_grid.pack(fill="x", pady=(25, 0))

        self.stat_cards = []
        for i in range(4):
            card = ctk.CTkFrame(stats_grid, corner_radius=12,
                               fg_color=("#f1f5f9", "#0f172a"),
                               height=80)
            card.grid(row=0, column=i, padx=8, pady=5, sticky="ew")
            stats_grid.grid_columnconfigure(i, weight=1)
            
            icon_label = ctk.CTkLabel(card, text="", font=("Helvetica", 24))
            icon_label.pack(pady=(10, 0))
            
            value_label = ctk.CTkLabel(card, text="", font=("Helvetica", 18, "bold"))
            value_label.pack()
            
            desc_label = ctk.CTkLabel(card, text="", font=("Helvetica", 11),
                                     text_color="gray60")
            desc_label.pack(pady=(0, 8))
            
            self.stat_cards.append((icon_label, value_label, desc_label))

        # Hourly forecast card
        hourly_card = ctk.CTkFrame(self.scroll_frame, corner_radius=20,
                                  fg_color=("#ffffff", "#1e293b"))
        hourly_card.pack(fill="x", padx=30, pady=15)

        ctk.CTkLabel(hourly_card, text="Hourly Forecast",
                    font=("Helvetica", 20, "bold")).pack(anchor="w", padx=25, pady=(20, 10))

        self.hourly_scroll = ctk.CTkScrollableFrame(hourly_card, height=160,
                                                    orientation="horizontal",
                                                    fg_color="transparent")
        self.hourly_scroll.pack(fill="x", padx=20, pady=(0, 20))

        # Chart card
        chart_card = ctk.CTkFrame(self.scroll_frame, corner_radius=20,
                                 fg_color=("#ffffff", "#1e293b"))
        chart_card.pack(fill="x", padx=30, pady=15)

        ctk.CTkLabel(chart_card, text="Temperature Trend",
                    font=("Helvetica", 20, "bold")).pack(anchor="w", padx=25, pady=(20, 10))

        self.chart_label = ctk.CTkLabel(chart_card, text="")
        self.chart_label.pack(padx=25, pady=(0, 20))

        # 3-day forecast card
        forecast_card = ctk.CTkFrame(self.scroll_frame, corner_radius=20,
                                    fg_color=("#ffffff", "#1e293b"))
        forecast_card.pack(fill="x", padx=30, pady=(15, 30))

        ctk.CTkLabel(forecast_card, text="3-Day Forecast",
                    font=("Helvetica", 20, "bold")).pack(anchor="w", padx=25, pady=(20, 10))

        self.forecast_frame = ctk.CTkFrame(forecast_card, fg_color="transparent")
        self.forecast_frame.pack(fill="x", padx=20, pady=(0, 20))

        # Status bar
        self.status = ctk.CTkLabel(self.scroll_frame, text="",
                                  font=("Helvetica", 11),
                                  text_color="gray60")
        self.status.pack(pady=(0, 20))

    def show_initial_message(self):
        """Display welcome message"""
        self.city_label.configure(text="Welcome!")
        self.date_label.configure(text="Search any city to begin")
        self.desc_label.configure(text="Real-time data")
        self.temp_label.configure(text="--°")

    # ---------------------------- FAVORITES / STORE --------------------
    def load_favorites(self):
        favs = self.store.get("favorites", [])
        if favs:
            self.recent_box.configure(values=favs)

    def save_favorite(self):
        city = self.city_entry.get().strip()
        if not city:
            return
        favs = self.store.setdefault("favorites", [])
        if city not in favs:
            favs.append(city)
            _write_store(self.store)
            self.recent_box.configure(values=favs)
            self.status.configure(text=f"✓ Saved {city}")

    def clear_favorites(self):
        if messagebox.askyesno("Confirm", "Clear all favorites?"):
            self.store["favorites"] = []
            _write_store(self.store)
            self.recent_box.configure(values=[])
            self.recent_box.set("Favorites")
            self.status.configure(text="Favorites cleared")

    def load_city(self, city):
        if city and city != "Favorites":
            self.city_entry.delete(0, "end")
            self.city_entry.insert(0, city)
            self.get_weather_async()

    # ---------------------------- THEME / UNIT -------------------------
    def theme_changed(self, value):
        self.theme = "dark" if "Dark" in value else "light"
        self.store["theme"] = self.theme
        _write_store(self.store)
        ctk.set_appearance_mode(self.theme)
        self.status.configure(text=f"Theme: {self.theme}")

    def unit_changed(self, value):
        self.unit = "C" if value == "°C" else "F"
        self.store["unit"] = self.unit
        _write_store(self.store)
        if self.last_data:
            self.update_display()

    # ---------------------------- ASYNC FETCH --------------------------
    def get_weather_async(self):
        threading.Thread(target=self.get_weather, daemon=True).start()

    # ---------------------------- FETCH WEATHER ------------------------
    def get_weather(self):
        city = self.city_entry.get().strip()
        if not city:
            return

        if not API_KEY:
            self.root.after(0, lambda: messagebox.showerror(
                "API Key Missing",
                "Get a free key at https://www.weatherapi.com/ and set:\n"
                "Windows (PowerShell):  setx WEATHER_API_KEY \"your_key\"\n"
                "macOS/Linux (bash/zsh): export WEATHER_API_KEY=\"your_key\""
            ))
            return

        # UI: loading state
        self.root.after(0, lambda: (self.search_btn.configure(state="disabled", text="Loading..."),
                                    self.status.configure(text="Fetching weather…")))
        try:
            params = {"key": API_KEY, "q": city, "days": 3, "aqi": "no", "alerts": "no"}
            resp = requests.get(BASE_URL, params=params, timeout=10)
            resp.raise_for_status()
            try:
                data = resp.json()
            except ValueError:
                self.root.after(0, lambda: messagebox.showerror("Error", "Unexpected response from the weather service."))
                return

            if "error" in data:
                self.root.after(0, lambda: messagebox.showerror("Error", data["error"]["message"]))
                return

            # Success
            self.last_data = data
            self.last_city = city
            self.store["last_city"] = city
            self.store.setdefault("cache", {})[city] = data
            _write_store(self.store)

            self.root.after(0, self.update_display)
            self.root.after(0, lambda: self.status.configure(text="Updated ✓"))

        except requests.exceptions.Timeout:
            self.root.after(0, lambda: (messagebox.showerror("Error", "Request timed out. Showing cached data if available."),
                                        self._handle_offline(city, "timeout")))
        except requests.exceptions.HTTPError as e:
            code = e.response.status_code if e.response else "HTTP"
            self.root.after(0, lambda: (messagebox.showerror("Error", f"HTTP error: {code}. Showing cached data if available."),
                                        self._handle_offline(city, f"http {code}")))
        except requests.exceptions.ConnectionError:
            self.root.after(0, lambda: (messagebox.showerror("Error", "No internet connection. Showing cached data if available."),
                                        self._handle_offline(city, "offline")))
        except Exception as e:
            self.root.after(0, lambda: (messagebox.showerror("Error", str(e)),
                                        self._handle_offline(city, "unknown error")))
        finally:
            self.root.after(0, lambda: self.search_btn.configure(state="normal", text="Search"))

    def _handle_offline(self, city, _reason):
        data = self.store.get("cache", {}).get(city)
        if data:
            self.last_data = data
            self.update_display()
            self.status.configure(text="⚠️ Showing cached data")
        else:
            self.status.configure(text="⚠️ No data available")

    # ---------------------------- DISPLAY ------------------------------
    def update_display(self):
        data = self.last_data
        loc = data["location"]
        cur = data["current"]
        days = data["forecast"]["forecastday"]

        self.city_label.configure(text=f"{loc['name']}, {loc['country']}")
        self.date_label.configure(text=f"{loc['localtime']}")
        self.icon_label.configure(text=self.get_icon(cur["condition"]["text"]))

        temp = cur["temp_c"] if self.unit == "C" else cur["temp_f"]
        feels = cur["feelslike_c"] if self.unit == "C" else cur["feelslike_f"]
        wind = cur["wind_kph"] if self.unit == "C" else cur["wind_mph"]
        wind_unit = "km/h" if self.unit == "C" else "mph"
        wind_dir = deg_to_compass(cur.get("wind_degree", 0))

        self.temp_label.configure(text=f"{int(round(temp))}°")
        self.desc_label.configure(text=cur["condition"]["text"].title())

        # Update stat cards (now includes wind direction)
        stats = [
            ("💧", f"{cur['humidity']}%", "Humidity"),
            ("💨", f"{wind} {wind_unit} ({wind_dir})", "Wind"),
            ("🌡️", f"{int(round(feels))}°", "Feels Like"),
            ("👁️", f"{cur.get('vis_km', 10)} km", "Visibility")
        ]
        for i, (icon, value, desc) in enumerate(stats):
            self.stat_cards[i][0].configure(text=icon)
            self.stat_cards[i][1].configure(text=value)
            self.stat_cards[i][2].configure(text=desc)

        self.display_hourly_and_chart(days, loc["localtime"])
        self.display_forecast(days)

    def display_hourly_and_chart(self, days, localtime_str):
        for w in self.hourly_scroll.winfo_children():
            w.destroy()

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

        for h in future:
            card = ctk.CTkFrame(self.hourly_scroll, corner_radius=12, width=90,
                               fg_color=("#f1f5f9", "#0f172a"))
            card.pack(side="left", padx=5)
            card.pack_propagate(False)

            hour = h["dt"].strftime("%I%p").lstrip("0")
            icon = self.get_icon(h["cond"])
            t = h["temp_c"] if self.unit == "C" else h["temp_f"]

            ctk.CTkLabel(card, text=hour, font=("Helvetica", 12, "bold")).pack(pady=(12, 4))
            ctk.CTkLabel(card, text=icon, font=("Helvetica", 32)).pack(pady=4)
            ctk.CTkLabel(card, text=f"{int(round(t))}°", font=("Helvetica", 16, "bold")).pack(pady=(4, 12))

        # Chart
        times = [h["dt"].strftime("%I%p").lstrip("0") for h in future]
        temps = [h["temp_c"] if self.unit == "C" else h["temp_f"] for h in future]

        fig = plt.figure(figsize=(8, 3), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(range(len(temps)), temps, marker="o", linewidth=3, markersize=8)
        ax.fill_between(range(len(temps)), temps, alpha=0.2)
        ax.set_xticks(range(len(times)))
        ax.set_xticklabels(times, fontsize=9)
        ax.set_ylabel(f"°{self.unit}", fontsize=10)
        ax.grid(True, alpha=0.2, linestyle="--")
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        fig.tight_layout()

        buf = BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", facecolor="white", transparent=True)
        plt.close(fig)
        buf.seek(0)

        img = Image.open(buf)
        self.chart_photo = ImageTk.PhotoImage(img)
        self.chart_label.configure(image=self.chart_photo)

    def display_forecast(self, days):
        for w in self.forecast_frame.winfo_children():
            w.destroy()

        for i, d in enumerate(days):
            card = ctk.CTkFrame(self.forecast_frame, corner_radius=15,
                               fg_color=("#f1f5f9", "#0f172a"))
            card.grid(row=0, column=i, padx=8, pady=5, sticky="ew")
            self.forecast_frame.grid_columnconfigure(i, weight=1)

            date = datetime.strptime(d["date"], "%Y-%m-%d").strftime("%a, %b %d")
            icon = self.get_icon(d["day"]["condition"]["text"])
            avg = d["day"]["avgtemp_c"] if self.unit == "C" else d["day"]["avgtemp_f"]
            max_t = d["day"]["maxtemp_c"] if self.unit == "C" else d["day"]["maxtemp_f"]
            min_t = d["day"]["mintemp_c"] if self.unit == "C" else d["day"]["mintemp_f"]

            ctk.CTkLabel(card, text=date, font=("Helvetica", 13, "bold")).pack(pady=(15, 5))
            ctk.CTkLabel(card, text=icon, font=("Helvetica", 48)).pack(pady=8)
            ctk.CTkLabel(card, text=f"{int(round(avg))}°", font=("Helvetica", 24, "bold")).pack()
            ctk.CTkLabel(card, text=f"H: {int(round(max_t))}°  L: {int(round(min_t))}°",
                        font=("Helvetica", 11), text_color="gray60").pack()
            ctk.CTkLabel(card, text=d["day"]["condition"]["text"],
                        font=("Helvetica", 11)).pack(pady=(5, 15))

    # ---------------------------- UTILITIES ----------------------------
    def get_icon(self, condition: str) -> str:
        t = condition.lower()
        if "sun" in t or "clear" in t: return "☀️"
        if "cloud" in t: return "☁️"
        if "rain" in t or "drizzle" in t: return "🌧️"
        if "snow" in t: return "❄️"
        if "storm" in t or "thunder" in t: return "⛈️"
        if "fog" in t or "mist" in t: return "🌫️"
        return "🌤️"

    def copy_summary(self):
        if not self.last_data:
            return
        loc = self.last_data["location"]
        cur = self.last_data["current"]
        temp = cur["temp_c"] if self.unit == "C" else cur["temp_f"]
        summary = f"{loc['name']}, {loc['country']}: {int(round(temp))}°{self.unit}, {cur['condition']['text']}"
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(summary)
            self.status.configure(text="✓ Copied to clipboard")
        except:
            pass

# ---------------------------- RUN APP --------------------------------
if __name__ == "__main__":
    root = ctk.CTk()
    app = WeatherApp(root)
    root.mainloop()

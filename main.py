import tkinter as tk
from tkinter import messagebox
import requests
from urllib.parse import urlencode

# ---------------- WEATHER FUNCTIONS ----------------

def get_weather():
    city = city_entry.get().strip()

    if not city:
        messagebox.showwarning("Input Required", "Please enter a city name.")
        return

    search_button.config(state="disabled", text="Searching...")
    status_label.config(text="Fetching weather data...")
    root.update_idletasks()

    try:
        # Step 1: Find the city coordinates
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo_params = {
            "name": city,
            "count": 10,
            "language": "en",
            "format": "json"
        }

        response = requests.get(
            geo_url, params=geo_params, timeout=15
        )
        response.raise_for_status()
        places = response.json().get("results", [])

        if not places:
            messagebox.showerror(
                "City Not Found",
                "No matching place found. Try another city name."
            )
            status_label.config(text="Location not found.")
            return

        # Use the first matching location
        place = places[0]
        latitude = place["latitude"]
        longitude = place["longitude"]

        # Step 2: Get current weather
        weather_url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": (
                "temperature_2m,relative_humidity_2m,"
                "apparent_temperature,is_day,precipitation,"
                "weather_code,wind_speed_10m"
            ),
            "timezone": "auto"
        }

        response = requests.get(
            weather_url, params=params, timeout=15
        )
        response.raise_for_status()
        data = response.json()

        current = data["current"]
        units = data["current_units"]

        # Weather code descriptions
        code = current["weather_code"]

        descriptions = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            56: "Light freezing drizzle",
            57: "Dense freezing drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            66: "Light freezing rain",
            67: "Heavy freezing rain",
            71: "Slight snow",
            73: "Moderate snow",
            75: "Heavy snow",
            77: "Snow grains",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Slight snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }

        description = descriptions.get(
            code, "Weather condition unavailable"
        )

        # Weather icon
        if code == 0:
            icon = "☀️" if current["is_day"] else "🌙"
        elif code in (1, 2):
            icon = "🌤️" if current["is_day"] else "☁️"
        elif code in (3, 45, 48):
            icon = "☁️"
        elif code in (51, 53, 55, 56, 57,
                      61, 63, 65, 66, 67, 80, 81, 82):
            icon = "🌧️"
        elif code in (71, 73, 75, 77, 85, 86):
            icon = "❄️"
        elif code in (95, 96, 99):
            icon = "⛈️"
        else:
            icon = "🌦️"

        # Display the results
        location = ", ".join(
            str(part) for part in (
                place.get("name"),
                place.get("admin1"),
                place.get("country")
            ) if part
        )

        location_label.config(text=location)
        icon_label.config(text=icon)
        temperature_label.config(
            text=f'{current["temperature_2m"]}'
                 f'{units["temperature_2m"]}'
        )
        description_label.config(text=description)

        feels_label.config(
            text=f'Feels like: {current["apparent_temperature"]}'
                 f'{units["apparent_temperature"]}'
        )
        humidity_label.config(
            text=f'Humidity: {current["relative_humidity_2m"]}'
                 f'{units["relative_humidity_2m"]}'
        )
        wind_label.config(
            text=f'Wind: {current["wind_speed_10m"]}'
                 f'{units["wind_speed_10m"]}'
        )
        rain_label.config(
            text=f'Precipitation: {current["precipitation"]}'
                 f'{units["precipitation"]}'
        )
        time_label.config(
            text=f'Local time: {current["time"].replace("T", " ")}'
        )
        status_label.config(text="Weather updated successfully.")

    except requests.exceptions.Timeout:
        messagebox.showerror(
            "Timeout", "The server took too long to respond."
        )
        status_label.config(text="Request timed out.")

    except requests.exceptions.ConnectionError:
        messagebox.showerror(
            "Connection Error",
            "Check your internet connection and try again."
        )
        status_label.config(text="Connection failed.")

    except (requests.exceptions.RequestException,
            KeyError, ValueError, TypeError) as error:
        messagebox.showerror(
            "Error", f"Could not retrieve weather data.\n{error}"
        )
        status_label.config(text="Unable to retrieve weather.")

    finally:
        search_button.config(state="normal", text="Search Weather")


# ---------------- GUI DESIGN ----------------

root = tk.Tk()
root.title("Santanu's Weather App")
root.geometry("440x650")
root.minsize(380, 600)
root.configure(bg="#101B2D")

title_label = tk.Label(
    root,
    text="WORLD WEATHER",
    font=("Arial", 22, "bold"),
    fg="white",
    bg="#101B2D"
)
title_label.pack(pady=(25, 5))

subtitle_label = tk.Label(
    root,
    text="Weather anywhere in the world",
    font=("Arial", 11),
    fg="#B8C7DF",
    bg="#101B2D"
)
subtitle_label.pack(pady=(0, 20))

city_entry = tk.Entry(
    root,
    font=("Arial", 14),
    justify="center",
    bg="#FFFFFF",
    fg="#17243B",
    relief="flat"
)
city_entry.pack(fill="x", padx=35, ipady=10)
city_entry.insert(0, "Kolkata")

search_button = tk.Button(
    root,
    text="Search Weather",
    font=("Arial", 12, "bold"),
    bg="#2D8CFF",
    fg="white",
    activebackground="#176BD1",
    activeforeground="white",
    relief="flat",
    cursor="hand2",
    command=get_weather
)
search_button.pack(fill="x", padx=35, pady=15, ipady=8)

location_label = tk.Label(
    root, text="Search for a location",
    font=("Arial", 15, "bold"),
    fg="white", bg="#101B2D",
    wraplength=370
)
location_label.pack(pady=(8, 0))

icon_label = tk.Label(
    root, text="🌤️",
    font=("Arial", 48),
    fg="white", bg="#101B2D"
)
icon_label.pack(pady=5)

temperature_label = tk.Label(
    root, text="-- °C",
    font=("Arial", 34, "bold"),
    fg="white", bg="#101B2D"
)
temperature_label.pack()

description_label = tk.Label(
    root, text="Current weather",
    font=("Arial", 15),
    fg="#B8C7DF", bg="#101B2D"
)
description_label.pack(pady=5)

details_frame = tk.Frame(root, bg="#1D2B44")
details_frame.pack(fill="x", padx=25, pady=15)

feels_label = tk.Label(
    details_frame, text="Feels like: --",
    font=("Arial", 11), fg="white",
    bg="#1D2B44", anchor="w"
)
feels_label.pack(fill="x", padx=15, pady=(12, 6))

humidity_label = tk.Label(
    details_frame, text="Humidity: --",
    font=("Arial", 11), fg="white",
    bg="#1D2B44", anchor="w"
)
humidity_label.pack(fill="x", padx=15, pady=6)

wind_label = tk.Label(
    details_frame, text="Wind: --",
    font=("Arial", 11), fg="white",
    bg="#1D2B44", anchor="w"
)
wind_label.pack(fill="x", padx=15, pady=6)

rain_label = tk.Label(
    details_frame, text="Precipitation: --",
    font=("Arial", 11), fg="white",
    bg="#1D2B44", anchor="w"
)
rain_label.pack(fill="x", padx=15, pady=6)

time_label = tk.Label(
    details_frame, text="Local time: --",
    font=("Arial", 10), fg="#B8C7DF",
    bg="#1D2B44", anchor="w"
)
time_label.pack(fill="x", padx=15, pady=(6, 12))

status_label = tk.Label(
    root, text="Ready to search",
    font=("Arial", 9),
    fg="#B8C7DF", bg="#101B2D"
)
status_label.pack(pady=5)

credit_label = tk.Label(
    root,
    text="Weather data by Open-Meteo.com",
    font=("Arial", 9),
    fg="#80B9FF",
    bg="#101B2D",
    cursor="hand2"
)
credit_label.pack(pady=(0, 10))

city_entry.bind("<Return>", lambda event: get_weather())

root.mainloop()
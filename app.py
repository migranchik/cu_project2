from flask import Flask, jsonify
import requests

app = Flask(__name__)


# Получение LocationKey по координатам
def get_location_key(lat, lon, api_key):
    url = "http://dataservice.accuweather.com/locations/v1/cities/geoposition/search"
    params = {"apikey": api_key, "q": f"{lat},{lon}"}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get("Key")
    else:
        return None


# получение текущих погодных условий
def get_weather(location_key, api_key):
    url = f"http://dataservice.accuweather.com/currentconditions/v1/{location_key}"
    params = {"apikey": api_key, "details": "true"}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()[0]  # берем первый объект из ответа
    else:
        return None


# извлечение параметров погоды
def extract_weather_data(weather_data):
    if not weather_data:
        return None
    extracted_data = {
        "temperature": weather_data.get("Temperature", {}).get("Metric", {}).get("Value"),
        "humidity": weather_data.get("RelativeHumidity"),
        "wind_speed": weather_data.get("Wind", {}).get("Speed", {}).get("Metric", {}).get("Value"),
        "rain_probability": weather_data.get("PrecipitationProbability", 0)
    }
    return extracted_data


# модель для оценки погодных условий
def check_bad_weather(temperature, wind_speed, precipitation_probability):
    """
    Определяет плохие погодные условия.

    Параметры:
    - temperature: Температура в градусах Цельсия.
    - wind_speed: Скорость ветра в км/ч.
    - precipitation_probability: Вероятность осадков в %.

    Возвращает:
    - "bad" если условия плохие, "good" если хорошие.
    """
    if temperature < 0 or temperature > 35:
        return "bad"
    if wind_speed > 50:
        return "bad"
    if precipitation_probability > 70:
        return "bad"
    return "good"


@app.route('/')
def home():
    return "Flask работает!"


# проверка работы
if __name__ == "__main__":
    latitude, longitude = 55.7558, 37.6173  # координаты мск
    api_key = "pgoSwlHSS8YfyTh6CJN3XhBSCWd6CmFq"

    # получение LocationKey
    location_key = get_location_key(latitude, longitude, api_key)
    if location_key:
        weather_data = get_weather(location_key, api_key)
        key_weather_params = extract_weather_data(weather_data)

        print("Ключевые параметры погоды:", key_weather_params)
    else:
        print("Не удалось получить LocationKey.")

    # тест модели
    test_cases = [
        {"temperature": -5, "wind_speed": 30, "precipitation_probability": 50},
        {"temperature": 20, "wind_speed": 60, "precipitation_probability": 20},
        {"temperature": 40, "wind_speed": 10, "precipitation_probability": 80},
        {"temperature": 25, "wind_speed": 20, "precipitation_probability": 30},
    ]

    for case in test_cases:
        result = check_bad_weather(
            case["temperature"], case["wind_speed"], case["precipitation_probability"]
        )
        print(f"Test case {case} -> Result: {result}")

    app.run(debug=True)




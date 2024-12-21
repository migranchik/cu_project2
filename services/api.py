import requests

API_KEY = "C5j86QLKuAXUt1L6QjCI6cXgZvy0QgNI"
BASE_URL = "http://dataservice.accuweather.com"


def get_location_key(city_name):
    """
    Получить Location Key для города.
    """
    try:
        url = f"{BASE_URL}/locations/v1/cities/search"
        params = {"apikey": API_KEY, "q": city_name}
        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        if len(data) > 0:
            return data[0]["Key"]
        else:
            raise ValueError(f"Город '{city_name}' не найден!")
    except requests.exceptions.RequestException as e:
        raise ConnectionError("Ошибка подключения к серверу.") from e


def get_weather_by_location_key(location_key):
    """
    Получить данные о погоде по Location Key.
    """
    try:
        url = f"{BASE_URL}/currentconditions/v1/{location_key}"
        params = {"apikey": API_KEY, "details": "true"}
        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        if len(data) > 0:
            return {
                "temperature": data[0]["Temperature"]["Metric"]["Value"],
                "wind_speed": data[0]["Wind"]["Speed"]["Metric"]["Value"],
                "precipitation_probability": data[0].get("PrecipitationProbability", 0),
            }
        else:
            raise ValueError("Данные о погоде не найдены!")
    except requests.exceptions.RequestException as e:
        raise ConnectionError("Ошибка подключения к серверу.") from e


def fetch_weather(start_city, end_city):
    """
    Получить данные о погоде для начального и конечного города.
    """
    start_key = get_location_key(start_city)
    end_key = get_location_key(end_city)

    start_weather = get_weather_by_location_key(start_key)
    end_weather = get_weather_by_location_key(end_key)

    return {
        "start": start_weather,
        "end": end_weather,
    }


def fetch_weather_extended(city_names, days):
    """
    Получить прогноз погоды для нескольких городов на заданное количество дней.

    :param city_names: Список городов.
    :param days: Количество дней (1, 3 или 5).
    :return: Словарь с данными о погоде.
    """
    forecasts = {}
    for city in city_names:
        location_key = get_location_key(city)
        url = f"{BASE_URL}/forecasts/v1/daily/{days}day/{location_key}"
        params = {"apikey": API_KEY, "details": "true", "metric": "true"}
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        print(data)
        forecasts[city] = [
            {
                "date": forecast.get("Date"),
                "temperature_max": forecast["Temperature"]["Maximum"].get("Value"),
                "temperature_min": forecast["Temperature"]["Minimum"].get("Value"),
                "wind_speed": forecast["Day"]["Wind"]["Speed"].get("Value", 0),  # Данные о ветре
                "precipitation_probability": forecast["Day"].get("PrecipitationProbability", 0)  # Вероятность осадков
            }
            for forecast in data.get("DailyForecasts", [])
        ]
    return forecasts



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

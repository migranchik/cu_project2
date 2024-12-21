from flask import Flask, render_template, request, jsonify
from services.api import fetch_weather_extended
from services.weather_model import check_bad_weather
from dash import Dash, html, dcc, Input, Output
import pandas as pd
import plotly.express as px


# Инициализация Flask
server = Flask(__name__)


# Глобальная переменная для хранения данных о погоде
weather_data_cache = {}


# Основная страница Flask
@server.route("/")
def index():
    return render_template("index.html")


@server.route("/check_route", methods=["POST"])
def check_route():
    global weather_data_cache

    # Получение данных из формы
    start = request.form.get("start")
    stops = request.form.get("stops").split(",") if request.form.get("stops") else []
    end = request.form.get("end")
    days = int(request.form.get("days"))

    try:
        # Все точки маршрута
        all_locations = [start] + stops + [end]

        # Получение данных о погоде для всех точек маршрута
        weather_data = fetch_weather_extended(all_locations, days)
        weather_data_cache = weather_data  # Кэширование для Dash
        print(weather_data_cache)
        # Проверка состояния погоды для каждой точки
        status = {
            city: check_bad_weather(
                data[0]["temperature_max"],
                data[0]["wind_speed"],
                data[0]["precipitation_probability"]
            )
            for city, data in weather_data.items()
        }

        return render_template(
            "result.html",
            weather_data=weather_data,
            status=status,
            locations=all_locations
        )
    except Exception as e:
        return render_template("error.html", error=f"Ошибка: {str(e)}")


# Инициализация Dash
app = Dash(__name__, server=server, url_base_pathname='/visualization/')


app.layout = html.Div([
    dcc.Store(id="weather-data-store"),  # Хранилище для данных
    html.H1("Погодные данные", style={"textAlign": "center"}),
    dcc.Dropdown(
        id="location-dropdown",
        placeholder="Выберите точку маршрута",
        style={"width": "50%", "margin": "auto"}
    ),
    dcc.Dropdown(
        id="parameter-dropdown",
        options=[
            {"label": "Максимальная температура", "value": "temperature_max"},
            {"label": "Минимальная температура", "value": "temperature_min"},
            {"label": "Скорость ветра", "value": "wind_speed"},
            {"label": "Вероятность осадков", "value": "precipitation_probability"}
        ],
        value="temperature_max",
        placeholder="Выберите параметр для отображения",
        style={"width": "50%", "margin": "auto"}
    ),
    dcc.Graph(id="weather-graph")
])


@server.route("/get_weather_data")
def get_weather_data():
    global weather_data_cache
    return jsonify(weather_data_cache)


@app.callback(
    Output("location-dropdown", "options"),
    Input("weather-data-store", "data")
)
def update_location_dropdown(data):
    if not data:
        return []
    return [{"label": city, "value": city} for city in data.keys()]


@app.callback(
    Output("weather-graph", "figure"),
    [Input("location-dropdown", "value"),
     Input("parameter-dropdown", "value")]
)
def update_graph(location, parameter):
    global weather_data_cache

    # Проверяем, есть ли данные
    if not weather_data_cache or location not in weather_data_cache:
        return px.line(title="Нет данных для отображения")

    # Создаём DataFrame для выбранного города
    df = pd.DataFrame(weather_data_cache[location])
    df["date"] = pd.to_datetime(df["date"])

    # Построение графика
    fig = px.line(
        df,
        x="date",
        y=parameter,
        title=f"{parameter.capitalize()} для {location}"
    )
    fig.update_layout(
        yaxis_title=parameter.capitalize(),
        xaxis_title="Дата",
        xaxis=dict(tickformat="%Y-%m-%d")
    )
    return fig



if __name__ == "__main__":
    server.run(debug=True)

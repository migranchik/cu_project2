from flask import Flask, render_template, request
from services.api import fetch_weather
from services.weather_model import check_bad_weather

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/check_route", methods=["POST"])
def check_route():
    start = request.form.get("start")
    end = request.form.get("end")

    try:
        # получение данных о погоде
        weather_data = fetch_weather(start, end)
        start_status = check_bad_weather(
            weather_data["start"]["temperature"],
            weather_data["start"]["wind_speed"],
            weather_data["start"]["precipitation_probability"]
        )
        end_status = check_bad_weather(
            weather_data["end"]["temperature"],
            weather_data["end"]["wind_speed"],
            weather_data["end"]["precipitation_probability"]
        )

        return render_template(
            "result.html",
            start=start,
            end=end,
            weather_data=weather_data,
            start_status=start_status,
            end_status=end_status
        )
    except ValueError as ve:
        return render_template("error.html", error=str(ve))
    except ConnectionError as ce:
        return render_template("error.html", error=str(ce))
    except Exception as e:
        return render_template("error.html", error="Произошла неизвестная ошибка.")


if __name__ == "__main__":
    app.run(debug=True)

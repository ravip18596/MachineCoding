from typing import Union
from fastapi import FastAPI
from sqlalchemy import text
from model import Weather
from main import main
from db import create_mysql_engine, fetch_weather_data, update_weather_db, delete_weather_row

app = FastAPI()
mysql_engine = create_mysql_engine()


@app.get("/")
async def health_check():
    return {"Hello": "World"}


@app.get("/weather/date/{date}")
async def fetch_weather(date: str, q: Union[str, None] = None):
    data = fetch_weather_data(mysql_engine, date)
    result = [Weather(**d) for d in data]
    return result


@app.post("/weather/update")
async def update_weather(weather: Weather):
    if weather.hour is None or weather.date is None:
        return {
            "error": "hour or date is empty or missing"
        }
    
    success = update_weather_db(weather.model_dump(), mysql_engine)
    result = "success" if success else "failure"
    return {
        "result": result
    }


@app.delete("/weather/date/{date}/hour/{hour}")
async def delete_weather(date: Union[str, None] = None, hour: Union[str, None] = None):
    if hour is None or date is None:
        return {
            "error": "hour or date is empty or missing"
        }
    
    success = delete_weather_row(date=date, hour=hour, engine=mysql_engine)
    result = "success" if success else "failure"
    return {
        "result": result
    }


@app.get("/weather/crawl")
async def crawl_weather():
    main()

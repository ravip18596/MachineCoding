from pydantic import BaseModel
from typing import Union


class Weather(BaseModel):
    hour: str 
    temp: Union[str, None]
    weather: Union[str, None]
    wind: Union[str, None]
    direction: Union[str, None]
    humidity: Union[str, None]
    barometer: Union[str, None]
    visibility: Union[str, None]
    date: str
from sqlalchemy import create_engine, text, Engine
import pandas as pd


def create_mysql_engine():
    engine = create_engine("mysql://ravi:password@localhost/algotest")
    return engine


    
def fetch_weather_data(engine: Engine, date: str) -> list:
    sql = text(f"select Temp,Weather,Wind,Direction,Humidity,Barometer,Visibility,date,hour from weather where date='{date}' order by hour")
    result = []
    with engine.connect() as conn:
        rows = conn.execute(sql)
        for row in rows:
            result.append({
                'temp': row[0] ,
                'weather': row[1],
                'wind': row[2],
                'direction': row[3],
                'humidity': row[4],
                'barometer': row[5],
                'visibility': row[6],
                'date': row[7],
                'hour': row[8]
            })
    return result


def upsert_weather(df: pd.DataFrame, engine: Engine):

    query = text("""INSERT INTO weather (hour,Temp,Weather,Wind,Direction,Humidity,Barometer,Visibility,date) 
                    VALUES(:hour, :temp, :weather, :wind, :direction, :humidity, :barometer, :visibility, :date) 
    ON DUPLICATE KEY UPDATE Temp=:temp,Weather=:weather,Wind=:wind,Direction=:direction,Humidity=:humidity,
                    Barometer=:barometer,Visibility=:visibility """)

    with engine.connect() as conn:
        for i in range(len(df)):
            params = {
                "hour": str(int(df.loc[i, "hour"])),
                "temp": str(df.loc[i, "Temp"]),
                "weather": str(df.Weather[i]),
                "wind": str(df.Wind[i]),
                "direction": str(df.Direction[i]),
                "humidity": str(df.Humidity[i]),
                "barometer": str(df.Barometer[i]),
                "visibility": str(df.Visibility[i]),
                "date": str(df.date[i])
            }
            conn.execute(statement=query, parameters=params)
            conn.commit()


def update_weather_db(data: dict, engine: Engine) -> bool:
    query = text(f"""update weather set Temp='{data['temp']}',Weather='{data['weather']}',Direction='{data['direction']}', Wind='{data['wind']}', Humidity='{data['humidity']}',Barometer='{data['barometer']}',Visibility='{data['visibility']}' where date='{data['date']}' and hour='{data['hour']}'; """)

    with engine.connect() as conn:
        try:
            conn.execute(query)
            conn.commit()
        except Exception as e:
            print(str(e))
            return False
      
    return True


def delete_weather_row(date: str, hour: str, engine: Engine) -> bool:
    query = text(""" delete from weather where date = :date and hour = :hour; """)
    params = {
        "date": date,
        "hour": hour
    }
    
    with engine.connect() as conn:
        try:
            conn.execute(statement=query, parameters=params)
            conn.commit()
        except Exception as e:
            print(str(e))
            return False

    return True
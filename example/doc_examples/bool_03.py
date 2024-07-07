import platitudes as pl


def weather(cloud_cover: float, is_rainy: bool, humidity: float, pressure: float = 1.0):
    print(f"The cloud cover is: {cloud_cover}%")
    print(f"Is it rainy: {is_rainy}")
    print(f"The humidity is: {humidity}%")
    print(f"The pressure is {pressure} atm")


pl.run(weather)

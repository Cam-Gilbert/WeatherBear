from weatherbear.data_fetcher import Data_Fetcher

def test_get_latlon():
    df = Data_Fetcher("28394")
    coords = df.get_latlon()
    if coords:
        print(f"Latitude: {coords[0]}, Longitude: {coords[1]}")
    else:
        print("Failed to get coordinates.")

#test_get_latlon()

def test_get_forecast_office():
    df = Data_Fetcher("Los Angeles")
    coords = df.get_latlon()
    if coords:
        print(f"Latitude: {coords[0]}, Longitude: {coords[1]}")
    else:
        print("Failed to get coordinates.")

    office = df.get_forecast_office(coords[0], coords[1])

    print(office)


#test_get_forecast_office()

def test_get_forecast():
    df = Data_Fetcher("Kansas City")
    forecast = df.get_forecast()

    print(forecast)
    return forecast


data = test_get_forecast()
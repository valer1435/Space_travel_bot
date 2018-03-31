import random

import requests

NASA_API_KEY = "AkGgBGq6bsssCbPSNwZX6u6xeCQl4JbrZfIXQlft"


def get_day_photo():
    try:
        NASA_api_server = "https://api.nasa.gov/planetary/apod"
        response = requests.get(NASA_api_server, params={
            "api_key": NASA_API_KEY,
        })

        if response:
            json_response = response.json()
            if "copyright" in json_response:
                cop = json_response["copyright"]
            else:
                cop = ""
            return (json_response["url"], json_response["explanation"], json_response["title"], cop)
        else:
            return (2, 2, 2, 2)
    except:
        return (1, 1, 1, 1)


def get_mars_picture():
    try:
        NASA_api_server = "https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos"
        response = requests.get(NASA_api_server, params={
            "api_key": NASA_API_KEY,
            "sol": str(random.choice(range(1, 2005)))
        })
        print(response.url)
        if response:
            json_response = response.json()
            photo = json_response["photos"][0]
            print(json_response["photos"][0])
            img = photo["img_src"]
            earth_date = photo["earth_date"]

            return (img, earth_date)
        else:
            return (0, 0)
    except:
        return (0, 0)
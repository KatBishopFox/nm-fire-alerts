import requests
from bs4 import BeautifulSoup

# Define the dictionary with forest names converted to lower case
NM_national_forests = {
    5430: ["santa fe", "pecos wilderness", "pecos", "chama river canyon", "chama river canyon wilderness", "san pedro parks wilderness", "san pedro parks"],
    5432: ["carson", "pecos wilderness", "columbine-hondo wilderness", "columbine-hondo", "wheeler peak wilderness", "wheeler peak", "latir peak wilderness", "latir peak", "pecos"],
    5434: ["gila"],
    5435: ["carson", "pecos wilderness", "columbine-hondo wilderness", "columbine-hondo", "wheeler peak wilderness", "wheeler peak", "latir peak wilderness", "latir peak", "pecos"],
    5436: ["cibola"],
    5439: ["lincoln"],
    5440: ["cibola"],
    5443: ["gila"],
    5444: ["carson", "pecos wilderness", "columbine-hondo wilderness", "columbine-hondo", "wheeler peak wilderness", "wheeler peak", "latir peak wilderness", "latir peak", "pecos"],
    5445: ["santa fe", "pecos wilderness", "chama river canyon", "chama river canyon wilderness", "san pedro parks wilderness", "san pedro parks"],
    5446: ["santa fe", "pecos wilderness", "pecos", "chama river canyon", "chama river canyon wilderness", "san pedro parks wilderness", "san pedro parks"],
    5447: ["lincoln"],
    5449: ["cibola"],
    5451: ["carson", "pecos wilderness", "pecos"],
    5453: ["carson", "pecos wilderness", "pecos", "cruces basin"],
    5454: ["kaibob"],
    5455: ["coronado"],
    5456: ["gila"],
    5458: ["gila"],
    5459: ["gila"],
    5460: ["cibola"],
    5462: ["coconino"],
    5463: ["lincoln"],
    5464: ["santa fe", "pecos wilderness", "pecos", "cruces basin", "chama river canyon", "chama river canyon wilderness", "san pedro parks wilderness", "san pedro parks"],
    5465: ["coconino"],
    5466: ["coronado", "pecos"],
    5467: ["coronado"],
    5468: ["cibola"],
    5473: ["gila"],
    5474: ["cibola"],
    5475: ["kaibob"],
    5476: ["santa fe", "pecos wilderness", "pecos", "cruces basin", "chama river canyon", "chama river canyon wilderness", "san pedro parks wilderness", "san pedro parks"],
    5477: ["kaibob"],
    5479: ["gila"],
}

# Parameters for the GET request
params = {
    "f": "pbf",
    "outFields": "Other_Info,PARKNAME,RestrictDateCurrent,RestrictSite,Restrict_Info,Stage,OBJECTID,GlobalID",
    "outSR": "102100",
    "returnGeometry": "false",
    "spatialRel": "esriSpatialRelIntersects",
    "where": "1=1"
}

# Base URL for fire restrictions information
base_url = "https://services3.arcgis.com/T4QMspbfLg3qTGWY/arcgis/rest/services/NPSBoundariesSWNonEditablePUBLICv2/FeatureServer/0/query"

# Base URL for fire weather information
fire_weather_url = "https://forecast.weather.gov/wwamap/wwatxtget.php?cwa=ABQ&wwa=fire%20weather%20watch"

def get_forest_ids(forest_name):
    forest_name = forest_name.lower()
    forest_ids = [key for key, values in NM_national_forests.items() if forest_name in [name.lower() for name in values]]
    return forest_ids

def check_fire_restrictions(forest_ids):
    fire_info_found = False
    for forest_id in forest_ids:
        params["objectIds"] = forest_id
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.content
            split_keyword = b"GlobalID\x10\x0b\x1a\x08GlobalID"
            if split_keyword in data:
                result = data.split(split_keyword, 1)[1]
                if b"Stage" in result or b"fire" in result:
                    print("There ARE fire restrictions for your destination.")
                    print(f"Response for forest ID {forest_id}: {result[:100]}...")
                    fire_info_found = True
            else:
                print(f"Keyword not found in the response for forest ID {forest_id}")
        else:
            print(f"Failed to get data for forest ID {forest_id}, status code: {response.status_code}")
    return fire_info_found

def get_fire_weather_info():
    fire_weather_response = requests.get(fire_weather_url)
    if fire_weather_response.status_code == 200:
               soup = BeautifulSoup(fire_weather_response.content, 'html.parser')
    pre_tags = soup.find_all('pre')
    for pre_tag in pre_tags:
        print(pre_tag.text.strip())
        print()

def main():
    forest_name = input("Enter the forest name: ")
    forest_ids = get_forest_ids(forest_name)
    if not forest_ids:
        print(f"No query found for forest name: {forest_name}. Visit https://nifc.maps.arcgis.com/apps/dashboards/aa9ff369dd414b74b69b696b40a1d057 and click on your destination to determine if any fire warnings exist.")
    else:
        fire_info_found = check_fire_restrictions(forest_ids)
        if not fire_info_found:
            print("It appears there are no fire restrictions for the forest you've indicated. To confirm, feel free to visit https://nifc.maps.arcgis.com/apps/dashboards/aa9ff369dd414b74b69b696b40a1d057.")
        input("Hit Enter to acknowledge the fire restriction information and inquire about fire weather alerts for the Albuquerque area.")
        get_fire_weather_info()

if __name__ == "__main__":
    main()


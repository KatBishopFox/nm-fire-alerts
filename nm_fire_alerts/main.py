import requests
from bs4 import BeautifulSoup

# Define the dictionary with forest names converted to lower case
NM_national_forests = {
    5430: [
        "santa fe",
        "pecos wilderness",
        "pecos",
        "chama river canyon",
        "chama river canyon wilderness",
        "san pedro parks wilderness",
        "san pedro parks",
    ],
    5432: [
        "carson",
        "pecos wilderness",
        "columbine-hondo wilderness",
        "columbine-hondo",
        "wheeler peak wilderness",
        "wheeler peak",
        "latir peak wilderness",
        "latir peak",
        "pecos",
    ],
    5434: ["gila"],
    5435: [
        "carson",
        "pecos wilderness",
        "columbine-hondo wilderness",
        "columbine-hondo",
        "wheeler peak wilderness",
        "wheeler peak",
        "latir peak wilderness",
        "latir peak",
        "pecos",
    ],
    5436: ["cibola"],
    5439: ["lincoln"],
    5440: ["cibola"],
    5443: ["gila"],
    5444: [
        "carson",
        "pecos wilderness",
        "columbine-hondo wilderness",
        "columbine-hondo",
        "wheeler peak wilderness",
        "wheeler peak",
        "latir peak wilderness",
        "latir peak",
        "pecos",
    ],
    5445: [
        "santa fe",
        "pecos wilderness",
        "chama river canyon",
        "chama river canyon wilderness",
        "san pedro parks wilderness",
        "san pedro parks",
    ],
    5446: [
        "santa fe",
        "pecos wilderness",
        "pecos",
        "chama river canyon",
        "chama river canyon wilderness",
        "san pedro parks wilderness",
        "san pedro parks",
    ],
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
    5464: [
        "santa fe",
        "pecos wilderness",
        "pecos",
        "cruces basin",
        "chama river canyon",
        "chama river canyon wilderness",
        "san pedro parks wilderness",
        "san pedro parks",
    ],
    5465: ["coconino"],
    5466: ["coronado", "pecos"],
    5467: ["coronado"],
    5468: ["cibola"],
    5473: ["gila"],
    5474: ["cibola"],
    5475: ["kaibob"],
    5476: [
        "santa fe",
        "pecos wilderness",
        "pecos",
        "cruces basin",
        "chama river canyon",
        "chama river canyon wilderness",
        "san pedro parks wilderness",
        "san pedro parks",
    ],
    5477: ["kaibob"],
    5479: ["gila"],
}

# Base URL for fire restrictions information
base_url = "https://services3.arcgis.com/T4QMspbfLg3qTGWY/arcgis/rest/services/NPSBoundariesSWNonEditablePUBLICv2/FeatureServer/0/query"

# Base URL for fire weather information
fire_weather_url = "https://forecast.weather.gov/wwamap/wwatxtget.php?cwa=ABQ&wwa=fire%20weather%20watch"


def get_forest_ids(forest_name: str) -> list:
    forest_name = forest_name.lower()
    forest_ids = [
        key
        for key, values in NM_national_forests.items()
        if forest_name in [name.lower() for name in values]
    ]
    return forest_ids


def fire_status_results(forest_id: int, response: requests.Response) -> str:
    """
    Parses the nasty protobuf awfulness and returns results
    if we have any.
    """
    # If we don't get a 200, flag the error and return early
    if response.status_code != 200:
        print(
            f"Failed to get data for forest ID {forest_id}, status code: {response.status_code}"
        )
        return ""
    data = response.content
    split_keyword = b"GlobalID\x10\x0b\x1a\x08GlobalID"
    # We don't have the keyword, return
    if split_keyword in data:
        results = data.split(split_keyword, 1)[1]
        # We have results! Return the first 100 characters of the string.
        if b"Stage" in results or b"fire" in results:
            return str(results[:100])
    return ""


def get_fire_status(forest_id: int):
    # Parameters for the GET request
    params = {
        "f": "pbf",
        "outFields": "Other_Info,PARKNAME,RestrictDateCurrent,RestrictSite,Restrict_Info,Stage,OBJECTID,GlobalID",
        "outSR": "102100",
        "returnGeometry": "false",
        "spatialRel": "esriSpatialRelIntersects",
        "where": "1=1",
        "objectIds": forest_id,
    }
    response = requests.get(base_url, params=params)
    return fire_status_results(forest_id, response)


def check_fire_restrictions(forest_ids: list) -> str:
    results = ""
    for forest_id in forest_ids:
        results = get_fire_status(forest_id)
        if results:
            return results
    return results


def get_fire_weather_info():
    fire_weather_response = requests.get(fire_weather_url)
    if fire_weather_response.status_code != 200:
        print("\nError retrieving fire weather advisories.")
        return
    soup = BeautifulSoup(fire_weather_response.content, "html.parser")
    pre_tags = soup.find_all("pre")
    if pre_tags:
        for pre_tag in pre_tags:
            print(pre_tag.text.strip())
            print()
    else:
        print(
            "\nThere are no fire weather advisories at https://forecast.weather.gov/wwamap/wwatxtget.php?cwa=ABQ&wwa=fire%20weather%20watch. Visit https://www.weather.gov/abq/ for relevant weather information."
        )


def main():
    forest_name = input("Enter the forest name: ")
    forest_ids = get_forest_ids(forest_name)
    if not forest_ids:
        print(
            f"\nNo query found for forest name: {forest_name}. Visit https://nifc.maps.arcgis.com/apps/dashboards/aa9ff369dd414b74b69b696b40a1d057 and click on your destination to determine if any fire warnings exist."
        )
    else:
        results = check_fire_restrictions(forest_ids)
        if results:
            print(
                "\nThere are fire restrictions in the area you selected. To confirm, feel free to visit https://nifc.maps.arcgis.com/apps/dashboards/aa9ff369dd414b74b69b696b40a1d057."
            )
        else:
            print(
                "\nIt appears there are no fire restrictions for the forest you've indicated. To confirm, feel free to visit https://nifc.maps.arcgis.com/apps/dashboards/aa9ff369dd414b74b69b696b40a1d057."
            )
        get_fire_weather_info()
        input(
            "\nHit Enter to acknowledge the fire weather information and close the script."
        )


if __name__ == "__main__":
    main()

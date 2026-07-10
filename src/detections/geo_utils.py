import requests
from math import radians, sin, cos, sqrt, atan2


def get_ip_location(ip_address):
    """
    Looks up the approximate real-world location of an IP address using a free
    public geolocation API (ip-api.com).

    Input: ip_address (string)
    Output: a dictionary with 'lat', 'lon', 'city', 'country' — or None if lookup fails
    """
    try:
        response = requests.get(f"http://ip-api.com/json/{ip_address}", timeout=5)
        data = response.json()

        if data.get("status") == "success":
            return {
                "lat": data["lat"],
                "lon": data["lon"],
                "city": data["city"],
                "country": data["country"]
            }
        else:
            return None
    except requests.RequestException:
        return None


def calculate_distance_km(lat1, lon1, lat2, lon2):
    """
    Calculates the distance in kilometers between two lat/lon points on Earth,
    using the Haversine formula (accounts for Earth's curvature).

    Input: latitude and longitude of two points
    Output: distance in kilometers (float)
    """
    R = 6371  # Earth's radius in kilometers

    lat1_rad, lon1_rad = radians(lat1), radians(lon1)
    lat2_rad, lon2_rad = radians(lat2), radians(lon2)

    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad

    a = sin(delta_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance
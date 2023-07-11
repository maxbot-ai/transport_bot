"""Openrouteservice client."""

import json
import logging

import openrouteservice
from openrouteservice import exceptions

logger = logging.getLogger(__name__)


class _RouteData:
    """Route data: stops and routes.

    Format (route-format):
        {
            "stops": {
                "<key>": {
                   "name": str,
                   "address": str,
                   "location": {
                       "lat": float,
                       "lon": float,
                   },
                ...
                }
            },
            "routes": {
                "<key>": {
                    "name": str,
                    "type": enum[trolleybus, bus, tram]
                    "stops": [
                        "<stop_key_1>",
                        "<stop_key_2>",
                        ....
                    ]
                }
            }
        }
    """

    def __init__(self):
        self._routes = None

    def load_from_json(self, path):
        """Load data from json file with route-format.

        :param str path: File path
        :raises Exception: on wrong stop data
        """
        with open(path, encoding="utf-8") as f:
            self._routes = json.load(f)
        for name, route in self._routes["routes"].items():
            for stop in route["stops"]:
                if stop not in self._routes["stops"]:
                    raise Exception(f'Stop "{stop}" for route "{name}" not defined')

    def __getitem__(self, name):
        return self._routes[name]


class _RouteClient:
    """Create route from driver to stop.

    See https://openrouteservice.org/ service for create route
    See https://github.com/GIScience/openrouteservice-py client library for openrouteservice
    """

    def __init__(self):
        self.client = None

    def set_config(self, open_route_service_key):
        """Set configuration.

        :param str open_route_service_key: See https://openrouteservice.org/dev/#/api-docs
        """
        self.client = openrouteservice.Client(key=open_route_service_key)

    def get_ors_route_info(
        self,
        from_latitude,
        from_longitude,
        to_latitude,
        to_longitude,
    ):
        """Get route summary: duration and distance.

        :param float from_latitude: driver latitude
        :param float from_longitude: driver longitude
        :param float to_latitude: stop latitude
        :param float to_longitude: stop longitude
        :return dict(duration=float, distance=float})
        """
        coords = (
            (from_longitude, from_latitude),
            (to_longitude, to_latitude),
        )
        data = None
        try:
            data = self.client.directions(coords)
        except exceptions.ApiError as e:
            logger.error("ORS ApiError: %s", e)
        except exceptions.Timeout as e:
            logger.error("ORS Timeout: %s", e)
        except exceptions.HTTPError as e:
            logger.error("ORS HTTPError: %s", e)

        # Skip if received any ORS error.
        if not data:
            return None
        summary = {
            "duration": round(data["routes"][0]["summary"].get("duration", 0) / 60),
            "distance": round(data["routes"][0]["summary"].get("distance", 0) / 1000, 2),
        }
        return summary


route_data = _RouteData()
route_client = _RouteClient()

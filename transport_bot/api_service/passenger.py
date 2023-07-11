"""Passenger http api."""

import haversine
from webargs import fields

from transport_bot.api_service import query
from transport_bot.api_service.common import resp, use_body
from transport_bot.api_service.route import route_client, route_data
from transport_bot.api_service.schema import app

MAX_RADIUS = 4


@app.route("/passenger/get_routes", methods=["POST"])
@use_body({"start_command": fields.String(required=True)})
def get_route(body):
    """Get routes by stop key.

    :param dict body: With key "start_command"
    :return Flask.Response: status=200 and json with format dict(error) or
                            dict(routes, stop) with stop detail and relevant routes
    """
    tokens = body["start_command"].split(" ", 1)
    if tokens[0] != "/start" or len(tokens) != 2:
        return resp(data={"error": "Request format error"})
    stop = tokens[1].strip()
    if stop not in route_data["stops"]:
        return resp(data={"error": "Unknown stop"})
    stop_info = _get_stop_info(stop)
    routes = sorted(list(stop_info["routes"].values()), key=lambda d: d["key"])
    return resp(data={"routes": routes, "stop": stop_info["stop"]})


@app.route("/passenger/get_nearest_driver", methods=["POST"])
@use_body({"stop": fields.String(required=True), "route": fields.String(required=True)})
def get_nearest_driver(body):
    """Get nearest driver.

    :param dict body: With keys "stop" and "route"
    :return Flask.Response: status=200 and json with format dict(name, distance, duration)
    """
    if body["stop"] not in route_data["stops"]:
        return resp(data={"error": "Unknown stop"})
    if body["route"] not in route_data["routes"]:
        return resp(data={"error": "Unknown route"})
    stop_info = _get_stop_info(body["stop"])
    if body["route"] not in stop_info["routes"]:
        return resp(data={"error": "No stop for route"})
    drivers = query.find_drivers_on_routes(routes=[body["route"]])
    if not drivers:
        return resp()
    stop_loc = stop_info["stop"]["location"]
    results = []
    for driver in drivers:
        distance = haversine.haversine(
            (driver.latitude, driver.longitude), (stop_loc["lat"], stop_loc["lon"])
        )
        if distance > MAX_RADIUS:
            continue
        summary = route_client.get_ors_route_info(
            driver.latitude, driver.longitude, stop_loc["lat"], stop_loc["lon"]
        )
        if not summary or summary["distance"] > MAX_RADIUS:
            continue

        # Compute reverse route and skip if this distance less
        summary_revert = route_client.get_ors_route_info(
            stop_loc["lat"], stop_loc["lon"], driver.latitude, driver.longitude
        )
        if summary_revert and summary["distance"] > summary_revert["distance"]:
            continue
        results.append((summary["distance"], summary, driver.name))
    if results:
        _, nearest_summary, driver_name = list(sorted(results))[0]
        nearest_summary["name"] = driver_name
        return resp(data=nearest_summary)
    return resp()


def _get_stop_info(stop):
    stop_data = route_data["stops"][stop]
    stop_data = dict(**stop_data, **{"key": stop})
    routes = {}
    for route, data in route_data["routes"].items():
        if stop in data["stops"]:
            routes[route] = {"name": data["name"], "key": route}
    result = {"stop": stop_data, "routes": routes}
    return result

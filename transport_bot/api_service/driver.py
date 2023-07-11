"""Driver http api."""

import haversine
from flask import abort
from webargs import fields, validate

from transport_bot.api_service import query
from transport_bot.api_service.common import conflict, resp, use_body
from transport_bot.api_service.route import route_data
from transport_bot.api_service.schema import app, db


class RouteValidate(validate.Validator):
    """Route validator."""

    def __call__(self, route):
        """Route validate."""
        if route in route_data["routes"]:
            return True
        raise validate.ValidationError(message=f"No route: {route}")


def lock_driver(messenger_id):
    """Db locked driver."""
    driver = query.find_driver(messenger_id, for_update=True)
    if not driver:
        abort(404, f"No found driver {messenger_id}")
    return driver


@app.route("/driver/get_routes", methods=["POST"])
@use_body(
    {
        "latitude": fields.Float(required=True, validate=[validate.Range(min=-90, max=90)]),
        "longitude": fields.Float(required=True, validate=[validate.Range(min=-180, max=180)]),
    }
)
def get_routes(body):
    """Get routes sorted by location.

    :param dict body: Contains latitude and longitude
    :return Flask.Response: status=200
    """
    result = []
    driver_location = (body["latitude"], body["longitude"])
    for key, data in route_data["routes"].items():
        min_distance = 0

        for stop_key in data["stops"]:
            stop_location = route_data["stops"][stop_key]["location"]
            stop_location = (stop_location["lat"], stop_location["lon"])
            distance = haversine.haversine(driver_location, stop_location)
            if min_distance == 0 or min_distance > distance:
                min_distance = distance
        result.append((min_distance, key, data))
    data = [{"key": r[1], "name": r[2]["name"]} for r in sorted(result)]
    return resp(data=data)


@app.route("/driver/<int:messenger_id>", methods=["GET"])
def get_driver(messenger_id):
    """Get driver.

    :param int messenger_id: Passenger telegram messenger_id
    :return Flask.Response: status=200 and json data with driver details
    """
    driver = query.find_driver(messenger_id, for_update=False)
    if driver:
        result = resp(
            data={
                "messenger_id": driver.messenger_id,
                "phone": driver.phone,
                "name": driver.name,
                "latitude": driver.latitude,
                "longitude": driver.longitude,
                "route": driver.route,
                "state": driver.state,
                "last_update": driver.last_update,
            }
        )
    else:
        result = resp()
    return result


@app.route("/driver/<int:messenger_id>", methods=["POST"])
@use_body(
    {
        "phone": fields.Str(required=True),
        "name": fields.Str(required=True),
        "latitude": fields.Float(required=True, validate=[validate.Range(min=-90, max=90)]),
        "longitude": fields.Float(required=True, validate=[validate.Range(min=-180, max=180)]),
        "route": fields.Str(required=True, validate=[RouteValidate()]),
    }
)
def post_driver(body, messenger_id):
    """Add new driver.

    :param dict body: Contains phone, name, latitude and longitude
    :param int messenger_id: driver identifier in telegram
    :return Flask.Response: status=200 on success,
                            status=409 on duplicate
    """
    driver = query.find_driver(messenger_id, for_update=False)
    if driver:
        if body["phone"] != driver.phone:
            return conflict("Duplicate phone")
        query.update_driver_location(messenger_id, body["latitude"], body["longitude"])
        query.update_driver_route(messenger_id, body["route"])
    else:
        query.add_driver(
            messenger_id,
            body["phone"],
            body["name"],
            body["latitude"],
            body["longitude"],
            body["route"],
        )
    db.session.commit()
    return resp()


@app.route("/driver/<int:messenger_id>/location", methods=["PUT"])
@use_body(
    {
        "latitude": fields.Float(required=True, validate=[validate.Range(min=-90, max=90)]),
        "longitude": fields.Float(required=True, validate=[validate.Range(min=-180, max=180)]),
    }
)
def put_driver_location(body, messenger_id):
    """Update driver location.

    :param dict body: Contains latitude and longitude
    :param int messenger_id: driver identifier in telegram
    :return Flask.Response: status=200 on success,
                            status=404 on not found
    """
    lock_driver(messenger_id)
    query.update_driver_location(messenger_id, body["latitude"], body["longitude"])
    db.session.commit()
    return resp()


@app.route("/driver/<int:messenger_id>/start", methods=["POST"])
def post_driver_start(messenger_id):
    """Update driver state on connected.

    :param int messenger_id: driver identifier in telegram
    :return Flask.Response: status=200 on success,
                            status=404 on not found
    """
    lock_driver(messenger_id)
    query.update_driver_state(messenger_id, state="connected")
    db.session.commit()
    return resp()


@app.route("/driver/<int:messenger_id>/stop", methods=["POST"])
def post_driver_stop(messenger_id):
    """Update driver state on disabled.

    :param int messenger_id: driver identifier in telegram
    :return Flask.Response: status=200 on success,
                            status=404 on not found
    """
    lock_driver(messenger_id)
    query.update_driver_state(messenger_id, state="disabled")
    db.session.commit()
    return resp()

import json
import logging
import random
import string
import time

import httpretty
import pytest

from transport_bot.api_service import driver, passenger
from transport_bot.api_service.route import route_client, route_data
from transport_bot.api_service.schema import app, db

DRIVER_BOT_URL = "http://driver.bot"
ORS_KEY = "ORS_KEY"
ORS_URL = "https://api.openrouteservice.org/v2/directions/driving-car/json"
ORS_BODY = {
    "routes": [
        {
            "summary": {"distance": 2755.2, "duration": 295.9},
            "geometry": "iovlJwfcxDqDyLCKq@yBC[AWFGPWt@aAz@gAFI`@i@PSLQzAmBNO`ByBX]EOCIAMKc@o@sAiAyBACi@eA_@w@KQgA}BGK}A{CMYMYe@{@aAoBk@kAg@aAKS{@iBUc@wAqCOYUa@}@gBAEi@cAg@eACGi@eAo@sAOIWAe@C[Ac@Cy@C[A]AM?w@GOEEAMC[OSGSA]E]Cc@EE?MAMAQ?UAq@A_@C{ACiACu@CyAGOAQEkEGU?U?UAsAEo@AaACy@CyAEkCG[AcACc@AWA[Ao@CoBGc@AyACI?uAE]??j@?b@?dB?`B?F?`A?rA",
        }
    ]
}

route_client.set_config(ORS_KEY)


logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def rand_phone_number():
    return "".join(random.choices(string.digits, k=10))


def rand_messenger_id():
    return str(random.randint(1000000, 10000000000))


@pytest.fixture
def client():
    route_data.load_from_json("./tests/routes.json")
    random.seed()
    with app.app_context():
        db.drop_all()
        db.create_all()
    return app.test_client()


def test_passenger(client):
    resp = client.post("/passenger/get_routes", json={"start_command": "/start hard_rock_cafe"})
    assert resp.status_code == 200
    print(resp.json)
    assert resp.json["routes"] == [
        {"key": "23", "name": "Bus №23"},
        {"key": "9", "name": "Bus №9"},
    ]
    assert resp.json["stop"] == {
        "address": "London W1J 7PX, United Kingdom",
        "key": "hard_rock_cafe",
        "location": {"lat": 51.504251036813, "lon": -0.14841997129390494},
        "name": "Old Park Lane Hard Rock Cafe",
    }
    resp = client.post("/passenger/get_routes", json={"start_command": "/start stop unknown"})
    assert resp.json["error"] == "Unknown stop"

    resp = client.post("/passenger/get_routes", json={"start_command": "/start portman_square"})
    assert resp.status_code == 200
    assert resp.json["routes"] == [{"key": "13", "name": "Bus №13"}]
    resp = client.post(
        "/passenger/get_nearest_driver", json={"stop": "portman_square", "route": "9"}
    )
    assert resp.status_code == 200
    assert resp.json["error"] == "No stop for route"

    resp = client.post("/passenger/get_nearest_driver", json={"stop": "unknown", "route": "17"})
    assert resp.status_code == 200
    assert resp.json["error"] == "Unknown stop"
    resp = client.post(
        "/passenger/get_nearest_driver",
        json={"stop": "portman_square", "route": "unknown"},
    )
    assert resp.status_code == 200
    assert resp.json["error"] == "Unknown route"

    resp = client.post(
        "/passenger/get_nearest_driver", json={"stop": "portman_square", "route": "13"}
    )
    assert resp.status_code == 200
    assert resp.json == {}


@httpretty.activate(allow_net_connect=False)
def test_driver(client):
    messenger_id = random.randint(1000000, 10000000000)
    phone = rand_phone_number()
    resp = client.get(f"/driver/{messenger_id}")
    assert resp.status_code == 200 and not resp.json
    data = {
        "phone": phone,
        "latitude": 1.1,
        "longitude": 1.1,
        "route": "9",
        "name": "NAME",
    }
    resp = client.post(f"/driver/{messenger_id}", json=data)
    assert resp.status_code == 200
    resp = client.get(f"/driver/{messenger_id}")
    assert resp.status_code == 200
    data = dict(resp.json)
    del data["last_update"]
    last_update = resp.json["last_update"]
    assert data == {
        "messenger_id": messenger_id,
        "phone": phone,
        "name": "NAME",
        "latitude": 1.1,
        "longitude": 1.1,
        "route": "9",
        "state": "disabled",
    }
    data["route"] = "unknown"
    resp = client.post(f"/driver/{messenger_id}", json=data)
    assert resp.status_code == 400
    time.sleep(1)
    data = {"latitude": 1.2, "longitude": 1.3}
    resp = client.put(f"/driver/{messenger_id}/location", json=data)
    assert resp.status_code == 200
    resp = client.get(f"/driver/{messenger_id}")
    assert resp.status_code == 200 and last_update < resp.json["last_update"]
    assert resp.json["latitude"] == 1.2 and resp.json["longitude"] == 1.3

    data = {
        "route": "unknown",
        "phone": phone,
        "name": "NNN",
        "latitude": 1,
        "longitude": 1,
    }
    resp = client.post(f"/driver/{messenger_id}", json=data)
    assert resp.status_code == 400
    data["route"] = "13"
    data["phone"] = rand_phone_number()
    resp = client.post(f"/driver/{messenger_id}", json=data)
    assert resp.status_code == 409
    data["phone"] = phone
    resp = client.post(f"/driver/{messenger_id}", json=data)
    assert resp.status_code == 200
    resp = client.get(f"/driver/{messenger_id}")
    assert resp.json["route"] == "13"

    assert client.post(f"/driver/{messenger_id}/start").status_code == 200
    assert client.get(f"/driver/{messenger_id}").json["state"] == "connected"
    assert client.post(f"/driver/{messenger_id}/start").status_code == 200
    assert client.get(f"/driver/{messenger_id}").json["state"] == "connected"
    assert client.post(f"/driver/{messenger_id}/stop").status_code == 200
    assert client.get(f"/driver/{messenger_id}").json["state"] == "disabled"
    assert client.post(f"/driver/{messenger_id}/stop").status_code == 200
    assert client.get(f"/driver/{messenger_id}").json["state"] == "disabled"
    assert client.post(f"/driver/{messenger_id}/start").status_code == 200
    assert client.get(f"/driver/{messenger_id}").json["state"] == "connected"
    location = {"latitude": 59.921005, "longitude": 30.339205}
    resp = client.post(f"/driver/get_routes", json=location)
    assert resp.status_code == 200
    assert resp.json == [
        {"key": "23", "name": "Bus №23"},
        {"key": "9", "name": "Bus №9"},
        {"key": "13", "name": "Bus №13"},
    ]
    data = {"latitude": 51.5271883782117, "longitude": -0.164119441314896}
    resp = client.put(f"/driver/{messenger_id}/location", json=data)
    assert resp.status_code == 200

    httpretty.register_uri(
        httpretty.POST,
        f"{ORS_URL}",
        body=json.dumps(ORS_BODY),
    )
    resp = client.post(
        "/passenger/get_nearest_driver",
        json={"stop": "alpha_close", "route": "13"},
    )
    assert resp.status_code == 200
    assert resp.json == {"distance": 2.76, "duration": 5, "name": "NAME"}


def test_inline():
    inline_keyboard = {
        "row": [
            {
                "button": [
                    {"caption": "Button-1", "callback_data": "data-1"},
                    {"caption": "Button-2", "callback_data": "data-2"},
                ]
            },
            {"button": [{"caption": "Button-3", "callback_data": "data-3"}]},
        ],
        "text": "Choice route for view nearest driver",
    }
    command = {"inline_keyboard": inline_keyboard}
    from transport_bot.channel.telegram_impl import _create_reply_markup

    reply_markup = _create_reply_markup(command)

    def create(data):
        print("<inline_keyboard>")
        i = 1
        print("  <row>")
        for route in data:
            print("     <button>", route["name"], "</button>")
            if i % 2 == 0:
                print("  </row>")
                print("  <row>")
            i = i + 1
        print("  </row>")
        print("</inline_keyboard>")

    routes = [{"name": "Button-1"}]
    create(routes)
    routes = [{"name": "Button-1"}, {"name": "Button-2"}]
    create(routes)
    routes = [{"name": "Button-1"}, {"name": "Button-2"}, {"name": "Button-3"}]
    create(routes)
    routes = [
        {"name": "Button-1"},
        {"name": "Button-2"},
        {"name": "Button-3"},
        {"name": "Button-4"},
    ]
    create(routes)

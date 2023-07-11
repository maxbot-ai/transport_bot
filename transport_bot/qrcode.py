"""QR code generator."""

import os

import click
import qrcode

from .api_service.route import route_data

OUTPUT_PATH = "qr_codes"


@click.command()
@click.option(
    "--passenger-bot-name",
    "passenger_bot_name",
    type=str,
    required=True,
    help="Passenger bot name",
)
@click.option(
    "--routes-data-json",
    "routes_data_json",
    type=str,
    required=True,
    help="Routes data json",
)
def main(passenger_bot_name, routes_data_json):
    """Run qr code generator."""
    route_data.load_from_json(routes_data_json)
    if not os.path.exists(OUTPUT_PATH):
        os.mkdir(OUTPUT_PATH)
    with open(f"{OUTPUT_PATH}/deeplink.txt", "w", encoding="utf-8") as f:
        for stop, _ in route_data["stops"].items():
            deeplink = f"https://t.me/{passenger_bot_name}?start={stop}"
            image = qrcode.make(deeplink)
            image.save(f"{OUTPUT_PATH}/{stop}.png")
            f.write(f"{deeplink}\n")

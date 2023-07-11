"""Server runner."""

import logging

import click
import click_config_file

from .api_service import driver, passenger, schema  # noqa: F401, pylint: disable=unused-import
from .api_service.route import route_client, route_data

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


@click.command()
@click.option("--bind-port", "bind_port", type=int, required=True, help="Bind port")
@click.option("--routes-json", "routes_json", type=str, required=True, help="Routes json")
@click.option("--ors-token", "ors_token", type=str, required=True, help="ORS token")
@click_config_file.configuration_option()
def main(bind_port, routes_json, ors_token):
    """Run transport bot server applications.

    Provides command to run transport bot
    """
    route_client.set_config(ors_token)
    route_data.load_from_json(routes_json)
    with schema.app.app_context():
        schema.db.create_all()
        schema.app.run(port=bind_port)

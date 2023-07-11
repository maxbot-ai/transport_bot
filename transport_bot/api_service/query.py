"""DB queries."""

from sqlalchemy import select, update

from transport_bot.api_service.schema import DriverTable, db


def find_driver(messenger_id, for_update):
    """Select driver by messenger_id."""
    stmt = select(DriverTable).where(DriverTable.messenger_id == messenger_id)
    if for_update:
        stmt = stmt.with_for_update()
    return db.session.scalars(stmt).one_or_none()


def add_driver(messenger_id, phone, name, latitude, longitude, route):
    """Add new driver."""
    driver = DriverTable(
        messenger_id=messenger_id,
        phone=phone,
        name=name,
        latitude=latitude,
        longitude=longitude,
        route=route,
        state="disabled",
    )
    db.session.add(driver)


def update_driver_location(messenger_id, latitude, longitude):
    """Update driver location."""
    stmt = (
        update(DriverTable)
        .where(DriverTable.messenger_id == messenger_id)
        .values(latitude=latitude, longitude=longitude)
    )
    db.session.execute(stmt)


def update_driver_route(messenger_id, route):
    """Update driver route."""
    stmt = update(DriverTable).where(DriverTable.messenger_id == messenger_id).values(route=route)
    db.session.execute(stmt)


def find_drivers_on_routes(routes):
    """Select all connected drivers on routes."""
    stmt = (
        select(DriverTable)
        .where(DriverTable.state == "connected")
        .where(DriverTable.route.in_(routes))
    )
    return db.session.scalars(stmt).all()


def update_driver_state(messenger_id, state):
    """Update driver state."""
    stmt = update(DriverTable).where(DriverTable.messenger_id == messenger_id).values(state=state)
    db.session.execute(stmt)

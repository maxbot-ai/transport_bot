"""Schemas for extension."""

from marshmallow import Schema, fields, validate


class LocationMessage(Schema):
    """A point on the map received from the user."""

    # Longitude as defined by receiver
    longitude = fields.Float(required=True)

    # Latitude as defined by receiver
    latitude = fields.Float(required=True)

    # Live_period as defined by receiver
    live_period = fields.Integer()


class LocationCommand(Schema):
    """A point on the map to send to the user."""

    # Longitude as defined by sender
    longitude = fields.Float(required=True)

    # Latitude as defined by sender
    latitude = fields.Float(required=True)

    # The radius of uncertainty for the location, measured in meters
    horizontal_accuracy = fields.Float(validate=validate.Range(0, 1500))


class KeyboardButtonCommand(Schema):
    """A single button to send to the user."""

    # Text message with button by sender
    text = fields.String(required=True)

    # Button title by sender
    title = fields.String(required=True)


class KeyboardButtonListCommand(Schema):
    """A button list to send to the user."""

    # Text message with buttons by sender
    text = fields.String(required=True)

    # Button titles by sender
    buttons = fields.List(fields.String)


class ContactMessage(Schema):
    """A contact message received from the user."""

    # Contact phone number as defined by receiver
    phone_number = fields.String(required=True)

    # Contact name as defined by receiver
    first_name = fields.String(required=True)

    # Contact last_name as defined by receiver
    last_name = fields.String()


class CallbackQueryMessage(Schema):
    """A callback query message received from the user."""

    # Data as defined by receiver
    data = fields.String(required=True)


class InlineButton(Schema):
    """A inline button from InlineKeyboardCommand."""

    # Caption as defined by sender
    caption = fields.String(required=True)

    # Callback query data as defined by sender
    callback_data = fields.String(required=True)


class Row(Schema):
    """A row from InlineButton."""

    # Button as defined by sender
    button = fields.Nested(InlineButton, many=True)


class InlineKeyboardCommand(Schema):
    """A inline button command send to the user."""

    # Caption as defined by sender
    text = fields.String(required=True)

    # Row as defined by sender
    row = fields.Nested(Row, many=True)

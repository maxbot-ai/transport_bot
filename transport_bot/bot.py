"""Bot runner."""
from maxbot import MaxBot

from transport_bot.channel import schemas, telegram_impl


def add_driver_telegram_mixin(builder):
    """Add telegram channel mixins for driver bot.

    send location command example:
        response: |-
          <location latitude="40.7580" longitude="-73.9855" horizontal_accuracy="100"/>

    receive location example:
      - condition: message.location
        response: |-
          latitude={{ message.location.latitude }}°
          longitude={{ message.location.longitude }}°
          live_period={{ message.location.live_period }} sec.

    send keyboard_button_location example:
        response: |-
          <keyboard_button_location text="Submit your location." title="My location" />

    send keyboard_button_list example:
        response: |-
            <keyboard_button_list text="Choice variants.">
              <buttons>Variants-1</buttons>
              <buttons>Variants-2</buttons>
            </keyboard_button_list>

    receive contact example:
      - condition: message.contact
        response: |-
          name={{ message.contact.name }}
          phone_number={{ message.contact.phone_number }}

    send keyboard_button_contact example:
       response: |-
         <keyboard_button_contact text="Submit your contact." title="My phone"/>

    send inline_keyboard example:
       response: |-
         <inline_keyboard text="Title: {{ slots.pattern }}." limit="10" >
            <row>
              <button caption="caption-1-1" callback_data="data-1-1" />
              <button caption="caption-1-2" callback_data="data-1-2" />
            </row>
            <row>
              <button caption="caption-2-1" callback_data="data-2-" />
            </row>
         </inline_keyboard>

    receive callback_query (click on inline button) example:
      - condition:message.callback_query
        label: name
        response: |-
          data={{ message.callback_query.data }}
    """
    builder.add_message(schemas.LocationMessage, "location")
    builder.add_command(schemas.LocationCommand, "location")
    builder.add_channel_mixin(telegram_impl.LocationExtension, "telegram")

    builder.add_command(schemas.KeyboardButtonCommand, "keyboard_button_location")
    builder.add_channel_mixin(telegram_impl.KeyboardButtonLocationExtension, "telegram")

    builder.add_command(schemas.KeyboardButtonListCommand, "keyboard_button_list")
    builder.add_channel_mixin(telegram_impl.KeyboardButtonListExtension, "telegram")

    builder.add_message(schemas.ContactMessage, "contact")
    builder.add_channel_mixin(telegram_impl.ContactExtension, "telegram")

    builder.add_command(schemas.KeyboardButtonCommand, "keyboard_button_contact")
    builder.add_channel_mixin(telegram_impl.KeyboardButtonContactExtension, "telegram")

    builder.add_command(schemas.InlineKeyboardCommand, "inline_keyboard")
    builder.add_channel_mixin(telegram_impl.InlineKeyboardExtension, "telegram")

    builder.add_message(schemas.CallbackQueryMessage, "callback_query")
    builder.add_channel_mixin(telegram_impl.CallbackQueryExtension, "telegram")


def add_passenger_telegram_mixin(builder):
    """Add telegram channel mixins for passenger bot."""
    builder.add_command(schemas.InlineKeyboardCommand, "inline_keyboard")
    builder.add_channel_mixin(telegram_impl.InlineKeyboardExtension, "telegram")

    builder.add_message(schemas.CallbackQueryMessage, "callback_query")
    builder.add_channel_mixin(telegram_impl.CallbackQueryExtension, "telegram")


passenger_builder = MaxBot.builder()
add_passenger_telegram_mixin(passenger_builder)
passenger_builder.use_package_resources(__name__, botfile="passenger.yaml")
passenger = passenger_builder.build()

driver_builder = MaxBot.builder()
add_driver_telegram_mixin(driver_builder)
driver_builder.use_package_resources(__name__, botfile="driver.yaml")
driver = driver_builder.build()

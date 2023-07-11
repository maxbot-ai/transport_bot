"""Implementation of telegram channel extensions."""

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


class KeyboardButtonListExtension:
    """Extension for send of button list."""

    async def send_keyboard_button_list(self, command: dict, dialog: dict):
        """Send button list command, :class:`KeyboardButtonListCommand`.

        See https://core.telegram.org/bots/api#replykeyboardmarkup
        See https://core.telegram.org/bots/api#keyboardbutton

        :param dict command: A command with the payload :attr:`KeyboardButtonListCommand`.
        :param dict dialog: A dialog we respond in, with the schema :class:`~maxbot.schemas.DialogSchema`.
        """
        keyboard = [[KeyboardButton(text)] for text in command["keyboard_button_list"]["buttons"]]
        await self.bot.send_message(
            dialog["user_id"],
            text=command["keyboard_button_list"]["text"],
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
        )


class LocationExtension:
    """Extension for send and receive location message with live period."""

    async def receive_location(self, update):
        """Receive :class:`LocationMessage`.

        See https://core.telegram.org/bots/api#location for more information.

        :param Update update: An incoming update.
        :return dict: A message with the payload :class:`~LocationMessage`.
        """
        message = update.message or update.edited_message
        if message:
            if message.location:
                result = {
                    "longitude": message.location.longitude,
                    "latitude": message.location.latitude,
                }
                if message.location.live_period:
                    result["live_period"] = message.location.live_period
                return {"location": result}

    async def send_location(self, command: dict, dialog: dict):
        """Send :class:`LocationCommand`.

        See https://core.telegram.org/bots/api#sendlocation for more information.

        :param dict command: A command with the payload :attr:`~LocationCommand`.
        :param dict dialog: A dialog we respond in, with the schema :class:`~maxbot.schemas.DialogSchema`.
        """
        await self.bot.send_location(
            dialog["user_id"],
            latitude=command["location"]["latitude"],
            longitude=command["location"]["longitude"],
            horizontal_accuracy=command["location"]["horizontal_accuracy"],
        )


class KeyboardButtonLocationExtension:
    """Extension for send of share-location button."""

    async def send_keyboard_button_location(self, command: dict, dialog: dict):
        """Send share-location button command, :class:`KeyboardButtonCommand`.

        See https://core.telegram.org/bots/api#sendmessage.
        See https://core.telegram.org/bots/api#keyboardbutton, param request_location

        :param dict command: A command with the payload :attr:`KeyboardButtonCommand`.
        :param dict dialog: A dialog we respond in, with the schema :class:`~maxbot.schemas.DialogSchema`.
        """
        keyboard = [
            [KeyboardButton(command["keyboard_button_location"]["title"], request_location=True)]
        ]
        await self.bot.send_message(
            dialog["user_id"],
            text=command["keyboard_button_location"]["text"],
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
        )


class KeyboardButtonContactExtension:
    """Extension for send of contact-location button."""

    async def send_keyboard_button_contact(self, command: dict, dialog: dict):
        """Send share-contact button command, :class:`KeyboardButtonCommand`.

        See https://core.telegram.org/bots/api#keyboardbutton, param request_contact

        :param dict command: A command with the payload :attr:`KeyboardButtonCommand`.
        :param dict dialog: A dialog we respond in, with the schema :class:`~maxbot.schemas.DialogSchema`.
        """
        keyboard = [
            [KeyboardButton(command["keyboard_button_contact"]["title"], request_contact=True)]
        ]
        await self.bot.send_message(
            dialog["user_id"],
            text=command["keyboard_button_contact"]["text"],
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
        )


class ContactExtension:
    """Extension for send and receive contact message."""

    async def receive_contact(self, update):
        """Receive contact data message, :class:`ContactMessage`.

        See https://core.telegram.org/bots/api#contact for more information.

        :param Update update: An incoming update.
        :return dict: A message with the payload :class:`~ContactMessage`.
        """
        if update.message and update.message.contact:
            contact = {
                "phone_number": update.message.contact.phone_number,
                "first_name": update.message.contact.first_name,
            }
            if update.message.contact.last_name:
                contact["last_name"] = update.message.contact.last_name
            return {"contact": contact}


def _create_reply_markup(command):
    keyboard = []
    for rows in command["inline_keyboard"]["row"]:
        if not rows:
            continue
        line = []
        for button in rows["button"]:
            line.append(
                InlineKeyboardButton(button["caption"], callback_data=button["callback_data"])
            )
        keyboard.append(line)
    return InlineKeyboardMarkup(keyboard)


class InlineKeyboardExtension:
    """Extension for send inline keyboard buttons."""

    async def send_inline_keyboard(self, command: dict, dialog: dict):
        """Send inline keyboard command, :class:`InlineKeyboardCommand`.

        See https://core.telegram.org/bots/features#inline-keyboards
        See https://core.telegram.org/bots/api#inlinekeyboardmarkup
        See https://core.telegram.org/bots/api#inlinekeyboardbutton

        :param dict command: A command with the payload :attr:`InlineKeyboardCommand`.
        :param dict dialog: A dialog we respond in, with the schema :class:`~maxbot.schemas.DialogSchema`.
        """
        reply_markup = _create_reply_markup(command)
        await self.bot.send_message(
            dialog["user_id"],
            text=command["inline_keyboard"]["text"],
            reply_markup=reply_markup,
        )


class CallbackQueryExtension:
    """Extension for receiving inline keyboard button callback query data."""

    async def receive_callback_query(self, update):
        """Receive callback query data message, :class:`CallbackQueryMessage`.

        See https://core.telegram.org/bots/api#callbackquery for more information.

        :param Update update: An incoming update.
        :return dict: A message with the payload :class:`~CallbackQueryMessage`.
        """
        if update.callback_query:
            return {"callback_query": {"data": update.callback_query.data}}

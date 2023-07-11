# Transport Bot

This is an example of public transport information system implemented on [Maxbot](https://github.com/maxbot-ai/maxbot) framework. A passenger at the stop can find out what routes go through it and when the next bus, trolleybus or tram will arrive. To do this, passenger scanns the QR code at this stop, and goes to the bot, which gives him all the information. Each driver uses bot to choose the route and inform the service of current location.

The example consists of two bots and an external service:

- `DriverBot` — bot for drivers,
- `PassengerBot` — bot for passengers,
- `Server` — external service.

### `DriverBot`:

- registers a driver by requesting a phone number,
- requests the current coordinates of the driver,
- displays a list of all routes ordered by driver distance,
- provides a choice of route to work,
- updates the driver’s coordinates using the ```telegram live location``` function,
- starts/ends of the trip along the route.
### `PassengerBot`:

- displays the list of routes passing through the stop, when you go to the chat using a QR code,
- searches the nearest driver on the selected route and displays the distance to him and the time to arrive at the stop.

### `Server`:

- stores data about drivers in the database: phone number, location, selected route, status (active or inactive),
- stores data about stops and routes,
- searches for the nearest driver using the service [openrouteservice.org](https://openrouteservice.org/).


**Note** Service does not verify that the driver:
- has left the route, his location is not on his route,
- does not send location for a long time, for example when the live-locations function expires.


**Note** The `QRCodeGenerator` is used to generate QR code images.
- it creates QR codes with deeplink,
- this images are attached at the stops, each stop has its own QR code,
- passenger puts the phone camera on the QR code, goes to the passenger bot that informs what routes passes through this stop,
- passenger selects the route, then bot informs him when the nearest driver will arrive.

# Requirements
Before you start, you should make sure that the system has:

* Python 3.9 - 3.11,
* Git,
* [Poetry](https://python-poetry.org/),
* [Pagekite](https://pagekite.net/downloads),
    We recommend to just download pagekite.py and use it as a separate scenario.
    ```bash
    curl -O https://pagekite.net/pk/pagekite.py
    ```
It's also required:
* To register and receive a token for the [Routing Service](https://openrouteservice.org/),
* To create two bots in `Telegram`: driver’s chat and passenger's chat: see BotFather and [instruction](https://core.telegram.org/bots/tutorial).

**Note** You'll need a smartphone with `Telegram` apps to work properly with `DriverBot`. Desktop versions of `Telegram` do not fit, as they don't allow you to send the location.

# Install

Clone this repository and change current directory
```bash
git clone https://github.com/maxbot-ai/transport_bot
cd transport_bot
```

Install the package with dependencies
```bash
poetry shell
poetry install
```

# Configuring the application

* Route settings are stored in a JSON file, an example is in ``tests/routes.json``.
* Settings for `Server` are stored in the file ``./transport_bot.conf``.
* Environment settings are stored in the file `.env`.

## The format of the JSON file with routes:
```json
{
    "stops": {
        "<stop_key:string>": {
            "name": "<string>",
            "address": "<string>",
            "location": {
               "lat": "<float>",
               "lon": "<float>"
            }
        },
        ...
    },
    "routes": {
        "<route_key:string>": {
            "name": "<string>",
            "type": "<enum[bus, tram, trolleybus]>",
            "stops": [
                "<stop_key_1:string>",
                "<stop_key_2:string>",
                ....
            ]
        },
        ...
    }
}
```

## `Server` configuration file:

To configure the service, save the file `transport_bot.conf.template` with the name `transport_bot.conf`. Open the `transport_bot.conf` file in your favorite editor and set the actual values for all parameters:

- `routes_json` — path to a local JSON file with a list of routes and stops,
- `bind_port` — port to start the `Server`,
- `ors_token` — token to access the [openrouteservice.org](https://openrouteservice.org) service.


## Environment file for `DriverBot` and `PassengerBot`:

To configure bots, save the file `env.template` with the name `.env` in the `transport_bot` directory. Open the `.env` file in your favorite editor and set the actual values for all parameters:

- `TELEGRAM_DRIVER_API_KEY` —  the token of `Telegram` bot, that will become `DriverBot`.
- `TELEGRAM_PASSENGER_API_KEY` —  the token of `Telegram` bot, that will become `PassengerBot`.
- `TRANSPORT_BOT_API` —  address of the `Server`. Leave `http://localhost:5000`, if everything runs on one machine.


# Run the application

1. Run qrcode_generator tool:
    ```
    poetry run qrcode_generator --passenger-bot-name=<BOT_NAME> --routes-data-json=<ROUTE>
    ```
    where BOT_NAME is username for your Telegram bot. It must end with `bot`, e.g. mytransport_bot.
    ROUTE is the path to the routes file.
    For example,
    ```
    poetry run qrcode_generator --passenger-bot-name=mytransport_bot --routes-data-json=tests/routes.json
    ```
    After launching, all QR codes of stops are saved in the `transport_bot/qr_codes` folder.
2. Run `Server`:
    ```
    poetry run server --config transport_bot.conf
    ```

3. Run `DriverBot`:
    * We will use [pagekite](https://pagekite.net/) to get an external address and create a tunnel. You can use any other similar utility, such as [ngrok](https://ngrok.com/) or setup communication through `reverse-proxy`.

    * If you use [pagekite](https://pagekite.net/), you need to register and specify the subdomain to be used to create the tunnel. For example, `driverbot.pagekite.me`.

    * Select the port for `DriverBot`, for example, `5011`
    * Run `pagekite`. Set the port and the external address. For example,
        ```
        python3 pagekite.py 5011 driverbot.pagekite.me
        ```
    * Make sure that `pagekite` has started successfully and created a tunnel
    * Make sure you are in the `transport_bot` directory
    * Run the bot with the command
        ```
        poetry run maxbot run --bot transport_bot.bot:driver --updater=webhooks --host=localhost --port=<BIND_PORT> --public-url=<DRIVER_BOT_PUBLIC_URL>
        ```
        In our particular example:
        ```
        poetry run maxbot run --bot transport_bot.bot:driver --updater=webhooks --host=localhost --port=5011 --public-url=https://driverbot.pagekite.me
        ```


4. Run `PassengerBot`:
    * In the [pagekite control panel](https://pagekite.net/home), add the `kite` to create another tunnel. For example, `passengerbot.pagekite.me`. To do this, click the `add kite` button
    * Select the port for `PassengerBot`, for example, `5012`
    * Run `pagekite`. Set the port and the external address. For example,
        ```
        python3 pagekite.py 5012 passengerbot.pagekite.me
        ```
    * Make sure that `pagekite` has started successfully and created a tunnel
    * Make sure you are in the `transport_bot` directory
    * Run the bot with the command
        ```
        poetry run maxbot run --bot transport_bot.bot:passenger --updater=webhooks --host=localhost --port=<BIND_PORT> --public-url=<PASSENGER_BOT_PUBLIC_URL>
        ```
        In our particular example:
        ```
        poetry run maxbot run --bot transport_bot.bot:passenger --updater=webhooks --host=localhost --port=5012 --public-url=https://passengerbot.pagekite.me
        ```

# Testing

After successfully launching `Server`, `DriverBot` and `PassengerBot` you can test the example.
1. Text `DriverBot` via `Telegram` and follow the hint. Send the geo-position and start the route.
2. Open the QR code and scan it through the phone camera. After you go to the chat, click on the route you are interested in.
3. If the route started by the driver is the same as the selected one, information about the driver and distance to him will be displayed.
4. To test multiple routes and multiple drivers at the same time, you can run the virtual drivers script, see below.

**Note** For `Telegram` on `iOS` it is necessary to scan the QR code when the application is closed or another dialog is open (not with the `PassengerBot`), otherwise the stop will not change.

## Virtual drivers script:

There is a script to create and run virtual drivers: ``transport_bot/virtual_drivers.py``. Virtual drivers are drivers that are created in ``Server`` database, but they have no real `Telegram` clients. The script starts their movement, sends their location on the route after a certain period of time. The movement points are specified inside the script. The script saves the map with stops(small dots in brown color) and locations of these virtual drivers in folder `./virtual_drivers`.

To create two virtual drivers per route run command:
```
poetry run virtual_drivers --config transport_bot.conf
```

#### There are three routes configured in the script:
* Route 9 with drivers Red and Black — from Trafalgar Square, along the south side of the Hyde Park,
* Route 23 with drivers Blue and Purple — along the east side of the Hyde Park to Trafalgar Square,
* Route 13 with drivers Green and Yellow — from Regent's Park, along the east side of the Hyde Park to Buckingham Palace,


#### Modes of the script:
The script also allows you to track the position of virtual drivers on the map. It can save the map with the positions of the drivers at each step of its execution (if `virtual_mode` option is set to `all`). The map images will be in the `virtual_drivers` directory.

If `virtual_mode` is `one` (default), the script will save the map with the drivers' positions only on the last step.


#### Settings for testing:

Open the `transport_bot.conf` file in your favorite editor and set the actual values for the parameters:

* `virtual_count` — the number of steps. Step is a small advance on the routes.
* `virtual_mode` — mode of virtual drivers. Values `one` or `all`.
* `virtual_timeout` — pause between steps in seconds, can be equal to 0.

# Implementation details

This example shows the implementation details of the following features:

- using an external `HTTP` service,
- database schema,
- adding new commands to channels using `mixin`,
- generation of QR codes,
- running tests,
- adding dependencies.

## Using an external HTTP service

- An external `HTTP` service in python is used to implement `Server` business logic.
- Implementation can be found in the `transport_bot/server.py` file and the `transport_bot/api_service` folder.
- It is accessed from bots via external `HTTP` calls ```REST```.

Example:

```yaml
       response: |-
          {% PUT "transport_service://driver/{}/location".format(dialog.user_id) body {
             'latitude': slots.location.latitude,
             'longitude': slots.location.longitude
            }
          %}
```

## Database schema

The database consists of one table for storing information about drivers:
- name
- phone
- chosen route
- current coordinates
- date of last coordinates update

**Note** Routes and stops data are stored in a JSON file, see "The format of the JSON file with routes".


## New commands for messengers (mixin)

- `mixin` is used to add features to communicate with `Telegram` messenger,
- the `channels` folder contains the implementation of additional features of channels.

### ```ContactMixin``` to get a contact (phone number and name) from drivers

- `Telegram` [documentation](https://core.telegram.org/bots/api#contact)

Example of usage in scenario:
```yaml
      - condition: message.contact
        response: |-
          - text: phone={{message.contact.phone_number}}
          - text: phone={{message.contact.first_name}}
```

### ```KeyboardButtonContactMixin``` to send contacts by pressing button in messenger

- `Telegram` [documentation](https://core.telegram.org/bots/api#keyboardbutton)
- The ```request_contact``` parameter is used in implementation for `Telegram`

Example of using in bot scenario:
```yaml
    response: |-
      - keyboard_button_contact:
           title: "Send your phone"
           text: "Could you please send me your contact."
```

### ```LocationMixin``` to obtain and update a driver's location

- `Telegram` [documentation](https://core.telegram.org/bots/api#location)
-  You can enable the function of periodically sending a location ```https://telegram.org/blog/live-locations```, then the ``live_period`` parameter will be added to the location message
- There is no special button to enable live-locations
- You can send an arbitrary location for testing

Example of using in bot scenario:
```yaml
     - condition: message.location
       response: |-
         - text: latitude={{message.location.latitude}}
         - text: longitude={{message.location.longitude}}
         - text: live_period={{message.location.live_period}}
```


**Note** Sending a location and the function ``live location`` work only on phones, the desktop application does not have this functionality.


### ```KeyboardButtonLocationMixin``` to send the current location by pressing button in messenger

- `Telegram` [documentation](https://core.telegram.org/bots/api#keyboardbutton)
- The ```request_location``` parameter is used in implementation for `Telegram`

Example of using in bot scenario:
```yaml
    response: |-
      - keyboard_button_location:
          text: "Enter your location."
          title: "My location"
```

### ```KeyboardButtonListMixin``` to send a list of buttons with any text

- `Telegram` [documentation](https://core.telegram.org/bots/api#)
- Used to start/stop work and change the route

Example of using in bot scenario:
```yaml
    response: |-
      - keyboard_button_list:
          text: "Click to start or change the route:"
          buttons:
             - start route
             - change route
```

### ```InlineKeyboardMixin``` and ```CallbackQueryMixin``` to send inline buttons

- `InlineKeyboardMixin`[documentation](https://core.telegram.org/bots/api#inlinekeyboardmarkup)
- `CallbackQueryMixin`[documentation](https://core.telegram.org/bots/api#callbackquery) — the format of the response when inline buttons are pressed
- Used when displaying the list of routes: each route is a button with the name of the route

Example of using in bot scenario:
```yaml
    response: |-
      - inline_keyboard:
          text: Please choose a route
          rows:
            - row:
               - button:
                   caption: Button name №1
                   callback_data: button_data1
               - button:
                   caption: Button name №2
                   callback_data: button_data2
            - row:
               - button:
                   caption: Button name №3
                   callback_data: button_data3
               - button:
                   caption: Button name №3
                   callback_data: button_data3
```

Example of inline-button handling:
```yaml
- condition: message.callback_query
        label: route
        response: |-
          - text: {{ message.callback_query.data }}
```

### `QRCodeGenerator` generation of QR codes

To generate QR code images, the `QRCodeGenerator` is used.
- It creates QR codes with a deeplink in the format ``https://t.me/{passenger_bot_name}?start={stop_key}``,
- You can find the script in the ``transport_bot/qrcode.py`` file,
- This images are attached at the stops, each stop has its own QR code,
- When you put the phone camera on the QR code you will go to the passenger bot with the parameter ```stop_key``` — the current stop with the list of routes going through this stop,
- When passenger selects the route bot informs him when the nearest driver will arrive.
- Command to start:
```
poetry run qrcode_generator --passenger-bot-name=<BOT_NAME> --routes-data-json=<ROUTE>
```

## Running tests
```bash
poetry shell
poetry install (if not previously installed)
(poetry run) pytest tests/
```

## Adding dependencies

The external python service contains a number of dependencies that need to be installed.
To do this, add these dependencies to the `pyproject.toml` file:
```
[tool.poetry.dependencies]
python = ">=3.9, <3.12"
maxbot = "^0.2.0b2"
click-config-file = {version = "^0.6.0"}
Flask-SQLAlchemy = {version = "^3.0.2"}
...
```

The `maxbot` dependency should be in all examples.
The `tool.poetry.group.dev.dependencies` section lists dependencies to run unit tests ,
in this example it is:
```
[tool.poetry.group.dev.dependencies]
pytest = "^7.2.0"  (for pytest based unit tests)
httpretty = "^1.1.4" (mock library for `HTTP` modules)
```

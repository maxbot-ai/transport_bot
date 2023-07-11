"""Virtual drivers."""

import os
import secrets
import time

import click
import click_config_file
import plotly.graph_objects as go
from requests_toolbelt.sessions import BaseUrlSession

from .api_service.route import route_data

OUTPUT_IMAGE_PATH = "virtual_drivers"

# Stops - small dots in brown color
# Route 9 with drivers Red and Black — from Trafalgar Square, along the south side of the Hyde Park,
# Route 23 with drivers Blue and Purple — along the east side of the Hyde Park to Trafalgar Square,
# Route 13 with drivers Green and Yellow — from Regent's Park, along the east side of the Hyde Park to Buckingham Palace.

ROUTE_9 = [
    (51.507662195407136, -0.1289855671072736),
    (51.507708566506324, -0.13023896266876048),
    (51.5077576652658, -0.13096645799465845),
    (51.50832229719681, -0.13158439077147543),
    (51.50915423007047, -0.1323031212081881),
    (51.509675203255526, -0.13270192898146727),
    (51.5096516740264, -0.13272798122687032),
    (51.51006062198672, -0.13377156479309998),
    (51.50999189149369, -0.1348206699655002),
    (51.50945579008969, -0.13580351586385409),
    (51.509308017439785, -0.13633911166239526),
    (51.508453314287976, -0.13914486565912262),
    (51.507758836658105, -0.14087220826425745),
    (51.50629738754516, -0.14383863106935532),
    (51.50544630751181, -0.14549083462990786),
    (51.50440425839184, -0.1475944359579245),
    (51.503626557691035, -0.1492988882813801),
    (51.503050955545845, -0.15338104669727337),
    (51.50238458370088, -0.15676802889225672),
    (51.501990104795496, -0.1599473526842036),
    (51.50169264655158, -0.1627764926368861),
    (51.501729752248814, -0.1655163493345772),
    (51.501893845551564, -0.16706730439735867),
    (51.501914670331026, -0.1694903350560538),
    (51.50200094431612, -0.17095753498766075),
    (51.50177484662478, -0.1743077215321834),
    (51.501614197579414, -0.17695059341554073),
    (51.50148627293869, -0.18095074456820468),
    (51.50168559722616, -0.1835219290780481),
    (51.50202176904924, -0.1851420621926298),
    (51.50231777669545, -0.18737870589379793),
    (51.50245611126544, -0.18821744722277844),
    (51.50206612803176, -0.1905553722993105),
    (51.50135137374703, -0.19212869066661725),
]


ROUTE_23 = [
    (51.51704238540009, -0.1692961725235801),
    (51.51774339775926, -0.16699483738442814),
    (51.51701567994176, -0.16575565682456372),
    (51.516034243933035, -0.16431262836679936),
    (51.51534989677608, -0.16327729567610674),
    (51.513770851681855, -0.1608794008756174),
    (51.5133673601521, -0.15909946333455788),
    (51.512392522555075, -0.1576671635993081),
    (51.511057094732266, -0.15710389967380453),
    (51.51033594742264, -0.1566425596844827),
    (51.50976169234421, -0.15592909214716985),
    (51.50880347151711, -0.15466845391929035),
    (51.50847626955145, -0.15408909682132205),
    (51.50717077705758, -0.15286600945444243),
    (51.506125135535164, -0.1515447214507912),
    (51.50578455831773, -0.1510994747921674),
    (51.50435026636014, -0.15107265262176175),
    (51.50327424048349, -0.1500190961015236),
    (51.504109030026314, -0.148345397818504),
    (51.505110757325035, -0.14597432487697284),
    (51.506446359433795, -0.14356033689763475),
    (51.507040689780816, -0.14247672454773105),
    (51.50768171257503, -0.14100238512361157),
    (51.508419595937994, -0.1391355678079359),
    (51.508656650971744, -0.1380734129263174),
    (51.50917082241618, -0.13664111327086825),
    (51.5095481003565, -0.13546630582221028),
    (51.510085632573755, -0.13454899023195602),
    (51.51007895517467, -0.13338491150991647),
    (51.509684988038515, -0.13268753722532498),
    (51.508987190428094, -0.13204917153404508),
    (51.508412918334486, -0.1316253824595317),
    (51.507728456685975, -0.13087972837482373),
    (51.507678373723095, -0.1296941920910182),
    (51.507601579739735, -0.12895390246583646),
]

ROUTE_13 = [
    (51.52713398027047, -0.16414437160519452),
    (51.526338678056426, -0.16263846474418284),
    (51.52612926325003, -0.16185514112154978),
    (51.52570083490099, -0.16120450246115905),
    (51.525395262211916, -0.16072601711839302),
    (51.52494162474968, -0.15985005987972223),
    (51.52452893674772, -0.15910828106406635),
    (51.5239020218606, -0.15833359056489116),
    (51.52354702699902, -0.15804078158632912),
    (51.52296924252494, -0.1578922023990474),
    (51.52279301679325, -0.1577900541702958),
    (51.52241456252463, -0.1576182594850013),
    (51.52135125740346, -0.1571429883845284),
    (51.52071635210357, -0.1569457411461899),
    (51.519878452356984, -0.15645262299520551),
    (51.518719528996066, -0.15596709125615116),
    (51.51808222661076, -0.1556788068308872),
    (51.517801338654074, -0.15547017994418297),
    (51.5172608014704, -0.1552539665581668),
    (51.516755184265534, -0.15509493613249004),
    (51.51580970069723, -0.15462049403340142),
    (51.51503909442678, -0.15429529364004815),
    (51.51462639945856, -0.15408146968643702),
    (51.5140613345551, -0.15390225330694648),
    (51.51387437342951, -0.15415144009317555),
    (51.51377984208936, -0.15525018403223878),
    (51.513732576343024, -0.15652361320167776),
    (51.5135923543439, -0.15746792552946637),
    (51.51332131911974, -0.15824513406022483),
    (51.51274624345199, -0.1579413338927419),
    (51.512508333308595, -0.15779449713285845),
    (51.51217746283537, -0.1576350020389041),
    (51.512012872172356, -0.1574867396569638),
    (51.511481896892, -0.1573019278498899),
    (51.51095091542627, -0.1570310393448362),
    (51.51037423417964, -0.1566766057732802),
    (51.50977313684606, -0.1559432959534438),
    (51.50913642870714, -0.15512488599613838),
    (51.50866950374997, -0.15447697811327157),
    (51.50817935272311, -0.15399842521084212),
    (51.50764246796477, -0.15335656748219367),
    (51.506864587672354, -0.15244656097072354),
    (51.505810409853304, -0.15126441325461565),
    (51.505078131024966, -0.15088930864447114),
    (51.50441538999499, -0.1509521125957345),
    (51.504294985803746, -0.15105663982639597),
    (51.50360513530607, -0.15092023813930724),
    (51.50280879367596, -0.149698568142557),
    (51.50208083727767, -0.15101821486570707),
    (51.50132615458148, -0.15070707850962145),
    (51.500631568325254, -0.14963419492190463),
    (51.50003047550211, -0.148808074465061),
    (51.49918893226915, -0.14776737745574753),
    (51.49822559024628, -0.14638188907511324),
    (51.49806529114725, -0.143989358837207),
    (51.49732390048074, -0.14436486806737167),
    (51.4969431816683, -0.14467600428665095),
    (51.496883067880894, -0.1456415994499315),
]


def get_center(routes):
    max_lon = max(r[1] for r in routes)
    min_lon = min(r[1] for r in routes)
    max_lat = max(r[0] for r in routes)
    min_lat = min(r[0] for r in routes)
    return {"lon": (max_lon + min_lon) / 2, "lat": (max_lat + min_lat) / 2}


DRIVER_SIZE = 10
STOP_SIZE = 6
CENTER = get_center(ROUTE_9 + ROUTE_23 + ROUTE_13)
SESSIONS = {}


def start_driver(driver_id, route, color, location):
    data = {
        "phone": f"Phone{driver_id}",
        "route": route,
        "name": color,
        "latitude": location[0],
        "longitude": location[1],
    }
    resp = SESSIONS["server"].post(f"/driver/{driver_id}", json=data)
    assert resp.status_code == 200
    resp = SESSIONS["server"].post(f"/driver/{driver_id}/start", json={})
    assert resp.status_code == 200


def stop_driver(driver_id):
    resp = SESSIONS["server"].post(f"/driver/{driver_id}/stop", json={})
    assert resp.status_code == 200


def update_location(driver_id, location):
    data = {"latitude": location[0], "longitude": location[1]}
    resp = SESSIONS["server"].put(f"/driver/{driver_id}/location", json=data)
    assert resp.status_code == 200


def create_mapbox_stops(stops):
    return go.Scattermapbox(
        mode="markers",
        lon=[s[1] for s in stops],
        lat=[s[0] for s in stops],
        marker=dict(size=STOP_SIZE, color="brown"),
    )


def create_mapbox(driver, color):
    return go.Scattermapbox(
        mode="markers",
        lon=[driver[1]],
        lat=[driver[0]],
        marker=dict(size=DRIVER_SIZE, color=color),
    )


def save_route_image(stops, driver1, driver2, driver3, driver4, driver5, driver6, name):
    stops = [(s["location"]["lat"], s["location"]["lon"]) for _, s in stops.items()]

    fig = go.Figure(create_mapbox_stops(stops))

    fig.add_trace(create_mapbox(driver1, "Red"))
    fig.add_trace(create_mapbox(driver2, "Blue"))
    fig.add_trace(create_mapbox(driver3, "Green"))

    fig.add_trace(create_mapbox(driver4, "Black"))
    fig.add_trace(create_mapbox(driver5, "Purple"))
    fig.add_trace(create_mapbox(driver6, "Yellow"))

    mapbox = {"center": CENTER, "style": "open-street-map", "zoom": 12.9}
    fig.update_layout(margin={"l": 0, "t": 0, "b": 0, "r": 0}, mapbox=mapbox)
    fig.update(layout_showlegend=False)
    fig.update_layout(width=800, height=800)
    fig.write_image(name)


def update_all_location(stops, drivers, i):
    i1 = i % len(ROUTE_9)
    i2 = i % len(ROUTE_23)
    i3 = i % len(ROUTE_13)

    j1 = (i + 17 + secrets.randbelow(6)) % len(ROUTE_9)
    j2 = (i + 17 + secrets.randbelow(6)) % len(ROUTE_23)
    j3 = (i + 17 + secrets.randbelow(6)) % len(ROUTE_13)

    update_location(drivers[0], ROUTE_9[i1])
    update_location(drivers[1], ROUTE_23[i2])
    update_location(drivers[2], ROUTE_13[i3])

    update_location(drivers[3], ROUTE_9[j1])
    update_location(drivers[4], ROUTE_23[j2])
    update_location(drivers[5], ROUTE_13[j3])
    save_route_image(
        stops,
        ROUTE_9[i1],
        ROUTE_23[i2],
        ROUTE_13[i3],
        ROUTE_9[j1],
        ROUTE_23[j2],
        ROUTE_13[j3],
        f"{OUTPUT_IMAGE_PATH}/drivers_map_step_{i + 1}.jpg.png",
    )


def run(stops, steps, timeout):
    drivers = range(1, 7)
    i = 0
    start_driver(drivers[0], "9", "Red", ROUTE_9[i])
    start_driver(drivers[1], "23", "Blue", ROUTE_23[i])
    start_driver(drivers[2], "13", "Green", ROUTE_13[i])

    start_driver(drivers[3], "9", "Black", ROUTE_9[i])
    start_driver(drivers[4], "23", "Purple", ROUTE_23[i])
    start_driver(drivers[5], "13", "Yellow", ROUTE_13[i])
    try:
        while i < steps:
            update_all_location(stops, drivers, i)
            time.sleep(timeout)
            i = i + 1
    except Exception as e:
        print("Error", e)
        for driver in drivers:
            stop_driver(driver)


def one_step(stops, i):
    drivers = range(1, 7)

    start_driver(drivers[0], "9", "Red", ROUTE_9[i])
    start_driver(drivers[1], "23", "Blue", ROUTE_23[i])
    start_driver(drivers[2], "13", "Green", ROUTE_13[i])

    start_driver(drivers[3], "9", "Black", ROUTE_9[i])
    start_driver(drivers[4], "23", "Purple", ROUTE_23[i])
    start_driver(drivers[5], "13", "Yellow", ROUTE_13[i])
    update_all_location(stops, drivers, i)


@click.command()
@click.option("--bind-port", "bind_port", type=int, required=True, help="Server bind port")
@click.option("--routes-json", "routes_json", type=str, required=True, help="Routes json")
@click.option("--virtual-mode", "virtual_mode", type=str, required=True, help="mode: one or all")
@click.option("--virtual-count", "virtual_count", type=int, required=False, help="count")
@click.option("--virtual-timeout", "virtual_timeout", type=int, required=False, help="timeout")
@click_config_file.configuration_option()
def main(bind_port, routes_json, virtual_mode, virtual_count, virtual_timeout):
    """Run virtual drivers."""
    SESSIONS["server"] = BaseUrlSession(f"http://localhost:{bind_port}")
    route_data.load_from_json(routes_json)
    if not os.path.exists(OUTPUT_IMAGE_PATH):
        os.mkdir(OUTPUT_IMAGE_PATH)
    if virtual_mode == "all":
        run(route_data["stops"], steps=virtual_count or 1, timeout=virtual_timeout or 0)
    elif virtual_mode == "one":
        one_step(route_data["stops"], virtual_count or 0)
    print("Virtual drivers have been successfully added. See ./virtual_drivers.")


main()  # pylint: disable=no-value-for-parameter

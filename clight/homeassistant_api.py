from .config import api_endpoint, api_key, default_group, default_media_player
import requests
from json import dumps as json
from struct import unpack


ha_headers = {
    "x-ha-access": api_key,
    "content-type": "application/json",
}


def set_light(state, group=default_group, level=None, color=None):
    data = {
        "entity_id": "group.{}".format(group),
    }
    if level:
        data.update({
            "brightness": level,
        })
    if color:
        data.update({
            "rgb_color": list(
                unpack(
                    "BBB",
                    bytes.fromhex(color.lstrip("#"))
                )
            ),
	})
    assert requests.post(api_endpoint+"/homeassistant/turn_{}".format(state),
                         headers=ha_headers,
                         data=json(data)).ok


def chrome(action, entity=default_media_player, debug=None, **kw):
    data = {}
    path = "/media_player/media_{}".format(action)
    data.update({"entity_id": entity})
    data.update(**kw)
    if debug:
        print(data)
    assert requests.post(
        api_endpoint+path,
        headers=ha_headers,
        data=json(data)).ok

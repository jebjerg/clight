import configparser

conf = configparser.ConfigParser()
conf.read("clight.ini")
api_key = conf["homeassistant"]["api_key"]
api_endpoint = conf["homeassistant"]["endpoint"]
if api_endpoint.endswith("/"):
    api_endpoint = api_endpoint[:-1]
default_group = conf["homeassistant"]["default_group"]
default_media_player = conf["homeassistant"]["default_media_player"]

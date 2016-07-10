from os import getenv
import configparser

conf = configparser.ConfigParser()
conf.read("{}/clight.ini".format(getenv("HOME", ".")))

bridge_host = conf["hue"]["host"]
# specify username in conf, or rely on phue builtin
bridge_username = conf["hue"]["username"]
default_group = conf["hue"]["default_group"]

chrome_addr = conf["chromecast"]["address"]

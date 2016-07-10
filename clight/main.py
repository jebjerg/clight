import click
from clight import config
from clight import hue
import socket
from os import path


@click.group()
def cli():
    pass


@click.command()
@click.argument("level", type=int)
@click.option("--color", help="hex value, e.g. ff0000")
@click.option("--group", help="entity", default=config.default_group)
# @hue.need_bridge
def level(level, group, color):
    hue.check_bridge()  # see main.on TODO
    # homeassistant.set_light(state="on",
    #                         group=group,
    #                         level=255*(level/100.),
    #                         color=color
    #                         )
    [hue.bridge.set_group(g.group_id, "bri", 255*(level/100.))
     for g in hue.bridge.groups if g.name == group]


@click.command()
@click.option("--group", default=config.default_group)
# @hue.need_bridge
def on(group):
    # TODO: until I figure out how to use a decorator (hue.need_bridge) and
    # @click at the same time (@command;@hue.need_bridge renames to command to
    # wrapper
    hue.check_bridge()

    [hue.bridge.set_group(g.group_id, "on", True)
     for g in hue.bridge.groups if g.name == group]


@click.command()
@click.option("--group", default=config.default_group)
# @hue.need_bridge
def off(group):
    hue.check_bridge()
    [hue.bridge.set_group(g.group_id, "on", False)
     for g in hue.bridge.groups if g.name == group]


def chromesocket(action):
    c = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    c.connect(config.chrome_addr)
    c.sendall(action)
    return c.recv(512).decode()


@click.command()
def play(entity):
    if path.exists(config.chrome_addr):  # unix socket
        chromesocket(b"play")
    else:
        c = pychromecast.get_chromecast()
        c.media_controller.play()


@click.command()
def pause(entity):
    if path.exists(config.chrome_addr):  # unix socket
        chromesocket(b"pause")
    else:
        c = pychromecast.get_chromecast()
        c.media_controller.pause()


@click.command()
def playpause(entity):
    if path.exists(config.chrome_addr):  # unix socket
        chromesocket(b"toggle")
    else:
        raise NotImplementedError


@click.command()
@click.argument("url", type=str)
@click.option("--debug/--no-debug", default=None)
@click.option("--wait/--no-wait", default=None)
@click.option("--repeat/--no-repeat", default=None)
def stream(url, debug, wait, repeat):
    from pychromecast import get_chromecast
    from mimetypes import types_map
    from os.path import splitext
    from time import sleep
    from json import dumps
    c = get_chromecast()
    c.wait()
    while True:
        if debug:
            print("play_media: {}".format(url))
        c.play_media(url, types_map.get(splitext(url)[-1]))
        c.wait()
        if wait or repeat:
            sleep(10)
            if debug:
                print("waiting for playback to stop")
            while c.media_controller.status \
                    and c.media_controller.status.player_state == "PLAYING" \
                    and c.media_controller.status.content_id == url:
                print("\r{}".format(dumps(c.media_controller.status.__dict__))
                      if debug else "\rstill zZZz'ing", end="")
                sleep(10)
                continue
            if repeat:
                continue
            else:
                print("\rdone. status: {}".format(c.status) if debug else "")
        break

cli.add_command(level)
cli.add_command(on)
cli.add_command(off)
cli.add_command(play)
cli.add_command(pause)
cli.add_command(playpause)
cli.add_command(stream)

if __name__ == "__main__":
    cli()

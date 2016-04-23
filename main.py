import click
import homeassistant_api as homeassistant


@click.group()
def cli():
    pass


@click.command()
@click.argument("level", type=int)
@click.option("--color", help="hex value, e.g. ff0000")
@click.option("--group", help="entity", default=homeassistant.default_group)
def level(level, group, color):
    homeassistant.set_light(state="on",
                            group=group,
                            level=255*(level/100.),
                            color=color
                            )


@click.command()
@click.option("--group", default=homeassistant.default_group)
def on(group):
    homeassistant.set_light("on", group)


@click.command()
@click.option("--group", default=homeassistant.default_group)
def off(group):
    homeassistant.set_light("off", group)


@click.command()
@click.option("--entity", default=homeassistant.default_media_player)
def play(entity):
    homeassistant.chrome("play", entity)


@click.command()
@click.option("--entity", default=homeassistant.default_media_player)
def pause(entity):
    homeassistant.chrome("pause", entity)


@click.command()
@click.option("--entity", default=homeassistant.default_media_player)
def playpause(entity):
    homeassistant.chrome("play_pause", entity)


@click.command()
@click.argument("url", type=str)
@click.option("--entity", default=homeassistant.default_media_player)
@click.option("--debug/--no-debug", default=None)
@click.option("--wait/--no-wait", default=None)
@click.option("--repeat/--no-repeat", default=None)
def stream(url, entity, debug, wait, repeat):
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

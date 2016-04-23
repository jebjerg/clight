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
def stream(url, entity, debug):
    from pychromecast import get_chromecast
    from mimetypes import types_map
    from os.path import splitext
    if debug:
        print("play_media: {}".format(url))
    get_chromecast().play_media(url, types_map.get(splitext(url)[-1]))

cli.add_command(level)
cli.add_command(on)
cli.add_command(off)
cli.add_command(play)
cli.add_command(pause)
cli.add_command(playpause)
cli.add_command(stream)

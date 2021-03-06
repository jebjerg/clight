import click
from clight import config
from clight import hue
from pychromecast import Chromecast  # TODO: from clight import chrome
from time import sleep


def get_cast():
    c = Chromecast(config.chrome_host)
    c.wait()
    sleep(.1)
    return c


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
    [hue.bridge.set_group(g.group_id, "bri", int(255*(level/100.)))
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


@click.command()
def play():
    c = get_cast()
    c.media_controller.play()


@click.command()
def pause():
    c = get_cast()
    c.media_controller.pause()


@click.command()
def playpause():
    c = get_cast()
    state = c.media_controller.status.player_state
    if state == "PLAYING":
        c.media_controller.pause()
    elif state == "PAUSED":
        c.media_controller.play()
    else:
        raise NotImplementedError


@click.command()
@click.argument("url", type=str)
@click.option("--debug/--no-debug", default=None)
@click.option("--wait/--no-wait", default=None)
@click.option("--repeat/--no-repeat", default=None)
def stream(url, debug, wait, repeat):
    from mimetypes import types_map
    from os.path import splitext
    from time import sleep
    from json import dumps
    c = get_cast()
    while True:
        if debug:
            print("play_media: {}".format(url))
        c.wait()
        sleep(.5)
        for i in range(5):
            if (c.media_controller.status.player_state == "PLAYING"
                or c.media_controller.status.player_state == "BUFFERING") \
                    and c.media_controller.status.content_id == url:
                break
            c.play_media(url, types_map.get(splitext(url)[-1]))
            c.wait()
            sleep(2)

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


@click.command()
@click.option("--debug/--no-debug", default=None)
def quit(debug):
    c = get_cast()
    c.quit_app()
    c.wait()


from parsec import many1, string, regex, one_of, optional, eof
from functools import partial


def delta_fn(args):
    op, seconds = args

    def wrapped(mul, delta, current, total):
        return current + mul*delta
    return partial(wrapped, -1 if op == "-" else 1, seconds)


def border_relative_fn(args):
    op, seconds = args

    def wrapped(mul, delta, current, total):
        return total - delta if mul == -1 else delta
    return partial(wrapped, -1 if op == "]" else 1, seconds)

units = {"h": 60*60, "m": 60, "s": 1}
digits = many1(regex("[0-9]"))
whitespace = optional(regex(r"\s*"))

time_spec = whitespace >> (
    many1(digits + one_of("hms")) ^ digits.parsecmap(lambda x: [(x, "s")])  # transform 1234 to 1234s
).parsecmap(lambda args: sum([int("".join(ns)) * units[u] for ns, u in args]))  # add up units to seconds

from_start, from_end = (string("[") + time_spec), (time_spec + string("]")).parsecmap(lambda x: tuple(reversed(x)))

delta_spec = (one_of("-+") + time_spec).parsecmap(delta_fn)
border_spec = (from_start ^ from_end).parsecmap(border_relative_fn)
absolute_spec = time_spec.parsecmap(lambda seconds: border_relative_fn("", seconds))
seek_spec = whitespace >> (delta_spec ^ border_spec ^ absolute_spec) << whitespace + eof()


@click.command()
@click.argument("time", type=str)
def seek(time):
    c = get_cast()
    current_time = c.media_controller.status.current_time
    total_time = c.media_controller.status.duration
    if current_time:
        fn = seek_spec.parse(time)
        seek_value = fn(current_time, total_time)
        c.media_controller.seek(seek_value)

cli.add_command(level)
cli.add_command(on)
cli.add_command(off)
cli.add_command(play)
cli.add_command(pause)
cli.add_command(playpause)
cli.add_command(stream)
cli.add_command(seek)
cli.add_command(quit)

if __name__ == "__main__":
    cli()

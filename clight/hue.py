from clight import config
import phue

bridge = None


def need_bridge(fn):
    try:
        def wrapper(*a, **kw):
            global bridge
            print("wut")
            if not bridge:
                print("wat")
                bridge = phue.Bridge(
                    ip=config.bridge_host,
                    username=config.bridge_username
                )
                bridge.connect()
            return fn(*a, **kw)
        return wrapper
    except Exception as e:
        print("FF", e)


def check_bridge():
    global bridge
    if not bridge:
        bridge = phue.Bridge(
            ip=config.bridge_host,
            username=config.bridge_username
        )
        bridge.connect()

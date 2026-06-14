import os

from aqt import mw


addon_path = os.path.dirname(__file__)
addonfoldername = os.path.basename(addon_path)


_config_cache = {}


def invalidate_config_cache():
    _config_cache.clear()


def gc(arg="", fail=False):
    cache_key = f"__all__" if not arg else arg
    if cache_key not in _config_cache:
        conf = mw.addonManager.getConfig(__name__)
        if conf:
            if arg:
                _config_cache[cache_key] = conf.get(arg, fail)
            else:
                _config_cache[cache_key] = conf
        else:
            _config_cache[cache_key] = fail
    return _config_cache[cache_key]


userOption = None


def _getUserOption(refresh):
    global userOption
    if userOption is None or refresh:
        userOption = mw.addonManager.getConfig(__name__)


def getUserOption(key=None, default=None, refresh=False):
    _getUserOption(refresh)
    if key is None:
        return userOption
    if key in userOption:
        return userOption[key]
    else:
        return default


def writeConfig(configToWrite=userOption):
    mw.addonManager.writeConfig(__name__, configToWrite)


def getDefaultConfig():
    addon = __name__.split(".")[0]
    return mw.addonManager.addonConfigDefaults(addon)

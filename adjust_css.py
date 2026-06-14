# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import os
import shutil
import random
import time

from aqt import gui_hooks, mw

from .config import addon_path, addonfoldername, gc
from anki.utils import pointVersion

_debug_log = open(
    os.path.join(os.path.dirname(__file__), "debug.log"), "a", buffering=1
)


def _log(msg):
    _debug_log.write(f"{time.perf_counter():.3f}s  {msg}\n")


IMAGE_EXTS = (
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".svg",
    ".ico",
    ".bmp",
    ".apng",
    ".avif",
)


def get_bg_folder():
    return os.path.join(addon_path, "user_files", "background")


def get_bg_css_url(imgname):
    if not imgname:
        return ""
    return f"/_addons/{addonfoldername}/user_files/background/{imgname}"


def add_bg_img(imgname, location, review=False):
    img_web_rel_path = get_bg_css_url(imgname)
    is_gif = imgname and imgname.lower().endswith(".gif")
    if location == "body":
        bg_position = gc("background-position", "center")
        bg_color = gc("background-color main", "")
    elif location == "top" and gc("Toolbar top/bottom"):
        bg_position = "top"
    elif location == "bottom" and gc("Toolbar top/bottom"):
        bg_position = "bottom;"
    else:
        bg_position = f"""background-position: {gc("background-position", "center")};"""
    if location == "top":
        bg_color = gc("background-color top", "")
    elif location == "bottom":
        bg_color = gc("background-color bottom", "")
    if review:
        opacity = gc("background opacity review", "1")
    else:
        opacity = gc("background opacity main", "1")
    scale = gc("background scale", "1")

    bracket_start = "body::before {"
    bracket_close = "}"
    if review and not gc("Reviewer image"):
        background = "background-image:none!important;"
    else:
        transform_css = (
            ""
            if is_gif
            else f"\n    will-change: transform;\n    transform: scale({scale});"
        )
        background = f"""
    background-image: url("{img_web_rel_path}"); 
    background-size: {gc("background-size", "contain")};  
    background-attachment: {gc("background-attachment", "fixed")}!important; 
    background-repeat: no-repeat;
    background-position: {bg_position};
    background-color: {bg_color}!important; 
    opacity: {opacity};
    content: "";
    top: 0;
    left: 0;
    bottom: 0;
    right: 0;
    position: fixed;
    z-index: -99;{transform_css}
    """

    css = f"""{bracket_start}\n{background}\n{bracket_close}"""
    return css


_bgimg_list_cache = None


def get_bg_img():
    global _bgimg_list_cache
    bg_abs_path = get_bg_folder()
    os.makedirs(bg_abs_path, exist_ok=True)
    if bg_abs_path == os.path.join(addon_path, "user_files", "background"):
        if not os.listdir(bg_abs_path):
            shutil.copytree(
                src=os.path.join(addon_path, "user_files", "default_background"),
                dst=bg_abs_path,
                dirs_exist_ok=True,
            )

    if _bgimg_list_cache is None:
        all_files = [
            os.path.basename(f)
            for f in os.listdir(bg_abs_path)
            if f.lower().endswith(IMAGE_EXTS)
        ]
        stems = {}
        for f in all_files:
            stem, ext = os.path.splitext(f)
            if ext.lower() == ".webp":
                stems[stem] = f
        _bgimg_list_cache = []
        for f in all_files:
            stem, ext = os.path.splitext(f)
            if ext.lower() != ".webp" and stem in stems:
                _bgimg_list_cache.append(stems[stem])
            else:
                _bgimg_list_cache.append(f)

    val = gc("Image name for background")
    if val and val.lower() == "random":
        result = random.choice(_bgimg_list_cache)
        _log(f"bg -> {result}")
        return result
    if val in _bgimg_list_cache:
        _log(f"bg -> {val}")
        return val
    _log("bg -> empty")
    return ""


imgname = get_bg_img()


def reset_image(browser, content):
    global imgname
    imgname = get_bg_img()
    if pointVersion() >= 27:
        mw.toolbar.draw()


gui_hooks.deck_browser_will_render_content.append(reset_image)


def adjust_deckbrowser_css():
    cont = add_bg_img(imgname, "body")
    # do not invert gears if using personal image
    if gc("Image name for gear") != "gears.svg":
        cont += """
.nightMode .gears {
  filter: none;
}
"""
    return cont


def adjust_toolbar_css():
    cont = add_bg_img(imgname, "top")
    return cont


def adjust_bottomtoolbar_css():
    cont = add_bg_img(imgname, "bottom")
    return cont


def adjust_overview_css():
    cont = add_bg_img(imgname, "body")
    return cont


def adjust_congrats_css():
    cont = add_bg_img(imgname, "body")
    return cont


def adjust_reviewer_css():
    cont = add_bg_img(imgname, "body", True)
    return cont


def adjust_reviewerbottom_css():
    cont = add_bg_img(imgname, "bottom", True)
    return cont

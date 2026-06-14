# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import os
import random
import sys
import time
from pathlib import Path
import json

_debug_log = open(
    os.path.join(os.path.dirname(__file__), "debug.log"), "a", buffering=1
)


def _log(msg):
    _debug_log.write(f"{time.perf_counter():.3f}s  {msg}\n")


from anki.utils import pointVersion
from aqt import mw
from aqt import gui_hooks
from aqt.editor import pics

# for the toolbar buttons
from aqt.qt import *
from aqt.addons import *
from aqt.utils import openFolder
from .adjust_css import *

from .config import (
    addon_path,
    addonfoldername,
    gc,
    getUserOption,
    invalidate_config_cache,
)

# from .gui import Manager
# a = Manager()
from . import gui_updatemanager

css_folder_for_anki_version = {
    "22": "22",
    "23": "22",
    "24": "22",
    "25": "25",
    "26": "25",
    "27": "25",
    "28": "25",
    "29": "25",
    "30": "25",
    "31": "31",
    "32": "31",
    "33": "31",
    "34": "31",
    "35": "31",
    "36": "36",
    "37": "36",
    "38": "36",
    "39": "36",
    "40": "36",
    "41": "36",
    "42": "36",
    "43": "36",
    "44": "36",
    "45": "36",
    "46": "36",
    "47": "36",
    "48": "36",
    "49": "36",
    "50": "36",
    "51": "36",
    "52": "36",
    "53": "36",
    "54": "36",
    "55": "55",
}
v = str(pointVersion())

if v in css_folder_for_anki_version:
    version_folder = css_folder_for_anki_version[v]
else:  # for newer Anki versions try the latest version and hope for the best
    version_folder = css_folder_for_anki_version[
        max(css_folder_for_anki_version, key=int)
    ]


regex = r"(user_files.*|web.*)"
mw.addonManager.setWebExports(__name__, regex)


# reset background when changing config
def apply_config_changes(config):
    invalidate_config_cache()
    mw.moveToState("deckBrowser")


mw.addonManager.setConfigUpdatedAction(__name__, apply_config_changes)


css_files_to_modify = [
    "webview.css",
    "deckbrowser.css",
    "overview.css",
    "reviewer-bottom.css",
    "toolbar-bottom.css",
    "reviewer.css",
    "toolbar.css",
]

from anki.utils import pointVersion


def maybe_adjust_filename_for_2136(filename):
    if pointVersion() >= 36:
        filename = filename.lstrip("css/")
    return filename


_path_exists_cache = {}


def inject_css(web_content, context):
    for filename in web_content.css.copy():
        filename = maybe_adjust_filename_for_2136(filename)
        if filename in css_files_to_modify:
            addon_css_path = os.path.join(
                addon_path, "web", "css", version_folder, filename
            )
            if _path_exists_cache.get(addon_css_path, False) or os.path.exists(
                addon_css_path
            ):
                _path_exists_cache[addon_css_path] = True
                web_content.css.append(
                    f"/_addons/{addonfoldername}/web/css/{version_folder}/{filename}"
                )

            user_css_path = os.path.join(
                addon_path, "user_files", "css", f"custom_{filename}"
            )
            if _path_exists_cache.get(user_css_path, False) or os.path.exists(
                user_css_path
            ):
                _path_exists_cache[user_css_path] = True
                web_content.css.append(
                    f"/_addons/{addonfoldername}/user_files/css/custom_{filename}"
                )

        f = filename
        css = ""
        if f == "deckbrowser.css":
            css = adjust_deckbrowser_css()
        if f == "toolbar.css" and gc("Toolbar image"):
            css = adjust_toolbar_css()
        if f == "overview.css":
            css = adjust_overview_css()
        if f == "toolbar-bottom.css" and gc("Toolbar image"):
            css = adjust_bottomtoolbar_css()
        if f == "reviewer.css" and gc("Reviewer image"):
            css = adjust_reviewer_css()
        if f == "reviewer-bottom.css":
            if v == 22:
                if gc("Reviewer image") and gc("Toolbar image"):
                    css = adjust_reviewerbottom_css()
            else:
                css = adjust_reviewerbottom_css()
        if css:
            web_content.head += f"<style>{css}</style>"


def inject_css_into_ts_page(web):
    page = os.path.basename(web.page().url().path())
    # Handle both old and new formats
    if page not in ("congrats.html", "congrats"):
        return

    css = adjust_congrats_css()
    web.eval(
        """
(() => {
    const style = document.createElement("style");
    style.textContent= %s;
    document.head.appendChild(style);
})();
"""
        % json.dumps(css)
    )


gui_hooks.webview_will_set_content.append(inject_css)
gui_hooks.webview_did_inject_style_into_page.append(inject_css_into_ts_page)


_gear_list_cache = []


def get_gearfile():
    global _gear_list_cache
    gear_abs = os.path.join(addon_path, "user_files", "gear")
    os.makedirs(gear_abs, exist_ok=True)
    if not os.listdir(gear_abs):
        shutil.copytree(
            src=os.path.join(addon_path, "user_files", "default_gear"),
            dst=gear_abs,
            dirs_exist_ok=True,
        )

    if not _gear_list_cache:
        _gear_list_cache = [
            os.path.basename(f)
            for f in os.listdir(gear_abs)
            if f.lower().endswith(IMAGE_EXTS)
        ]
    val = gc("Image name for gear")
    if val and val.lower() == "random":
        r = random.choice(_gear_list_cache)
        _log(f"gear -> {r}")
        return r
    if val in _gear_list_cache:
        _log(f"gear -> {val}")
        return val
    _log("gear -> empty")
    return ""


def replace_gears(deck_browser, content):
    if gc("Image name for gear") == "gears.svg":
        return
    old = """<img src='/_anki/imgs/gears.svg'"""
    new = f"""<img src='/_addons/{addonfoldername}/user_files/gear/{get_gearfile()}'"""
    content.tree = content.tree.replace(old, new)


gui_hooks.deck_browser_will_render_content.append(replace_gears)


# No longer needed
"""
menu = QMenu(('Custom Background & Gear Icon'), mw)
mw.form.menuTools.addMenu(menu)

#add config button
def on_advanced_settings():
	addonDlg = AddonsDialog(mw.addonManager)
	addonDlg.accept() #closes addon dialog
	ConfigEditor(addonDlg,__name__,mw.addonManager.getConfig(__name__))

#menu.addSeparator()
advanced_settings = QAction('Set up Background/Gear (Config)', mw)
menu.addAction(advanced_settings)
advanced_settings.triggered.connect(on_advanced_settings)

shortcut = gc("Keyboard Shortcut", "Ctrl+shift+b")
#add folder button
imgfolder = os.path.join(addon_path, "user_files") 
action = QAction(mw) 
action.setText("Background/gear image folder") 
action.setShortcut(QKeySequence(shortcut))
menu.addAction(action) 
action.triggered.connect(lambda: openFolder(imgfolder))
"""

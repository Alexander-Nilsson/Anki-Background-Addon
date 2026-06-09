# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import os
import shutil
import random
import base64

from aqt.editor import pics
from aqt import gui_hooks

from .config import addon_path, addonfoldername, gc

# Supported image extensions
IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".ico", ".bmp", ".apng", ".avif")

MIME_MAP = {
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif',
    '.webp': 'image/webp',
    '.svg': 'image/svg+xml',
    '.ico': 'image/x-icon',
    '.bmp': 'image/bmp',
    '.apng': 'image/apng',
    '.avif': 'image/avif',
}

def get_bg_folder():
    custom_folder = gc("background folder", "")
    if custom_folder and os.path.isdir(custom_folder):
        return custom_folder
    return os.path.join(addon_path, "user_files", "background")

def get_bg_css_url(imgname):
    if not imgname:
        return ""
    custom_folder = gc("background folder", "")
    if custom_folder and os.path.isdir(custom_folder):
        filepath = os.path.join(custom_folder, imgname)
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                data = base64.b64encode(f.read()).decode('ascii')
            ext = os.path.splitext(imgname)[1].lower()
            mime = MIME_MAP.get(ext, 'image/png')
            return f"data:{mime};base64,{data}"
        return ""
    return f"/_addons/{addonfoldername}/user_files/background/{imgname}"

def add_bg_img(imgname, location, review=False):
    img_web_rel_path = get_bg_css_url(imgname)
    is_gif = imgname and imgname.lower().endswith('.gif')
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
        transform_css = "" if is_gif else f"\n    will-change: transform;\n    transform: scale({scale});"
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

def get_bg_img():
    bg_abs_path = get_bg_folder()
    os.makedirs(bg_abs_path, exist_ok=True)
    if bg_abs_path == os.path.join(addon_path, "user_files", "background"):
        if not os.listdir(bg_abs_path):
            shutil.copytree(src=os.path.join(addon_path, "user_files", "default_background"), dst=bg_abs_path, dirs_exist_ok=True)

    bgimg_list = [os.path.basename(f) for f in os.listdir(bg_abs_path) if f.lower().endswith(IMAGE_EXTS)]
    val = gc("Image name for background")
    if val and val.lower() == "random":
        return random.choice(bgimg_list)
    if val in bgimg_list:
        return val
    else:
        return ""


imgname = get_bg_img()
def reset_image(new_state, old_state):
    global imgname
    if new_state == "deckBrowser":
        imgname = get_bg_img()
gui_hooks.state_did_change.append(reset_image)

def adjust_deckbrowser_css():
    cont = add_bg_img(imgname, "body")
    #do not invert gears if using personal image
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

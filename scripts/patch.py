#!/usr/bin/env python3
"""Patch an apktool-decoded app: rename the launcher label and replace the launcher icon.
usage: patch.py <decoded_dir> <icons_dir> <new_name>
"""
import sys, os, re, glob, shutil
import xml.etree.ElementTree as ET

decoded, icons, NEW_NAME = sys.argv[1], sys.argv[2], sys.argv[3]
ANDROID = "http://schemas.android.com/apk/res/android"
A = lambda n: f"{{{ANDROID}}}{n}"
BG_HEX = "#FBE7E3"

manifest_path = os.path.join(decoded, "AndroidManifest.xml")
root = ET.parse(manifest_path).getroot()
app = root.find("application")

def is_launcher(el):
    for f in el.findall("intent-filter"):
        acts = [a.get(A("name")) for a in f.findall("action")]
        cats = [c.get(A("name")) for c in f.findall("category")]
        if "android.intent.action.MAIN" in acts and "android.intent.category.LAUNCHER" in cats:
            return True
    return False

launchers = [e for e in list(app.findall("activity")) + list(app.findall("activity-alias")) if is_launcher(e)]
targets = [app] + launchers
print("launcher components:", [e.get(A("name")) for e in launchers])

# ---- label
label_refs, literal_labels = set(), set()
for el in targets:
    v = el.get(A("label"))
    if v:
        (label_refs if v.startswith("@string/") else literal_labels).add(v)

values_files = glob.glob(os.path.join(decoded, "res", "values*", "*.xml"))
changed = 0
for ref in label_refs:
    name = ref.split("/", 1)[1]
    pat = re.compile(r'(<string\s+name="%s"[^>]*>)(.*?)(</string>)' % re.escape(name), re.S)
    for f in values_files:
        txt = open(f, encoding="utf-8").read()
        new, n = pat.subn(lambda m: m.group(1) + NEW_NAME + m.group(3), txt)
        if n:
            open(f, "w", encoding="utf-8").write(new)
            changed += n
print(f"label strings {sorted(label_refs)} -> '{NEW_NAME}' ({changed} replacements)")

if literal_labels:
    mtxt = open(manifest_path, encoding="utf-8").read()
    for lit in literal_labels:
        mtxt = mtxt.replace(f'android:label="{lit}"', f'android:label="{NEW_NAME}"')
    open(manifest_path, "w", encoding="utf-8").write(mtxt)
    print("literal labels replaced:", literal_labels)
if not label_refs and not literal_labels:
    print("WARNING: no label found on <application> or launcher activity")

# ---- icon
icon_refs = set()
for el in targets:
    for attr in ("icon", "roundIcon"):
        v = el.get(A(attr))
        if v and re.match(r"@(mipmap|drawable)/", v):
            icon_refs.add(v)
print("launcher icon resources:", sorted(icon_refs))
if not icon_refs:
    print("WARNING: no @mipmap/@drawable launcher icon found")

res = os.path.join(decoded, "res")
DENS = ("mdpi", "hdpi", "xhdpi", "xxhdpi", "xxxhdpi")
for ref in icon_refs:
    rtype, name = ref[1:].split("/", 1)
    for d in glob.glob(os.path.join(res, rtype + "*")):
        for f in glob.glob(os.path.join(d, name + ".*")):
            os.remove(f)
    for dens in DENS:
        out = os.path.join(res, f"{rtype}-{dens}")
        os.makedirs(out, exist_ok=True)
        shutil.copy(os.path.join(icons, f"mipmap-{dens}", "legacy.png"), os.path.join(out, name + ".png"))
    ad = os.path.join(res, f"{rtype}-anydpi-v26")
    os.makedirs(ad, exist_ok=True)
    open(os.path.join(ad, name + ".xml"), "w").write(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n'
        '    <background android:drawable="@color/yts_icon_bg"/>\n'
        '    <foreground android:drawable="@mipmap/yts_icon_fg"/>\n'
        '</adaptive-icon>\n')

if icon_refs:
    for dens in DENS:
        out = os.path.join(res, f"mipmap-{dens}")
        os.makedirs(out, exist_ok=True)
        shutil.copy(os.path.join(icons, f"mipmap-{dens}", "yts_icon_fg.png"), os.path.join(out, "yts_icon_fg.png"))
    os.makedirs(os.path.join(res, "values"), exist_ok=True)
    open(os.path.join(res, "values", "yts_colors.xml"), "w").write(
        f'<?xml version="1.0" encoding="utf-8"?>\n<resources>\n    <color name="yts_icon_bg">{BG_HEX}</color>\n</resources>\n')
print("done")

#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Export an allowlisted, sanitized desktop snapshot; never modify live files."""
import argparse
import configparser
import getpass
import hashlib
import io
import json
import re
import socket
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DIRECT_FILES = [
    ".config/kitty/kitty.conf", ".config/fish/config.fish",
    ".config/fastfetch/config.jsonc", ".config/btop/btop.conf",
    ".config/btop/themes/Cristal-Morado.theme",
    ".local/share/konsole/CristalOscuro.profile",
    ".local/share/konsole/CristalOscuro.colorscheme",
    ".local/share/konsole/CristalOscuroRedondeado.colorscheme",
    ".local/share/kwin/scripts/move-window-and-follow/metadata.json",
    ".local/share/kwin/scripts/move-window-and-follow/contents/code/main.js",
    ".var/app/dev.vencord.Vesktop/config/vesktop/settings/quickCss.css",
]
INI_FILES = [
    ".config/kdeglobals", ".config/kdedefaults/kdeglobals",
    ".config/kdedefaults/plasmarc", ".config/kwinrc", ".config/kwinrulesrc",
    ".config/kglobalshortcutsrc", ".config/plasmarc", ".config/plasmashellrc",
    ".config/plasma-org.kde.plasma.desktop-appletsrc", ".config/plasmanotifyrc",
    ".config/kscreenlockerrc", ".config/kcmfonts", ".config/kcminputrc",
    ".config/konsolerc", ".config/dolphinrc", ".config/gtk-3.0/settings.ini",
    ".config/gtk-4.0/settings.ini", ".config/Kvantum/kvantum.kvconfig",
    ".config/Kvantum/Sweet-Blur/Sweet-Blur.kvconfig", ".config/cava/config",
    ".config/local.desktop/WaywallenSelector.conf",
]
SHORTCUT_GROUPS = {
    "kwin", "kwin][$InverseAction", "plasmashell", "ksmserver", "kaccess",
    "KDE Keyboard Layout Switcher", "kcm_touchpad", "mediacontrol",
    "org_kde_powerdevil", "org.kde.krunner.desktop", "org.kde.plasma.emojier.desktop",
    "org.kde.konsole.desktop", "kitty.desktop", "org.kde.kscreen",
    "services][kitty.desktop", "services][org.kde.dolphin.desktop",
    "services][org.local.WaywallenSelector.desktop", "org.kde.dolphin.desktop",
    "org.local.WaywallenSelector.desktop",
}
PRIVATE_FIELDS = {
    "password", "passwd", "token", "accesstoken", "refreshtoken", "apikey",
    "clientsecret", "secret", "credentials", "cookie", "cookies", "sessionid",
    "latitude", "longitude", "locationname", "savedlocations", "activelocation",
    "countrycode", "altitude", "timezone", "selectedtimezones", "lastselectedtimezone", "targetkey", "lastwallpaper",
    "userproperties", "paireddevices", "paireddeviceid",
}
WEATHER_APPEARANCE = {
    "simpleFontAutoSz", "simpleIconAutoSz", "simplePanelDim", "simplePanelLargeDim",
}
SECRET_PATTERN = re.compile(
    r"-----BEGIN [^-]*PRIVATE KEY-----|github_pat_[A-Za-z0-9_]{20,}|"
    r"gh[pousr]_[A-Za-z0-9]{25,}|mfa\.[A-Za-z0-9_-]{30,}|"
    r"(?i:Bearer)\s+[A-Za-z0-9._-]{25,}"
)
HOME_PATTERN = re.compile(r"/home/[^/\s\"'<>]+")
PRIVATE_IP = re.compile(r"\b(?:192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})\b")
MAC_PATTERN = re.compile(r"\b(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}\b")


def compact(key):
    return re.sub(r"[^a-z0-9]", "", key.lower())


def private_key(key):
    word = compact(key)
    return word in PRIVATE_FIELDS or word.endswith(("apikey", "accesstoken", "refreshtoken", "password", "clientsecret"))


def parser():
    obj = configparser.ConfigParser(interpolation=None, strict=False)
    obj.optionxform = str
    return obj


class Exporter:
    def __init__(self, source, output):
        self.source = source.resolve()
        self.output = output.resolve()
        self.files = {}
        self.omitted = set()

    def normalize(self, text):
        # Config templates intentionally need rendering before being copied home.
        text = text.replace(str(self.source), "@HOME@")
        text = text.replace(getpass.getuser(), "@USER@")
        hostname = socket.gethostname()
        if hostname:
            text = re.sub(r"(?<![\w.-])" + re.escape(hostname) + r"(?![\w.-])", "@HOST@", text)
        text = PRIVATE_IP.sub("@PRIVATE_IP@", text)
        return MAC_PATTERN.sub("@MAC_ADDRESS@", text)

    def clean_value(self, value):
        if isinstance(value, dict):
            return {key: self.clean_value(item) for key, item in value.items() if not private_key(key)}
        if isinstance(value, list):
            return [self.clean_value(item) for item in value]
        if isinstance(value, str):
            return self.normalize(value)
        return value

    def add(self, relative, text, normalize=True):
        relative = Path(relative)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("Ruta de salida no permitida")
        result = self.normalize(text) if normalize else text
        if normalize:
            result = "\n".join(line.rstrip() for line in result.splitlines()).rstrip("\n") + "\n"
        if SECRET_PATTERN.search(result) or HOME_PATTERN.search(result):
            raise ValueError(f"Posibles datos sensibles: {relative}; exportación cancelada")
        self.files[str(relative)] = result

    def export_ini(self, name):
        path = self.source / name
        if not path.is_file():
            return
        original = parser()
        original.read(path, encoding="utf-8")
        result = parser()
        plugin_groups = {section: original[section].get("plugin", "") for section in original.sections() if "plugin" in original[section]}
        for section in original.sections():
            if name.endswith("kwinrc") and section.startswith("Tiling"):
                continue
            if name.endswith("kglobalshortcutsrc") and section not in SHORTCUT_GROUPS:
                continue
            if name.endswith("kcminputrc") and section != "Mouse":
                continue
            if name.endswith("WaywallenSelector.conf") and section != "appearance":
                continue
            if name.endswith("kdeglobals") and section in {"KScreen", "PreviewSettings"}:
                continue
            if name.endswith("plasmashellrc") and not section.startswith("PlasmaViews"):
                continue
            is_panel = name.endswith("plasma-org.kde.plasma.desktop-appletsrc")
            if is_panel and not section.startswith(("Containments][", "ActionPlugins", "ScreenMapping")):
                continue
            if is_panel and section.startswith("ScreenMapping"):
                continue
            owner = ""
            if is_panel:
                for parent in sorted(plugin_groups, key=len, reverse=True):
                    if section == parent or section.startswith(parent + "]["):
                        owner = plugin_groups[parent]
                        break
            values = {}
            for key, value in original[section].items():
                low = compact(key)
                if private_key(key) or low in {"recentfiles", "recenturls", "lastvisited", "history", "recentdocuments"}:
                    self.omitted.add("sensitive-or-local-fields")
                    continue
                if "weather" in owner and section != next((s for s in plugin_groups if s == section), ""):
                    if key not in WEATHER_APPEARANCE:
                        self.omitted.add("weather-location-and-state")
                        continue
                if low.startswith(("notification", "itemgeometries")) or low in {"positions", "previews", "activityid"}:
                    continue
                if key == "customGreeting":
                    value = "Hola"
                elif key == "customButtonImage":
                    value = "file://@HOME@/Pictures/panel-logo.png"
                elif key in {"Image", "PreviewImage"} and "Wallpaper" in section:
                    value = "file://@HOME@/Pictures/wallpaper.jpg"
                elif key == "SlidePaths":
                    value = "@HOME@/Pictures/wallpapers/"
                else:
                    try:
                        parsed = json.loads(value)
                    except (ValueError, TypeError):
                        parsed = None
                    if isinstance(parsed, (dict, list)):
                        value = json.dumps(self.clean_value(parsed), ensure_ascii=False, separators=(",", ":"))
                values[key] = self.normalize(value)
            if values:
                result[section] = values
        stream = io.StringIO()
        result.write(stream, space_around_delimiters=False)
        self.add("home/" + name, stream.getvalue())

    def export_waywallen(self):
        import tomllib
        path = self.source / ".var/app/org.waywallen.waywallen/config/waywallen/config.toml"
        if not path.is_file():
            return
        data = tomllib.loads(path.read_text())
        lines = []
        allowed_global = {
            "queue_mode", "rotation_secs", "audio_fade_ms", "mute_when_other_audio",
            "audio_capture_enabled", "manual_muted", "duplicate_renderers_for_same_wallpaper",
            "pointer_forwarding_enabled", "plugin_update_notifications", "autostart_enabled",
            "hide_tray_icon", "debug_logging_enabled", "renderer", "layout", "auto_replay",
            "pause_effect", "transition",
        }

        def table(section, fields):
            lines.append("[" + section + "]")
            for key, value in fields.items():
                if isinstance(value, dict) or private_key(key):
                    continue
                if key == "window_exclusions":
                    continue
                if isinstance(value, (str, int, float, bool)):
                    lines.append(key + " = " + json.dumps(value, ensure_ascii=False))
            lines.append("")
            for key, value in fields.items():
                if isinstance(value, dict) and key != "window_exclusions":
                    table(section + "." + key, value)

        table("global", {k: v for k, v in data.get("global", {}).items() if k in allowed_global})
        for name in ["waywallen-video", "waywallen-image", "wescene-renderer", "weweb-renderer"]:
            if name in data.get("plugin", {}):
                table("plugin." + name, data["plugin"][name])
        self.add("snippets/waywallen/config.appearance.toml", "\n".join(lines))

    def export_vesktop(self):
        base = self.source / ".var/app/dev.vencord.Vesktop/config/vesktop"
        selections = {
            "settings.json": ["nativeTitleBar", "enableShadow", "enableRoundedCorners", "splashTheming", "transparencyOption"],
            "settings/settings.json": ["transparent", "useQuickCss", "frameless"],
        }
        for name, keys in selections.items():
            path = base / name
            if path.is_file():
                data = json.loads(path.read_text())
                selected = {k: data[k] for k in keys if k in data}
                output = "vesktop-appearance.json" if name == "settings.json" else "vencord-appearance.json"
                self.add("snippets/vesktop/" + output, json.dumps(selected, indent=2) + "\n")

    def collect(self):
        for name in DIRECT_FILES:
            source = self.source / name
            if source.is_file():
                self.add("home/" + name, source.read_text())
        for name in INI_FILES:
            self.export_ini(name)
        self.export_waywallen()
        self.export_vesktop()
        root = self.source / ".local/share/plasma/plasmoids/AndromedaLauncher"
        override = root / "contents/ui/MenuRepresentation.qml"
        if override.is_file() and (root / "LICENSE").is_file():
            self.add("home/.local/share/plasma/plasmoids/AndromedaLauncher/contents/ui/MenuRepresentation.qml", override.read_text())
            self.add("third_party/AndromedaLauncher-LICENSE", (root / "LICENSE").read_text(), normalize=False)
        desktop_keys = {"Type", "Name", "Comment", "Exec", "Icon", "Terminal", "StartupNotify", "StartupWMClass", "X-KDE-Shortcuts"}
        for base in [".local/share/applications", ".local/share/kglobalaccel"]:
            for name in ["org.kde.dolphin.desktop", "org.local.WaywallenSelector.desktop"]:
                source = self.source / base / name
                if source.is_file():
                    original = parser()
                    original.read(source)
                    result = parser()
                    result["Desktop Entry"] = {k: v for k, v in original["Desktop Entry"].items() if k in desktop_keys}
                    stream = io.StringIO()
                    result.write(stream, space_around_delimiters=False)
                    self.add("home/" + base + "/" + name, stream.getvalue())

    def write(self):
        # Validate the entire plan before writing anything. Existing files are
        # never overwritten with different content; export to a fresh directory.
        for name, text in self.files.items():
            target = self.output / name
            if target.exists() and target.read_text() != text:
                raise ValueError(f"Ya existe un archivo diferente: {name}; usa otra salida")
        for name, text in self.files.items():
            target = self.output / name
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                target.write_text(text)
        manifest = {"files": {name: hashlib.sha256(text.encode()).hexdigest() for name, text in sorted(self.files.items())},
                    "omitted_categories": sorted(self.omitted), "templates": ["@HOME@", "@USER@", "@HOST@"]}
        target = self.output / "manifest.json"
        target.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--source-home", type=Path, default=Path.home())
    cli.add_argument("--output", type=Path, required=True)
    args = cli.parse_args()
    source, output = args.source_home.expanduser().resolve(), args.output.expanduser().resolve()
    protected = [source / name for name in [".config", ".local", ".var", ".ssh", ".gnupg"]]
    if output == source or any(output == path or output.is_relative_to(path) for path in protected):
        raise SystemExit("La salida no puede ser una configuración activa")
    export = Exporter(source, output)
    export.collect()
    export.write()
    print(f"Exportados {len(export.files)} archivos revisados; no se modificó la configuración activa.")


if __name__ == "__main__":
    main()

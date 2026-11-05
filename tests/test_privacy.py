# SPDX-License-Identifier: GPL-3.0-only
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("snapshot", ROOT / "scripts/export_snapshot.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PrivacyTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)
        self.source = self.base / "source"
        self.output = self.base / "output"
        self.source.mkdir()

    def tearDown(self):
        self.temporary.cleanup()

    def put(self, relative, text):
        path = self.source / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def test_weather_location_removed_but_layout_retained(self):
        source = self.put(".config/plasma-org.kde.plasma.desktop-appletsrc", """[Containments][1]
plugin=org.kde.panel
location=3
[Containments][1][Applets][2]
plugin=org.kde.plasma.advanced-weather-widget
[Containments][1][Applets][2][Configuration][General]
latitude=TEST_LATITUDE
longitude=TEST_LONGITUDE
locationName=PRIVATE_LOCATION
savedLocations=PRIVATE_SAVED_LOCATION
simplePanelDim=120
""")
        original = source.read_bytes()
        export = module.Exporter(self.source, self.output)
        export.collect()
        export.write()
        text = (self.output / "home/.config/plasma-org.kde.plasma.desktop-appletsrc").read_text()
        for secret in ["TEST_LATITUDE", "TEST_LONGITUDE", "PRIVATE_LOCATION", "PRIVATE_SAVED_LOCATION"]:
            self.assertNotIn(secret, text)
        self.assertIn("location=3", text)
        self.assertIn("simplePanelDim=120", text)
        self.assertEqual(source.read_bytes(), original)

    def test_vesktop_does_not_export_tokens_accounts_or_plugins(self):
        self.put(".var/app/dev.vencord.Vesktop/config/vesktop/settings/settings.json", json.dumps({
            "transparent": True, "useQuickCss": True, "frameless": False,
            "account": "PRIVATE_ACCOUNT", "token": "PRIVATE_TOKEN", "plugins": {"private": True},
        }))
        export = module.Exporter(self.source, self.output)
        export.collect()
        export.write()
        data = json.loads((self.output / "snippets/vesktop/vencord-appearance.json").read_text())
        self.assertEqual(set(data), {"transparent", "useQuickCss", "frameless"})

    def test_nested_api_keys_removed(self):
        export = module.Exporter(self.source, self.output)
        value = export.clean_value({"color": "#c061ff", "nested": {"apiKey": "PRIVATE_KEY", "latitude": "PRIVATE_LATITUDE", "radius": 18}})
        self.assertEqual(value, {"color": "#c061ff", "nested": {"radius": 18}})

    def test_home_and_private_network_addresses_are_templates(self):
        export = module.Exporter(self.source, self.output)
        text = export.normalize(str(self.source) + "/Pictures 192.168.99.13 aa:bb:cc:dd:ee:ff")
        self.assertEqual(text, "@HOME@/Pictures @PRIVATE_IP@ @MAC_ADDRESS@")

    def test_token_in_plain_config_aborts_without_writing(self):
        self.put(".config/fish/config.fish", "set -x GITHUB_TOKEN " + "gh" + "p_" + "A" * 40)
        export = module.Exporter(self.source, self.output)
        with self.assertRaises(ValueError):
            export.collect()
        self.assertFalse(self.output.exists())

    def test_existing_different_file_is_not_overwritten(self):
        self.put(".config/kitty/kitty.conf", "font_size 10\n")
        target = self.output / "home/.config/kitty/kitty.conf"
        target.parent.mkdir(parents=True)
        target.write_text("USER_WORK\n")
        export = module.Exporter(self.source, self.output)
        export.collect()
        with self.assertRaises(ValueError):
            export.write()
        self.assertEqual(target.read_text(), "USER_WORK\n")


if __name__ == "__main__":
    unittest.main()

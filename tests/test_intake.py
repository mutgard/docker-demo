import json
import sys
import tempfile
import unittest
from pathlib import Path

# Allow importing from scripts/
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


class TestLoadScenarios(unittest.TestCase):
    def test_returns_empty_list_when_dir_missing(self):
        import dashboard
        original_root = dashboard.ROOT
        dashboard.ROOT = Path("/tmp/nonexistent-atelier-xyz")
        try:
            result = dashboard.load_scenarios()
            self.assertEqual(result, [])
        finally:
            dashboard.ROOT = original_root

    def test_loads_scenario_files(self):
        import dashboard
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sc_dir = root / "demo-scenarios"
            sc_dir.mkdir()
            (sc_dir / "test-scenario.json").write_text(json.dumps({
                "id": "test-scenario",
                "label": "Test Scenario",
                "client_slug": "test-client",
                "messages": [],
                "brief": {"nombre": "Test"}
            }))
            original_root = dashboard.ROOT
            dashboard.ROOT = root
            try:
                result = dashboard.load_scenarios()
                self.assertEqual(len(result), 1)
                self.assertEqual(result[0]["id"], "test-scenario")
                self.assertEqual(result[0]["label"], "Test Scenario")
            finally:
                dashboard.ROOT = original_root

    def test_skips_invalid_json(self):
        import dashboard
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sc_dir = root / "demo-scenarios"
            sc_dir.mkdir()
            (sc_dir / "bad.json").write_text("not valid json{{{")
            (sc_dir / "good.json").write_text(json.dumps({"id": "good", "label": "Good"}))
            original_root = dashboard.ROOT
            dashboard.ROOT = root
            try:
                result = dashboard.load_scenarios()
                self.assertEqual(len(result), 1)
                self.assertEqual(result[0]["id"], "good")
            finally:
                dashboard.ROOT = original_root


class TestCreateClientFiles(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "clients").mkdir()
        (self.root / "clients" / "_index.md").write_text(
            "# Clients\n\n## Leads (No order yet)\n\n"
            "| Name | First contact | Source | Follow-up due |\n"
            "|------|---------------|--------|---------------|\n"
            "| [Existing](existing/profile.md) | 2026-01-01 | — | — |\n\n"
            "---\n*Last updated: 2026-01-01*\n"
        )

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, scenario):
        import dashboard
        original_root = dashboard.ROOT
        dashboard.ROOT = self.root
        try:
            return dashboard.create_client_files(scenario)
        finally:
            dashboard.ROOT = original_root

    def test_creates_profile_md(self):
        scenario = {
            "client_slug": "test-bride",
            "messages": [{"from": "client", "text": "Hola", "time": "10:00"}],
            "brief": {
                "nombre": "Test Bride",
                "boda": "20 junio 2026",
                "lugar": "Barcelona",
                "estilo": "Boho",
                "silueta": "Corte A",
                "tejido": "Gasa",
                "color": "Blanco",
                "presupuesto": "€2.000",
                "alertas": []
            }
        }
        self._run(scenario)
        profile = self.root / "clients" / "test-bride" / "profile.md"
        self.assertTrue(profile.exists())
        content = profile.read_text()
        self.assertIn("# Client: Test Bride", content)
        self.assertIn("€2.000", content)
        self.assertIn("20 junio 2026", content)

    def test_creates_comms_log(self):
        scenario = {
            "client_slug": "test-bride-2",
            "messages": [{"from": "client", "text": "Hola", "time": "10:00"}],
            "brief": {"nombre": "Test", "boda": "", "lugar": "", "estilo": "",
                      "silueta": "", "tejido": "", "color": "", "presupuesto": "", "alertas": []}
        }
        self._run(scenario)
        comms_dir = self.root / "clients" / "test-bride-2" / "comms"
        logs = list(comms_dir.glob("*.md"))
        self.assertEqual(len(logs), 1)
        content = logs[0].read_text()
        self.assertIn("whatsapp", content)
        self.assertIn("Hola", content)

    def test_updates_index(self):
        scenario = {
            "client_slug": "new-client",
            "messages": [],
            "brief": {"nombre": "New Client", "boda": "2026-09-05",
                      "lugar": "", "estilo": "", "silueta": "", "tejido": "",
                      "color": "", "presupuesto": "", "alertas": []}
        }
        self._run(scenario)
        index = (self.root / "clients" / "_index.md").read_text()
        self.assertIn("new-client", index)
        self.assertIn("New Client", index)

    def test_idempotent_on_second_call(self):
        scenario = {
            "client_slug": "idempotent-client",
            "messages": [],
            "brief": {"nombre": "Same Client", "boda": "", "lugar": "",
                      "estilo": "", "silueta": "", "tejido": "", "color": "",
                      "presupuesto": "", "alertas": []}
        }
        self._run(scenario)
        self._run(scenario)  # second call should not duplicate
        index = (self.root / "clients" / "_index.md").read_text()
        self.assertEqual(index.count("idempotent-client"), 1)


if __name__ == "__main__":
    unittest.main()

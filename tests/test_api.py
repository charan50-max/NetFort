import unittest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.scenarios import get_scenario_packets, SCENARIOS


class TestBackendAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["packets_per_scenario"], 100)

    def test_scenarios_have_100_packets(self):
        response = self.client.get("/api/scenarios")
        self.assertEqual(response.status_code, 200)
        scenarios = response.json()
        self.assertGreaterEqual(len(scenarios), 3)
        for s in scenarios:
            self.assertEqual(s["packet_count"], 100)

        # Test packets generation
        pkts = get_scenario_packets("enterprise_100")
        self.assertEqual(len(pkts), 100)
        self.assertEqual(pkts[0].packet_id, "PKT-001")
        self.assertEqual(pkts[99].packet_id, "PKT-100")
        # Ensure raw format works for double-click inspection
        self.assertTrue(len(pkts[0].to_raw_format()) > 20)

    def test_rules_crud_and_presets(self):
        # Read rules
        resp = self.client.get("/api/rules")
        self.assertEqual(resp.status_code, 200)
        rules = resp.json()
        self.assertGreaterEqual(len(rules), 3)

        # Apply preset
        resp = self.client.post("/api/rules/presets/strict")
        self.assertEqual(resp.status_code, 200)

        # Reset rules
        resp = self.client.post("/api/rules/reset")
        self.assertEqual(resp.status_code, 200)

    def test_simulation_workflow(self):
        # Create simulation with 100 packets
        resp = self.client.post("/api/simulations", json={
            "scenario_id": "enterprise_100",
            "model_type": "stateful"
        })
        self.assertEqual(resp.status_code, 200)
        sim = resp.json()
        run_id = sim["run_id"]
        self.assertEqual(sim["total_packets"], 100)
        self.assertEqual(sim["processed_packets"], 0)

        # Step 5 packets
        step_resp = self.client.post(f"/api/simulations/{run_id}/step?batch_size=5")
        self.assertEqual(step_resp.status_code, 200)
        step_data = step_resp.json()
        self.assertEqual(step_data["processed_packets"], 5)
        self.assertIsNotNone(step_data["step_result"])
        # Check raw packet information exists for double click inspection
        self.assertIn("raw_format", step_data["step_result"]["packet"])

        # Step remaining 95 packets
        step_resp = self.client.post(f"/api/simulations/{run_id}/step?batch_size=95")
        self.assertEqual(step_resp.status_code, 200)
        step_data = step_resp.json()
        self.assertEqual(step_data["processed_packets"], 100)
        self.assertTrue(step_data["finished"])

        # Check packet log
        pkts_resp = self.client.get(f"/api/simulations/{run_id}/packets?page=1&limit=10")
        self.assertEqual(pkts_resp.status_code, 200)
        pkts_data = pkts_resp.json()
        self.assertEqual(pkts_data["total"], 100)
        self.assertEqual(len(pkts_data["packets"]), 10)

    def test_comparison_100_packets(self):
        resp = self.client.post("/api/comparisons?scenario_id=enterprise_100")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["total_packets"], 100)
        self.assertEqual(len(data["results"]), 100)
        # Verify genuine differences between stateful and stateless
        self.assertGreater(data["diff_count"], 0)
        self.assertGreater(data["same_count"], 0)
        self.assertGreater(data["stateful_allowed"], data["stateless_allowed"])

        # Check metrics endpoint
        comp_id = data["comparison_id"]
        m_resp = self.client.get(f"/api/metrics/{comp_id}")
        self.assertEqual(m_resp.status_code, 200)
        m_data = m_resp.json()
        self.assertTrue(m_data["is_comparison"])
        self.assertGreater(m_data["comparison_metrics"]["disagreement_rate"], 0)


if __name__ == "__main__":
    unittest.main()

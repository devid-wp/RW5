import datetime as dt
import sys
import unittest
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from schedule import load, status, validate


class ScheduleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = load(ROOT / "schedule.json")

    def at(self, day, hour, minute):
        return status(self.config, dt.datetime(2026, 11, day, hour, minute, tzinfo=ZoneInfo("Europe/Kyiv")))

    def test_before(self):
        self.assertEqual((self.at(2, 8, 0)["state"], self.at(2, 8, 0)["remaining_minutes"]), ("before", 60))

    def test_lesson_and_boundary(self):
        self.assertEqual(self.at(2, 9, 0)["state"], "lesson")
        self.assertEqual(self.at(2, 9, 44)["remaining_minutes"], 1)

    def test_break_and_next(self):
        x = self.at(2, 9, 45)
        self.assertEqual((x["state"], x["remaining_minutes"], x["next"]["subject"]), ("break", 10, "History"))

    def test_after(self):
        self.assertEqual(self.at(2, 15, 40)["state"], "after")

    def test_rotation(self):
        for day, subject in ((5, "World Literature"), (12, "Algebra"),
                             (19, "World Literature"), (26, "Algebra")):
            self.assertEqual(self.at(day, 12, 0)["current"]["subject"], subject)

    def test_progress(self):
        self.assertEqual(self.at(2, 9, 50)["progress"], 0.5)
        self.assertEqual(self.at(2, 9, 55)["progress"], 0)
        self.assertEqual(self.at(4, 16, 34)["current"]["number"], 8)
        self.assertEqual(self.at(4, 16, 35)["state"], "after")

    def test_weekend(self):
        self.assertEqual(self.at(7, 12, 0)["state"], "weekend")

    def test_overlap_rejected(self):
        config = load(ROOT / "schedule.json")
        config["days"]["monday"][1]["start"] = "09:00"
        with self.assertRaises(ValueError):
            validate(config)


if __name__ == "__main__":
    unittest.main()


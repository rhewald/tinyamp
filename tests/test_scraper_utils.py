import unittest
from scrapers.scraper_utils import normalize_date

class TestNormalizeDate(unittest.TestCase):
    def test_valid_dates(self):
        self.assertEqual(normalize_date("5.1"), "2025-05-01")
        self.assertEqual(normalize_date("12.31"), "2025-12-31")
        self.assertEqual(normalize_date("1.9"), "2025-01-09")
        self.assertEqual(normalize_date(" 6.7 "), "2025-06-07")

    def test_invalid_dates(self):
        self.assertIsNone(normalize_date("bad"))
        self.assertIsNone(normalize_date("13.1"))  # invalid month
        self.assertIsNone(normalize_date("2.30"))  # invalid day
        self.assertIsNone(normalize_date(""))

if __name__ == "__main__":
    unittest.main()

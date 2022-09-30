import unittest
import ontario_school_scraper

class TestOntarioSchoolScraper(unittest.TestCase):
    def test_get_schools(self):
        elementary_url = "https://www.app.edu.gov.on.ca/eng/sift/index.asp"
        secondary_url = "https://www.app.edu.gov.on.ca/eng/sift/indexSec.asp"

        # School IDs list should be non-empty
        self.assertTrue(ontario_school_scraper.get_schools(elementary_url))
        self.assertTrue(ontario_school_scraper.get_schools(secondary_url))

    def test_get_school_data(self):
        self.assertTrue(ontario_school_scraper.get_school_data(890170))
        self.assertTrue(ontario_school_scraper.get_school_data(685186))

if __name__ == '__main__':
    unittest.main()

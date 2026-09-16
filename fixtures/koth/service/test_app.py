import unittest
from urllib.parse import quote


class ServicePolicyTest(unittest.TestCase):
    def test_markup_is_encoded(self):
        value = "<script>fixture</script>"
        self.assertNotIn("<script>", quote(value))


if __name__ == "__main__":
    unittest.main()

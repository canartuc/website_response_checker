import unittest
from unittest.mock import patch
from main import chunk_websites, monitor_websites_chunk
from validator import Website


class TestMainModule(unittest.TestCase):

    def setUp(self):
        # Setup mock data
        self.websites = [
            Website("https://google.com", 10, None),
            Website("https://bing.com", 15, "Ask"),
        ]

    def test_chunk_websites(self):
        # Test if websites are correctly chunked.
        chunks = list(chunk_websites(self.websites, 1))
        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0][0].url, "https://google.com")
        self.assertEqual(chunks[1][0].url, "https://bing.com")

    @patch('main.monitor_website_continuous')
    def test_monitor_websites_chunk(self, mock_monitor_website_continuous):
        # Test if separate threads are started for each website in a chunk.
        monitor_websites_chunk(self.websites)
        self.assertEqual(mock_monitor_website_continuous.call_count, 2)


if __name__ == '__main__':
    unittest.main()

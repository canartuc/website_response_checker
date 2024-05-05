import unittest
from unittest.mock import patch, MagicMock
from database import DatabaseManager


class TestDatabaseManager(unittest.TestCase):
    @patch('psycopg2.connect')
    def test_init(self, mock_connect):
        db_manager = DatabaseManager(dbname='test_db', user='test_user', password='test_pass', host='localhost',
                                     port=5432)
        mock_connect.assert_called_once_with(dbname='test_db', user='test_user', password='test_pass', host='localhost',
                                             port=5432)

    @patch('psycopg2.connect')
    def test_context_manager(self, mock_connect):
        with DatabaseManager() as db_manager:
            self.assertIsNotNone(db_manager)
        mock_connect.return_value.close.assert_called_once()

    @patch('psycopg2.connect')
    def test_upsert_website(self, mock_connect):
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [1]

        with DatabaseManager() as db_manager:
            web_id = db_manager.upsert_website('https://example.com')
            self.assertEqual(web_id, 1)

    @patch('psycopg2.connect')
    def test_stream_insert_result(self, mock_connect):
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [1]

        with DatabaseManager() as db_manager:
            logs = [("https://example.com", 0.5, 200, "content", 1234567890, "log details")]
            db_manager.stream_insert_result(logs)
            mock_cursor.copy_expert.assert_called_once()


if __name__ == '__main__':
    unittest.main()

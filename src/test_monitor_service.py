import unittest
from unittest.mock import patch, MagicMock
from monitor_service import monitor_url
from http import HTTPStatus
import requests


class TestMonitorService(unittest.TestCase):

    @patch('monitor_service.DatabaseManager')
    @patch('monitor_service.check_content_and_extract', return_value=(True, 'Matched Content'))
    @patch('monitor_service.requests.get')
    def test_monitor_url_success_with_match(self, mock_get, mock_check, mock_db):
        # Setup mock response for requests.get
        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.elapsed.total_seconds.return_value = 0.5
        mock_response.text = 'Data Engineer'
        mock_get.return_value = mock_response

        # Execute the function under test
        monitor_url("https://canartuc.com", r"Data")

        # Assertions
        mock_get.assert_called_once_with("https://canartuc.com", timeout=10)
        mock_check.assert_called_once_with('Data Engineer', r"Data")
        mock_db.return_value.stream_insert_result.assert_called()

    @patch('monitor_service.DatabaseManager')
    @patch('monitor_service.check_content_and_extract', return_value=(False, None))
    @patch('monitor_service.requests.get', side_effect=requests.exceptions.Timeout)
    def test_monitor_url_timeout(self, mock_get, mock_check, mock_db):
        monitor_url("http://tirafikimirafiki.com/", None)

        mock_get.assert_called_once_with("http://tirafikimirafiki.com/", timeout=10)
        mock_check.assert_not_called()
        mock_db.return_value.stream_insert_result.assert_called_once()


if __name__ == '__main__':
    unittest.main()

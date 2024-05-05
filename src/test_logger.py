import unittest
from unittest.mock import patch
from logger import setup_logger, log_function_call


class TestLogger(unittest.TestCase):

    def test_log_function_call(self):
        # Setup a test logger
        logger = setup_logger('test_logger', 'test_logger.log')

        with patch.object(logger, 'info') as mock_info, patch.object(logger, 'exception') as mock_exception:
            @log_function_call(logger=logger)
            def sample_function(param):
                return f"Result is {param}"

            # Call the decorated function
            result = sample_function(42)
            self.assertEqual(result, "Result is 42")
            mock_info.assert_any_call("Entering: sample_function")
            mock_info.assert_any_call("Exiting: sample_function")

            # Test exception logging
            @log_function_call(logger=logger)
            def sample_function_exception():
                raise ValueError("Test exception")

            # Ensure exception is logged and re-raised
            with self.assertRaises(ValueError):
                sample_function_exception()

            mock_exception.assert_called_once_with("Error in sample_function_exception: Test exception")


if __name__ == '__main__':
    unittest.main()

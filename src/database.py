"""
This module provides a DatabaseManager class for managing database operations in the application.

Example usage:
    # Create a DatabaseManager instance
    db_manager = DatabaseManager()

    # Upsert a website into the database
    website_id = db_manager.upsert_website("https://example.com")

    # Stream insert a batch of logs into the database
    logs = [("https://example.com", 0.5, 200, "content", 1234567890, "log details")]
    db_manager.stream_insert_result(logs)
"""

import psycopg2
import os
from typing import List, Tuple, Optional
from logger import log_function_call, setup_logger
import io

db_logger = setup_logger('db_operations', 'db_operations.log')


class DatabaseManager:
    """
    The DatabaseManager class is responsible for managing the database operations in the application.
    It provides methods to connect to the database, insert or update website data, and stream insert logs.

    Attributes:
        dbname (str): The name of the database.
        user (str): The database user.
        password (str): The database password.
        host (str): The database host.
        port (int): The database port.
        logger (Logger): A logger for database operations.
        conn (psycopg2.extensions.connection): The database connection object.
    """

    def __init__(self, dbname: Optional[str] = None, user: Optional[str] = None,
                 password: Optional[str] = None, host: Optional[str] = None,
                 port: Optional[int] = None):
        """
        Initializes a DatabaseManager object.

        Args:
            dbname (str, optional): The name of the database.
                If not provided, it will be fetched from the environment variable "POSTGRES_DB".
                Defaults to None.
            user (str, optional): The username for the database connection.
                If not provided, it will be fetched from the environment variable "POSTGRES_USR".
                Defaults to None.
            password (str, optional): The password for the database connection.
                If not provided, it will be fetched from the environment variable "POSTGRES_PASS".
                Defaults to None.
            host (str, optional): The host address for the database connection.
                If not provided, it will be fetched from the environment variable "POSTGRES_HOST".
                Defaults to None.
            port (int, optional): The port number for the database connection.
                If not provided, it will be fetched from the environment variable "POSTGRES_PORT".
                Defaults to None.
        """
        self.dbname = dbname if dbname is not None else os.getenv("POSTGRES_DB")
        self.user = user if user is not None else os.getenv("POSTGRES_USR")
        self.password = password if password is not None else os.getenv("POSTGRES_PASS")
        self.host = host if host is not None else os.getenv("POSTGRES_HOST")
        self.port = port if port is not None else os.getenv("POSTGRES_PORT")

        self.logger = setup_logger('db_operations', 'db_operations.log')

        self.conn = psycopg2.connect(dbname=self.dbname, user=self.user, password=self.password,
                                     host=self.host, port=self.port)

    def __enter__(self):
        """
        Context manager entry point.

        Returns:
            DatabaseManager: The current instance of the DatabaseManager class.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Ensures the database connection is closed when exiting the context manager scope.
        """
        self.conn.close()

    @log_function_call(logger=db_logger)
    def upsert_website(self, url: str) -> int:
        """
        Upserts a website into the database.

        Args:
            url (str): The URL of the website to be upserted.

        Returns:
            int: The ID of the upserted website.
        """
        with self.conn.cursor() as cursor:
            insert_sql = (f"INSERT INTO t_website (web_url) VALUES ('{url}') "
                          f"ON CONFLICT (web_url) DO UPDATE SET web_url = EXCLUDED.web_url RETURNING web_id;")
            cursor.execute(insert_sql)
            web_id = cursor.fetchone()[0]
            self.conn.commit()
            return web_id

    def stream_insert_result(self, results: List[Tuple[str, float, int, Optional[str], int, str]],
                             chunk_size: int = 1000) -> None:
        """
        Streams and inserts the given results into the database.

        Args:
            results (List[Tuple[str, float, int, Optional[str], int, str]]): A list of tuples representing the results
                to be inserted. Each tuple should contain the following values:
                - url (str): The URL of the website.
                - response_time (float): The response time in seconds.
                - status_code (int): The HTTP status code.
                - matched_content (Optional[str]): The matched content, if any.
                - timestamp_data (int): The epoch timestamp data.
                - detail_log (str): The detail log.

            chunk_size (int, optional): The number of results to process in each chunk. Defaults to 1000.

        Raises:
            Exception: If an error occurs during the streaming insert.
            psycopg2.DatabaseError: If a database error occurs during the streaming insert.

        """
        try:
            modified_results = []
            for result in results:
                url, response_time, status_code, matched_content, timestamp_data, detail_log = result
                web_id = self.upsert_website(url)
                
                # Ensure matched_content is a string or None for consistent handling
                matched_content_str = matched_content if matched_content is not None else ''
                
                # Escape double quotes by doubling them
                matched_content_escaped = matched_content_str.replace('"', '""')
                modified_results.append((web_id, status_code, response_time, matched_content_escaped,
                                         timestamp_data, detail_log))

            with self.conn.cursor() as cursor:
                for i in range(0, len(modified_results), chunk_size):
                    chunk = modified_results[i:i + chunk_size]
                    csv_data = io.StringIO()
                    
                    # Properly format each log entry as a CSV line - We are doing this because streaming insert
                    # to Postgres work with CSV stdin in the following query. We need to build CSV either in memory
                    # with io.String or pysical CSV file directly
                    for log_entry in chunk:
                        # Convert each value to string, escape double quotes in strings
                        csv_line = ','.join(
                            f'"{value}"' if isinstance(value, str) else str(value) for value in log_entry)
                        csv_data.write(csv_line + "\n")
                    csv_data.seek(0)
                    cursor.copy_expert(
                        "COPY t_monitor (web_id, status_code, response_time, matched_content, check_ts, detail_log) "
                        "FROM STDIN WITH CSV NULL ''", csv_data)
                self.conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            self.logger.exception("Error in streaming insert logs: %s", error)
            raise

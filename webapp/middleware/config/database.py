from typing import Optional
from config.logging import logger
from config.settings import settings
import pyodbc
import time


class DatabaseConnection:
    def __init__(self):
        """
        Initializes the database connection class using a predefined connection string.
        """
        self.connection_string = (
            "Driver={ODBC Driver 18 for SQL Server};"
            f"Server=tcp:{settings.DB_SERVER},1433;"
            f"Database={settings.DB_NAME};"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
            "Connection Timeout=120;"
            "Authentication=ActiveDirectoryServicePrincipal;"
            f"UID={settings.CLIENT_ID};"
            f"PWD={settings.CLIENT_SECRET};"
        )
        self.connection: Optional[pyodbc.Connection] = None
        self._retries = 3
        self._retry_delay = 5

    def _attempt_connection(self) -> pyodbc.Connection:
        """
        Tries to establish a database connection with retry logic.
        """
        for attempt in range(1, self._retries + 1):
            try:
                logger.info(f"[Attempt {attempt}] Connecting to database...")
                conn = pyodbc.connect(self.connection_string, autocommit=True)
                logger.info("Database connection established successfully.")
                return conn
            except pyodbc.Error as e:
                logger.error(f"Connection attempt {attempt} failed: {e}")
                if attempt < self._retries:
                    logger.info(f"Retrying in {self._retry_delay} seconds...")
                    time.sleep(self._retry_delay)
                else:
                    logger.critical("Max retry attempts exceeded.")
                    raise Exception(f"Database connection failed: {str(e)}")

    def get_connection(self) -> pyodbc.Connection:
        """
        Always returns a new connection (stateless pattern).
        """
        return self._attempt_connection()

    def close_connection(self) -> None:
        """
        Closes the current stored connection, if any.
        """
        if self.connection:
            try:
                self.connection.close()
                logger.info("Database connection closed.")
            except pyodbc.Error as e:
                logger.error(f"Error closing connection: {e}")
            finally:
                self.connection = None

    def __del__(self):
        """
        Destructor to clean up any lingering connection.
        """
        if self.connection and not self.connection.closed:
            self.close_connection()


database_connection = DatabaseConnection()


def get_db_connection() -> pyodbc.Connection:
    """
    Function to retrieve a fresh database connection.
    """
    try:
        return database_connection.get_connection()
    except Exception as e:
        logger.error(f"Unable to connect to DB: {e}")
        raise

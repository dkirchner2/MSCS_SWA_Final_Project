from collector import db_handler
import unittest
from unittest.mock import patch, MagicMock
import sqlite3
import os

class TestDbHandler(unittest.TestCase):

    # -------------- COMMON TEST FUNCTIONS ------------------

    def setUp(self):
        # Create an in-memory database for testing
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.conn = sqlite3.connect(":memory:")
        self.cursor = self.conn.cursor()
        self.dbpath = os.path.join(self.BASE_DIR, 'fake_data.db')


    def tearDown(self):
        self.conn.close()

    # ------------ INITIALIZE_DB() TESTS -----------

    @patch('collector.db_handler.get_db_connection')
    @patch('collector.db_handler.Path')
    def test_initialize_db_initialized(self, mock_path, mock_connection):
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        mock_path_instance.is_file.return_value = True
        mock_connection.return_value = (self.conn, self.cursor)

        result = db_handler.initialize_db(self.dbpath)
        self.assertTrue(result)
        mock_connection.assert_not_called()
        table_exists = self.cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='Locations'").fetchone()
        self.assertFalse(table_exists[0])


    @patch('collector.db_handler.get_db_connection')
    @patch('collector.db_handler.Path')
    def test_initialize_db_not_initialized(self, mock_path, mock_connection):
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        mock_path_instance.is_file.return_value = False
        mock_connection.return_value = (self.conn, self.cursor)

        result = db_handler.initialize_db(self.dbpath)
        self.assertFalse(result)
        mock_connection.assert_called_once()
        table_exists = self.cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='Locations'").fetchone()
        self.assertTrue(table_exists[0])



if __name__ == "__main__":
    unittest.main(verbosity=2)
"""Tests for CleanDB."""

import sqlite3
import tempfile
import os
import unittest
from cleandb import DatabaseCleaner


class TestDatabaseCleaner(unittest.TestCase):
    """Test cases for DatabaseCleaner."""
    
    def setUp(self):
        """Set up test database before each test."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name
        
        # Create a test database with sample data
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()
        
        # Create test tables
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content TEXT,
                user_id INTEGER
            )
        """)
        
        # Insert test data
        cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", ("Alice", "alice@example.com"))
        cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", ("Bob", "bob@example.com"))
        cursor.execute("INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)", 
                      ("Post 1", "Content 1", 1))
        cursor.execute("INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)", 
                      ("Post 2", "Content 2", 2))
        
        self.conn.commit()
    
    def tearDown(self):
        """Clean up after each test."""
        self.conn.close()
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
    
    def test_detect_database_type(self):
        """Test database type detection."""
        cleaner = DatabaseCleaner(self.conn)
        self.assertEqual(cleaner.db_type, "sqlite")
    
    def test_get_all_tables(self):
        """Test getting all tables from database."""
        cleaner = DatabaseCleaner(self.conn)
        tables = cleaner.get_all_tables()
        self.assertEqual(set(tables), {"users", "posts"})
    
    def test_empty_single_table(self):
        """Test emptying a single table."""
        cleaner = DatabaseCleaner(self.conn)
        
        # Verify data exists
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        self.assertEqual(cursor.fetchone()[0], 2)
        
        # Empty the table
        cleaner.empty_table("users")
        
        # Verify table is empty
        cursor.execute("SELECT COUNT(*) FROM users")
        self.assertEqual(cursor.fetchone()[0], 0)
        
        # Verify other table still has data
        cursor.execute("SELECT COUNT(*) FROM posts")
        self.assertEqual(cursor.fetchone()[0], 2)
    
    def test_empty_database(self):
        """Test emptying entire database."""
        cleaner = DatabaseCleaner(self.conn)
        
        # Empty all tables
        emptied = cleaner.empty_database()
        
        # Should have emptied 2 tables
        self.assertEqual(emptied, 2)
        
        # Verify all tables are empty
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        self.assertEqual(cursor.fetchone()[0], 0)
        cursor.execute("SELECT COUNT(*) FROM posts")
        self.assertEqual(cursor.fetchone()[0], 0)
    
    def test_empty_database_with_exclusions(self):
        """Test emptying database with excluded tables."""
        cleaner = DatabaseCleaner(self.conn)
        
        # Empty all tables except 'users'
        emptied = cleaner.empty_database(exclude_tables=["users"])
        
        # Should have emptied 1 table
        self.assertEqual(emptied, 1)
        
        # Verify 'posts' is empty
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM posts")
        self.assertEqual(cursor.fetchone()[0], 0)
        
        # Verify 'users' still has data
        cursor.execute("SELECT COUNT(*) FROM users")
        self.assertEqual(cursor.fetchone()[0], 2)
    
    def test_autoincrement_reset(self):
        """Test that auto-increment is reset after emptying."""
        cleaner = DatabaseCleaner(self.conn)
        
        # Empty the users table
        cleaner.empty_table("users", reset_autoincrement=True)
        
        # Insert a new record
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", 
                      ("Charlie", "charlie@example.com"))
        self.conn.commit()
        
        # The new record should have id=1 (auto-increment was reset)
        cursor.execute("SELECT id FROM users WHERE name='Charlie'")
        new_id = cursor.fetchone()[0]
        self.assertEqual(new_id, 1)
    
    def test_context_manager(self):
        """Test using DatabaseCleaner as a context manager."""
        with DatabaseCleaner(self.conn) as cleaner:
            tables = cleaner.get_all_tables()
            self.assertEqual(len(tables), 2)
    
    def test_empty_already_empty_table(self):
        """Test emptying a table that's already empty."""
        cleaner = DatabaseCleaner(self.conn)
        
        # Empty the table twice
        cleaner.empty_table("users")
        cleaner.empty_table("users")  # Should not raise an error
        
        # Verify table is still empty
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        self.assertEqual(cursor.fetchone()[0], 0)


if __name__ == "__main__":
    unittest.main()

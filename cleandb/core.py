"""Core database cleaning functionality."""

import sqlite3
from typing import Optional, List


class DatabaseCleaner:
    """A class to clean and empty databases."""
    
    def __init__(self, connection):
        """
        Initialize the DatabaseCleaner.
        
        Args:
            connection: Database connection object (e.g., sqlite3.Connection)
        """
        self.connection = connection
        self.db_type = self._detect_database_type()
        self._tables_cache = None
    
    def _detect_database_type(self) -> str:
        """Detect the type of database from the connection object."""
        if isinstance(self.connection, sqlite3.Connection):
            return "sqlite"
        
        # Check for psycopg2 connection
        if "psycopg2" in str(type(self.connection).__module__):
            return "postgresql"
        
        # Check for MySQL connection
        if "mysql" in str(type(self.connection).__module__):
            return "mysql"
        
        return "unknown"
    
    def _quote_identifier(self, identifier: str) -> str:
        """
        Safely quote a database identifier (table name).
        
        Args:
            identifier: The identifier to quote
            
        Returns:
            Quoted identifier appropriate for the database type
        """
        if self.db_type == "sqlite":
            # SQLite uses double quotes for identifiers
            # Escape any double quotes in the identifier
            return '"' + identifier.replace('"', '""') + '"'
        elif self.db_type == "postgresql":
            # PostgreSQL uses double quotes for identifiers
            return '"' + identifier.replace('"', '""') + '"'
        elif self.db_type == "mysql":
            # MySQL uses backticks for identifiers
            return '`' + identifier.replace('`', '``') + '`'
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")
    
    def _validate_table_name(self, table_name: str) -> None:
        """
        Validate that a table name exists in the database.
        
        Args:
            table_name: The table name to validate
            
        Raises:
            ValueError: If the table doesn't exist
        """
        # Use cached table list if available
        if self._tables_cache is None:
            self._tables_cache = self._get_all_tables_uncached()
        
        if table_name not in self._tables_cache:
            raise ValueError(f"Table '{table_name}' does not exist in the database")
    
    def _get_all_tables_uncached(self) -> List[str]:
        """
        Get a list of all tables in the database (uncached).
        
        Returns:
            List of table names
        """
        cursor = self.connection.cursor()
        
        if self.db_type == "sqlite":
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
        elif self.db_type == "postgresql":
            cursor.execute(
                "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
            )
        elif self.db_type == "mysql":
            cursor.execute("SHOW TABLES")
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")
        
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return tables
    
    def get_all_tables(self) -> List[str]:
        """
        Get a list of all tables in the database.
        
        Returns:
            List of table names
        """
        # Always fetch fresh list for this public method
        return self._get_all_tables_uncached()
    
    def empty_table(self, table_name: str, reset_autoincrement: bool = True) -> None:
        """
        Empty a specific table.
        
        Args:
            table_name: Name of the table to empty
            reset_autoincrement: Whether to reset auto-increment counters (default: True)
            
        Raises:
            ValueError: If the table doesn't exist
        """
        # Validate table name to prevent SQL injection
        self._validate_table_name(table_name)
        
        cursor = self.connection.cursor()
        quoted_table = self._quote_identifier(table_name)
        
        if self.db_type == "sqlite":
            cursor.execute(f"DELETE FROM {quoted_table}")
            if reset_autoincrement:
                # sqlite_sequence only exists if there are AUTOINCREMENT columns
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='sqlite_sequence'"
                )
                if cursor.fetchone():
                    cursor.execute(
                        "DELETE FROM sqlite_sequence WHERE name=?",
                        (table_name,)
                    )
        elif self.db_type == "postgresql":
            if reset_autoincrement:
                cursor.execute(f"TRUNCATE TABLE {quoted_table} RESTART IDENTITY CASCADE")
            else:
                cursor.execute(f"TRUNCATE TABLE {quoted_table} CASCADE")
        elif self.db_type == "mysql":
            cursor.execute(f"TRUNCATE TABLE {quoted_table}")
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")
        
        self.connection.commit()
        cursor.close()
    
    def empty_database(
        self, 
        exclude_tables: Optional[List[str]] = None,
        reset_autoincrement: bool = True
    ) -> int:
        """
        Empty all tables in the database.
        
        Args:
            exclude_tables: List of table names to exclude from cleaning
            reset_autoincrement: Whether to reset auto-increment counters (default: True)
        
        Returns:
            Number of tables that were emptied
        """
        exclude_tables = exclude_tables or []
        tables = self.get_all_tables()
        
        # Populate cache for efficient validation of multiple tables
        self._tables_cache = tables
        
        emptied_count = 0
        
        for table in tables:
            if table not in exclude_tables:
                self.empty_table(table, reset_autoincrement=reset_autoincrement)
                emptied_count += 1
        
        # Clear cache after operation
        self._tables_cache = None
        
        return emptied_count
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        # Don't close the connection as it was provided by the user
        pass

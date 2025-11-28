# CleanDB

A Python utility to empty and clean databases quickly and safely.

## Features

- **Empty entire databases** or specific tables
- **Support for multiple database types**: SQLite, PostgreSQL, MySQL
- **Exclude specific tables** from cleaning
- **Reset auto-increment counters** (optional)
- **Command-line interface** for easy usage
- **Python API** for programmatic use

## Installation

```bash
pip install -e .
```

For specific database support:

```bash
# PostgreSQL support
pip install -e ".[postgresql]"

# MySQL support
pip install -e ".[mysql]"
```

## Usage

### Command Line Interface

Empty an SQLite database:

```bash
cleandb --sqlite mydb.db
```

Empty database but exclude certain tables:

```bash
cleandb --sqlite mydb.db --exclude users sessions
```

Preview what would be done without actually doing it:

```bash
cleandb --sqlite mydb.db --dry-run
```

Don't reset auto-increment counters:

```bash
cleandb --sqlite mydb.db --no-reset-autoincrement
```

### Python API

```python
import sqlite3
from cleandb import DatabaseCleaner

# Connect to your database
conn = sqlite3.connect('mydb.db')

# Create a cleaner instance
cleaner = DatabaseCleaner(conn)

# Empty all tables
cleaner.empty_database()

# Empty all tables except specific ones
cleaner.empty_database(exclude_tables=['users', 'sessions'])

# Empty a specific table
cleaner.empty_table('logs')

# Get list of all tables
tables = cleaner.get_all_tables()
print(f"Found {len(tables)} tables: {tables}")

conn.close()
```

### Using as Context Manager

```python
import sqlite3
from cleandb import DatabaseCleaner

conn = sqlite3.connect('mydb.db')
with DatabaseCleaner(conn) as cleaner:
    cleaner.empty_database(exclude_tables=['users'])
conn.close()
```

## API Reference

### `DatabaseCleaner(connection)`

Initialize a DatabaseCleaner instance.

**Parameters:**
- `connection`: Database connection object (e.g., `sqlite3.Connection`)

**Methods:**

#### `get_all_tables() -> List[str]`

Get a list of all tables in the database.

**Returns:** List of table names

#### `empty_table(table_name: str, reset_autoincrement: bool = True) -> None`

Empty a specific table.

**Parameters:**
- `table_name`: Name of the table to empty
- `reset_autoincrement`: Whether to reset auto-increment counters (default: True)

#### `empty_database(exclude_tables: Optional[List[str]] = None, reset_autoincrement: bool = True) -> int`

Empty all tables in the database.

**Parameters:**
- `exclude_tables`: List of table names to exclude from cleaning
- `reset_autoincrement`: Whether to reset auto-increment counters (default: True)

**Returns:** Number of tables that were emptied

## Supported Databases

- **SQLite**: Built-in support, no extra dependencies
- **PostgreSQL**: Requires `psycopg2-binary`
- **MySQL**: Requires `mysql-connector-python`

## Running Tests

```bash
python -m unittest discover tests
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
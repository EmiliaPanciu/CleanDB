"""Command-line interface for CleanDB."""

import argparse
import sqlite3
import sys
from cleandb import DatabaseCleaner


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="CleanDB - Empty and clean databases",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  cleandb --sqlite mydb.db
  cleandb --sqlite mydb.db --exclude users sessions
  cleandb --sqlite mydb.db --no-reset-autoincrement
        """
    )
    
    parser.add_argument(
        "--sqlite",
        metavar="PATH",
        help="Path to SQLite database file"
    )
    
    parser.add_argument(
        "--exclude",
        nargs="+",
        metavar="TABLE",
        help="Tables to exclude from cleaning"
    )
    
    parser.add_argument(
        "--no-reset-autoincrement",
        action="store_true",
        help="Do not reset auto-increment counters"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without actually doing it"
    )
    
    args = parser.parse_args()
    
    # Check if at least one database option is provided
    if not args.sqlite:
        parser.error("Please specify a database (e.g., --sqlite PATH)")
    
    # Handle SQLite
    if args.sqlite:
        try:
            conn = sqlite3.connect(args.sqlite)
            cleaner = DatabaseCleaner(conn)
            
            tables = cleaner.get_all_tables()
            exclude_tables = args.exclude or []
            tables_to_clean = [t for t in tables if t not in exclude_tables]
            
            if args.dry_run:
                print(f"Would empty {len(tables_to_clean)} table(s):")
                for table in tables_to_clean:
                    print(f"  - {table}")
                if exclude_tables:
                    print(f"\nExcluding {len(exclude_tables)} table(s):")
                    for table in exclude_tables:
                        print(f"  - {table}")
            else:
                emptied = cleaner.empty_database(
                    exclude_tables=exclude_tables,
                    reset_autoincrement=not args.no_reset_autoincrement
                )
                print(f"Successfully emptied {emptied} table(s)")
            
            conn.close()
            return 0
            
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

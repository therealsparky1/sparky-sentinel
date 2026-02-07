"""
Data Storage Module for Scraped Data
=====================================

A lightweight SQLite-based storage system with auto-schema creation,
upsert logic, and flexible querying for web scraping projects.

Features:
- Auto-creates database and tables from data structure
- Handles nested data (stored as JSON)
- Upsert logic (insert or update on conflict)
- Flexible filtering and search
- Returns results as list of dicts

Usage Example:
    from data_storage import store_data, fetch_data
    
    # Store data
    data = {'url': 'https://example.com', 'title': 'Example', 'price': 29.99}
    store_data(data, 'products')
    
    # Fetch data
    results = fetch_data('products', filters={'price': 29.99})
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pathlib import Path


class DataStorage:
    """Main storage class handling SQLite operations."""
    
    def __init__(self, db_path: str = "scraped_data.db"):
        """
        Initialize storage with database path.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Create database file if it doesn't exist."""
        if not os.path.exists(self.db_path):
            conn = sqlite3.connect(self.db_path)
            conn.close()
            print(f"✓ Created database: {self.db_path}")
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _infer_sql_type(self, value: Any) -> str:
        """
        Infer SQL column type from Python value.
        
        Args:
            value: Python value to analyze
            
        Returns:
            SQL type string
        """
        if value is None:
            return "TEXT"
        elif isinstance(value, bool):
            return "INTEGER"  # SQLite uses 0/1 for bool
        elif isinstance(value, int):
            return "INTEGER"
        elif isinstance(value, float):
            return "REAL"
        elif isinstance(value, (dict, list)):
            return "TEXT"  # Store as JSON
        elif isinstance(value, datetime):
            return "TEXT"  # Store as ISO format
        else:
            return "TEXT"
    
    def _serialize_value(self, value: Any) -> Any:
        """
        Serialize complex values for storage.
        
        Args:
            value: Value to serialize
            
        Returns:
            Serialized value suitable for SQLite
        """
        if isinstance(value, (dict, list)):
            return json.dumps(value)
        elif isinstance(value, datetime):
            return value.isoformat()
        elif isinstance(value, bool):
            return 1 if value else 0
        return value
    
    def _deserialize_value(self, value: Any, original_type: str) -> Any:
        """
        Deserialize values from storage.
        
        Args:
            value: Value from database
            original_type: Original SQL type
            
        Returns:
            Deserialized value
        """
        if value is None:
            return None
        
        if isinstance(value, str):
            # Try to parse JSON
            if value.startswith('{') or value.startswith('['):
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    pass
        
        return value
    
    def _table_exists(self, conn: sqlite3.Connection, table_name: str) -> bool:
        """Check if table exists."""
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        )
        return cursor.fetchone() is not None
    
    def _get_table_columns(self, conn: sqlite3.Connection, table_name: str) -> List[str]:
        """Get existing column names for a table."""
        cursor = conn.execute(f"PRAGMA table_info({table_name})")
        return [row[1] for row in cursor.fetchall()]
    
    def _create_or_update_table(self, conn: sqlite3.Connection, table_name: str, data: Dict[str, Any]):
        """
        Create table or add missing columns.
        
        Args:
            conn: Database connection
            table_name: Name of table
            data: Sample data to infer schema
        """
        if not self._table_exists(conn, table_name):
            # Create new table
            columns = []
            for key, value in data.items():
                sql_type = self._infer_sql_type(value)
                columns.append(f"{key} {sql_type}")
            
            # Add metadata columns
            columns.append("_id INTEGER PRIMARY KEY AUTOINCREMENT")
            columns.append("_created_at TEXT DEFAULT CURRENT_TIMESTAMP")
            columns.append("_updated_at TEXT DEFAULT CURRENT_TIMESTAMP")
            
            create_sql = f"CREATE TABLE {table_name} ({', '.join(columns)})"
            conn.execute(create_sql)
            print(f"✓ Created table: {table_name}")
        else:
            # Check for new columns and add them
            existing_cols = self._get_table_columns(conn, table_name)
            for key, value in data.items():
                if key not in existing_cols:
                    sql_type = self._infer_sql_type(value)
                    alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {key} {sql_type}"
                    conn.execute(alter_sql)
                    print(f"✓ Added column: {table_name}.{key}")
    
    def store_data(self, data: Union[Dict[str, Any], List[Dict[str, Any]]], 
                   table_name: str, unique_key: Optional[str] = None) -> int:
        """
        Store data in SQLite database with upsert logic.
        
        Args:
            data: Dictionary or list of dictionaries to store
            table_name: Name of table to store data in
            unique_key: Column name to use for duplicate detection (upsert)
                       If None, always inserts new records
        
        Returns:
            Number of records stored/updated
        """
        # Handle single dict or list of dicts
        if isinstance(data, dict):
            data = [data]
        
        if not data:
            return 0
        
        conn = self._get_connection()
        count = 0
        
        try:
            # Create or update table schema
            self._create_or_update_table(conn, table_name, data[0])
            
            for record in data:
                # Serialize complex values
                serialized = {k: self._serialize_value(v) for k, v in record.items()}
                
                if unique_key and unique_key in serialized:
                    # Upsert: Check if record exists
                    cursor = conn.execute(
                        f"SELECT _id FROM {table_name} WHERE {unique_key} = ?",
                        (serialized[unique_key],)
                    )
                    existing = cursor.fetchone()
                    
                    if existing:
                        # Update existing record
                        set_clause = ", ".join([f"{k} = ?" for k in serialized.keys()])
                        set_clause += ", _updated_at = CURRENT_TIMESTAMP"
                        values = list(serialized.values()) + [existing['_id']]
                        
                        update_sql = f"UPDATE {table_name} SET {set_clause} WHERE _id = ?"
                        conn.execute(update_sql, values)
                        count += 1
                    else:
                        # Insert new record
                        columns = ", ".join(serialized.keys())
                        placeholders = ", ".join(["?" for _ in serialized])
                        insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                        conn.execute(insert_sql, list(serialized.values()))
                        count += 1
                else:
                    # Always insert
                    columns = ", ".join(serialized.keys())
                    placeholders = ", ".join(["?" for _ in serialized])
                    insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                    conn.execute(insert_sql, list(serialized.values()))
                    count += 1
            
            conn.commit()
            print(f"✓ Stored {count} record(s) in {table_name}")
            
        except Exception as e:
            conn.rollback()
            print(f"✗ Error storing data: {e}")
            raise
        finally:
            conn.close()
        
        return count
    
    def fetch_data(self, table_name: str, 
                   filters: Optional[Dict[str, Any]] = None,
                   order_by: Optional[str] = None,
                   limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Fetch data from database with optional filtering.
        
        Args:
            table_name: Name of table to query
            filters: Dictionary of column: value filters (AND logic)
            order_by: Column name to sort by (prefix with '-' for DESC)
            limit: Maximum number of records to return
        
        Returns:
            List of dictionaries containing matching records
        """
        conn = self._get_connection()
        
        try:
            # Build query
            query = f"SELECT * FROM {table_name}"
            params = []
            
            # Add WHERE clause
            if filters:
                where_clauses = []
                for key, value in filters.items():
                    where_clauses.append(f"{key} = ?")
                    params.append(self._serialize_value(value))
                query += " WHERE " + " AND ".join(where_clauses)
            
            # Add ORDER BY
            if order_by:
                if order_by.startswith('-'):
                    query += f" ORDER BY {order_by[1:]} DESC"
                else:
                    query += f" ORDER BY {order_by} ASC"
            
            # Add LIMIT
            if limit:
                query += f" LIMIT {limit}"
            
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            
            # Convert to list of dicts
            results = []
            for row in rows:
                record = dict(row)
                # Deserialize JSON fields
                for key, value in record.items():
                    record[key] = self._deserialize_value(value, type(value).__name__)
                results.append(record)
            
            print(f"✓ Fetched {len(results)} record(s) from {table_name}")
            return results
            
        except Exception as e:
            print(f"✗ Error fetching data: {e}")
            raise
        finally:
            conn.close()


# Global storage instance
_storage = DataStorage()


# Convenience functions
def store_data(data: Union[Dict[str, Any], List[Dict[str, Any]]], 
               table_name: str, unique_key: Optional[str] = None) -> int:
    """
    Store data in SQLite database.
    
    Args:
        data: Dictionary or list of dictionaries to store
        table_name: Name of table to store data in
        unique_key: Column name for duplicate detection (upsert)
    
    Returns:
        Number of records stored/updated
    
    Example:
        >>> data = {'url': 'https://example.com', 'title': 'Example'}
        >>> store_data(data, 'websites', unique_key='url')
        1
    """
    return _storage.store_data(data, table_name, unique_key)


def fetch_data(table_name: str, 
               filters: Optional[Dict[str, Any]] = None,
               order_by: Optional[str] = None,
               limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Fetch data from database.
    
    Args:
        table_name: Name of table to query
        filters: Dictionary of column: value filters
        order_by: Column name to sort by (prefix with '-' for DESC)
        limit: Maximum number of records to return
    
    Returns:
        List of dictionaries containing matching records
    
    Example:
        >>> results = fetch_data('websites', filters={'title': 'Example'})
        >>> len(results)
        1
    """
    return _storage.fetch_data(table_name, filters, order_by, limit)


def get_storage(db_path: str = "scraped_data.db") -> DataStorage:
    """
    Get a DataStorage instance with custom database path.
    
    Args:
        db_path: Path to SQLite database
    
    Returns:
        DataStorage instance
    """
    return DataStorage(db_path)


if __name__ == "__main__":
    print("Data Storage Module - Ready for use!")
    print("Import with: from data_storage import store_data, fetch_data")

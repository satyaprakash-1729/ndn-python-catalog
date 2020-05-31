import os
import sqlite3
from typing import List, Optional
import time


class SqliteStorage(object):
    """
    Handles all SQLite operations on the catalog_data table. Structured in a key-value format with expiry times.
    """
    def __init__(self, db_path):
        """
        Creates Database if not present. Creates table catalog_data if not present.
        TABLE:
        key             PRIMARY KEY     BLOB
        value           PRIMARY KEY     BLOB
        expire_time_ms                  INT
        :param db_path:
        """
        super().__init__()
        db_path = os.path.expanduser(db_path)
        if len(os.path.dirname(db_path)) > 0 and not os.path.exists(os.path.dirname(db_path)):
            try:
                os.makedirs(os.path.dirname(db_path))
            except PermissionError:
                raise PermissionError(f'Could not create database directory: {db_path}') from None

        self.conn = sqlite3.connect(os.path.expanduser(db_path))
        c = self.conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS catalog_data (
                key BLOB,
                value BLOB,
                expire_time_ms INTEGER,
                PRIMARY KEY(key, value)
            )
        """)
        self.conn.commit()

    def put(self, key: bytes, value: bytes, expire_time_ms: Optional[int]):
        """
        Inserts key - value - expire_time_ms into the table.
        :param key:
        :param value:
        :param expire_time_ms:
        :return:
        """
        c = self.conn.cursor()
        c.execute('INSERT OR REPLACE INTO catalog_data (key, value, expire_time_ms) VALUES (?, ?, ?)',
            (key, value, expire_time_ms))
        self.conn.commit()

    def put_batch(self, keys: List[bytes], values: List[bytes], expire_time_mss: List[Optional[int]]):
        """
        Inserts all key - value - expire_time_ms in the list into the table.
        :param keys:
        :param values:
        :param expire_time_mss:
        :return:
        """
        c = self.conn.cursor()
        c.executemany('INSERT OR REPLACE INTO catalog_data (key, value, expire_time_ms) VALUES (?, ?, ?)',
            zip(keys, values, expire_time_mss))
        self.conn.commit()

    def get(self, key: bytes) -> Optional[bytes]:
        """
        Returns all values which have not expired for the given key.
        :param key:
        :return:
        """
        c = self.conn.cursor()
        query = 'SELECT value FROM catalog_data WHERE '
        query += f'(expire_time_ms > {int(time.time())}) AND '
        query += 'key = ?'
        c.execute(query, (key, ))
        ret = c.fetchall()
        return [retelem[0] for retelem in ret] if ret else None

    def remove(self, key1: bytes, key2: bytes) -> bool:
        """
        Removes all entries in the table with the given pair key1-key2
        Here value is called key2 to give an intuitive sense, key2 here is basically the value.
        :param key1:
        :param key2:
        :return:
        """
        c = self.conn.cursor()
        n_removed = c.execute('DELETE FROM catalog_data WHERE key = ? AND value = ?', (key1, key2, )).rowcount
        self.conn.commit()
        return n_removed > 0

    def remove_batch(self, keys1: List[bytes], keys2: List[bytes]) -> bool:
        """
        Removes all entries in the table corresponding to any of the key-value pairs in the given list in
        a batched manner.
        :param keys1:
        :param keys2:
        :return:
        """
        c = self.conn.cursor()
        n_removed = c.executemany('DELETE FROM catalog_data WHERE key = ? AND value = ?', zip(keys1, keys2)).rowcount
        self.conn.commit()
        return n_removed > 0


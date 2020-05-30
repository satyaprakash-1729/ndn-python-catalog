import os
import sqlite3
from typing import List, Optional
import time


class SqliteStorage(object):

    def __init__(self, db_path):
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
                key BLOB PRIMARY KEY,
                value BLOB,
                expire_time_ms INTEGER
            )
        """)
        self.conn.commit()

    def put(self, key: bytes, value: bytes, expire_time_ms: Optional[int]):
        c = self.conn.cursor()
        c.execute('INSERT OR REPLACE INTO catalog_data (key, value, expire_time_ms) VALUES (?, ?, ?)',
            (key, value, expire_time_ms))
        self.conn.commit()

    def put_batch(self, keys: List[bytes], values: List[bytes], expire_time_mss: List[Optional[int]]):
        c = self.conn.cursor()
        c.executemany('INSERT OR REPLACE INTO catalog_data (key, value, expire_time_ms) VALUES (?, ?, ?)',
            zip(keys, values, expire_time_mss))
        self.conn.commit()

    def get(self, key: bytes) -> Optional[bytes]:
        c = self.conn.cursor()
        query = 'SELECT value FROM catalog_data WHERE '
        query += f'(expire_time_ms > {int(time.time())}) AND '
        query += 'key = ?'
        c.execute(query, (key, ))
        ret = c.fetchall()
        return [retelem[0] for retelem in ret] if ret else None

    def remove(self, key1: bytes, key2: bytes) -> bool:
        c = self.conn.cursor()
        n_removed = c.execute('DELETE FROM catalog_data WHERE key = ? AND value = ?', (key1, key2, )).rowcount
        self.conn.commit()
        return n_removed > 0

    def remove_batch(self, keys1: List[bytes], keys2: List[bytes]) -> bool:
        c = self.conn.cursor()
        n_removed = c.executemany('DELETE FROM catalog_data WHERE key = ? AND value = ?', zip(keys1, keys2)).rowcount
        self.conn.commit()
        return n_removed > 0


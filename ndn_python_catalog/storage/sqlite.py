import os
import sqlite3
from typing import List, Optional


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
                value BLOB
            )
        """)
        self.conn.commit()

    def put(self, key: bytes, value: bytes):
        c = self.conn.cursor()
        c.execute('INSERT OR REPLACE INTO catalog_data (key, value, expire_time_ms) VALUES (?, ?)',
            (key, value))
        self.conn.commit()

    def put_batch(self, keys: List[bytes], values: List[bytes]):
        c = self.conn.cursor()
        c.executemany('INSERT OR REPLACE INTO catalog_data (key, value) VALUES (?, ?)',
            zip(keys, values))
        self.conn.commit()

    def get(self, key: bytes) -> Optional[bytes]:
        c = self.conn.cursor()
        query = 'SELECT value FROM catalog_data WHERE '
        query += 'key = ?'
        c.execute(query, (key, ))
        ret = c.fetchone()
        return ret[0] if ret else None

    def _remove(self, key: bytes) -> bool:
        c = self.conn.cursor()
        n_removed = c.execute('DELETE FROM catalog_data WHERE key = ?', (key, )).rowcount
        self.conn.commit()
        return n_removed > 0
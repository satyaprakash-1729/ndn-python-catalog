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
        c.execute('INSERT OR REPLACE INTO catalog_data (key, value) VALUES (?, ?)',
            (key, value))
        self.conn.commit()

    def put_batch(self, keys: List[bytes], values: List[bytes]):
        c = self.conn.cursor()
        print (keys)
        c.executemany('INSERT OR REPLACE INTO catalog_data (key, value) VALUES (?, ?)',
            zip(keys, values))
        self.conn.commit()

    def get(self, key: bytes) -> Optional[bytes]:
        c = self.conn.cursor()
        print(key)
        query = 'SELECT value FROM catalog_data WHERE '
        query += 'key = ?'
        c.execute(query, (key, ))
        ret = c.fetchone()
        return ret[0] if ret else None

    def remove(self, key: bytes) -> bool:
        c = self.conn.cursor()
        n_removed = c.execute('DELETE FROM catalog_data WHERE key = ?', (key, )).rowcount
        self.conn.commit()
        return n_removed > 0

    def remove_batch(self, keys: List[bytes]) -> bool:
        c = self.conn.cursor()
        print (keys)
        n_removed = c.executemany('DELETE FROM catalog_data WHERE key = ?', [(key, ) for key in keys]).rowcount
        self.conn.commit()
        return n_removed > 0

    def alter_batch(self, keys: List[bytes], values: List[bytes]):
        c = self.conn.cursor()
        for key, value in zip(keys, values):
            return_val = self.get(key)
            if return_val is None:
                self.put(key, value)
            else:
                return_val = return_val + " " + value
                c.execute('INSERT OR REPLACE INTO catalog_data (key, value) VALUES (?, ?)',
                          (key, return_val))
        self.conn.commit()

    def granular_remove_batch(self, keys: List[bytes], repo_name: bytes):
        for key in keys:
            return_data_names = self.get(key).split()
            left_names = [name for name in return_data_names if name != repo_name]
            if len(left_names) > 0:
                self.put(key, " ".join(left_names))
            else:
                self.remove(key)

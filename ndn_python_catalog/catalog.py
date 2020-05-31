from ndn.app import NDNApp
from .storage import *
from .handle import *


class Catalog(object):
    def __init__(self, prefix, app: NDNApp, storage: SqliteStorage, read_handle: ReadHandle,
                 write_handle: WriteHandle):
        self.prefix = prefix
        self.app = app
        self.storage = storage
        self.write_handle = write_handle
        self.read_handle = read_handle
        self.running = True

    async def listen(self):
        """
        Start listening on the write handle.
        """
        await self.write_handle.listen(self.prefix)

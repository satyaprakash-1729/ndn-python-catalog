from ndn.app import NDNApp
from ndn_python_repo.storage import *
from .handle import *


class Catalog(object):
    def __init__(self, prefix, app: NDNApp, storage: Storage, read_handle: ReadHandle,
                 write_handle: WriteHandle):
        self.prefix = prefix
        self.app = app
        self.storage = storage
        self.write_handle = write_handle
        self.read_handle = read_handle
        self.running = True

    async def listen(self):
        await self.write_handle.listen(self.prefix)

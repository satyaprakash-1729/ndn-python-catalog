import asyncio as aio
import logging
from ndn.app import NDNApp
from ndn.encoding import NonStrictName, DecodeError
from . import ReadHandle, CommandHandle
from command.catalog_command import CatalogCommandParameter
from ndn_python_repo.storage import Storage


class WriteHandle(CommandHandle):
    def __init__(self, app: NDNApp, storage: Storage, read_handle: ReadHandle):
        super(WriteHandle, self).__init__(app, storage)
        self.m_read_handle = read_handle
        self.prefix = None

    async def listen(self, prefix: NonStrictName):
        self.prefix = prefix
        self.app.route(self.prefix + ['insert'])(self._on_insert)

    def _on_insert(self, msg):
        try:
            cmd_param = CatalogCommandParameter.parse(msg)
            if cmd_param.name is None:
                raise DecodeError()
        except (DecodeError, IndexError) as exc:
            logging.warning('Parameter interest blob decoding failed')
            return
        aio.ensure_future(self._process_insert(cmd_param))

    async def _process_insert(self, cmd_param: CatalogCommandParameter):
        data_name = cmd_param.data_name
        repo_name = cmd_param.repo_name

        self.storage.put(bytes(data_name), bytes(repo_name), 1000)

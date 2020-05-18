import asyncio as aio
import logging
from ndn.app import NDNApp
from ndn.encoding import NonStrictName, DecodeError, FormalName, InterestParam, BinaryStr, Name
from typing import Optional
from .command_handle import CommandHandle
from .read_handle import ReadHandle
from ..command.catalog_command import CatalogCommandParameter, CatalogRequestParameter
from ndn_python_repo.storage import Storage


class WriteHandle(CommandHandle):
    def __init__(self, app: NDNApp, storage: Storage, read_handle: ReadHandle):
        super(WriteHandle, self).__init__(app, storage)
        self.m_read_handle = read_handle
        self.prefix = None

    async def listen(self, prefix: NonStrictName):
        self.prefix = prefix
        # print(self.prefix)
        print(">>>>", Name.to_str(self.prefix + ['insert']))

        self.app.route(self.prefix + ['insert'])(self._on_insert)

        self.app.route(self.prefix)(self._on_interest)

    def _on_insert(self, int_name: FormalName, int_param: InterestParam, app_param: Optional[BinaryStr]):
        print(">>>>", int_name, int_param, app_param)
        aio.ensure_future(self._process_insert(int_name, int_param, app_param))

    def _on_interest(self, int_name: FormalName, int_param: InterestParam, app_param: Optional[BinaryStr]):
        aio.ensure_future(self._process_interest(int_name, int_param, app_param))

    async def _process_insert(self, int_name: FormalName, int_param: InterestParam, app_param: Optional[BinaryStr]):
        print(">>>>", int_name, int_param, app_param)
        try:
            cmd_param = CatalogCommandParameter.parse(app_param)
            if cmd_param.name is None:
                raise DecodeError()
        except (DecodeError, IndexError) as exc:
            logging.warning('Parameter interest blob decoding failed')
            return

        print("CMD PARAM: ", cmd_param)
        data_name = cmd_param.data_name
        repo_name = cmd_param.repo_name

        self.storage.put(bytes(data_name), bytes(repo_name), 1000)
        self.app.put_data()

    async def _process_interest(self, int_name: FormalName, int_param: InterestParam, app_param: Optional[BinaryStr]):
        app_param_parsed = CatalogRequestParameter.parse(app_param)
        data_name = app_param_parsed.data_name

        repo_name_bytes = self.storage.get(bytes(data_name))
        self.app.put_data(int_name, repo_name_bytes, freshness_period=0)


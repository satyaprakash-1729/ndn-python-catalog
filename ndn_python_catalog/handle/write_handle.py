import asyncio as aio
from ndn.app import NDNApp
from ndn.encoding import NonStrictName, FormalName, InterestParam, BinaryStr, Name
from typing import Optional
from .command_handle import CommandHandle
from .read_handle import ReadHandle
from ..command.catalog_command import *
from ..storage import SqliteStorage
from ndn.types import InterestNack, InterestTimeout
from ndn.utils import gen_nonce


class WriteHandle(CommandHandle):
    def __init__(self, app: NDNApp, storage: SqliteStorage, read_handle: ReadHandle):
        super(WriteHandle, self).__init__(app, storage)
        self.m_read_handle = read_handle
        self.prefix = None
        self.storage = storage

    async def listen(self, prefix: NonStrictName):
        self.prefix = prefix
        print("REGISTERED TO: ", Name.to_str(self.prefix + ['insert']))
        # /catalog/insert
        self.app.route(self.prefix + ['insert'])(self._on_insert)

    def _on_insert(self, int_name: FormalName, int_param: InterestParam, app_param: Optional[BinaryStr]):
        print(">>>>", int_name, int_param, app_param)
        aio.ensure_future(self._process_insert(int_name, int_param, app_param))

#    async def put_new_data(self, int_name:FormalName):
#        self.app.put_data(int_name, "".encode(), freshness_period=0)

    async def _process_insert(self, int_name: FormalName, int_param: InterestParam, app_param: Optional[BinaryStr]):
        print(">>>>", int_name, int_param, app_param)
        # cmd_param = CatalogCommandParameter.parse(app_param)
        # name = cmd_param.name
        name = Name.from_str("testrepo")

        # ACK
        #aio.ensure_future(self._process_insert(int_name))
        self.app.put_data(int_name, "".encode(), freshness_period=0)

        # INTEREST
        n_retries = 3
        while n_retries > 0:
            try:
                name = name + ['fetch_map']
                name += [str(gen_nonce())]
                print("Sending interest on : ", Name.to_str(name))
                _, _, data_bytes = await self.app.express_interest(name, must_be_fresh=True, can_be_prefix=True)
                break
            except InterestNack:
                print(">>>NACK")
                return None
            except InterestTimeout:
                print(">>>TIMEOUT")
            n_retries -= 1

        data_recvd = CatalogDataListParameter.parse(data_bytes)
        mapping_name = Name.to_str(data_recvd.name)
        keys_to_insert = [Name.to_str(data_name) for data_name in data_recvd.insert_data_names]
        keys_to_delete = [Name.to_str(data_name) for data_name in data_recvd.delete_data_names]
        vals = [mapping_name]*len(keys_to_insert)
        self.storage.alter_batch(keys_to_insert, vals)
        self.storage.granular_remove_batch(keys_to_delete, mapping_name)


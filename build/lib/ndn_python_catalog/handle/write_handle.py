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
import logging
import time


class WriteHandle(CommandHandle):
    def __init__(self, app: NDNApp, storage: SqliteStorage, read_handle: ReadHandle):
        super(WriteHandle, self).__init__(app, storage)
        self.m_read_handle = read_handle
        self.prefix = None
        self.storage = storage

    async def listen(self, prefix: NonStrictName):
        self.prefix = prefix
        logging.debug("REGISTERED TO: {}".format(Name.to_str(self.prefix + ['insert'])))
        # /catalog/insert
        self.app.route(self.prefix + ['insert'])(self._on_insert)

    def _on_insert(self, int_name: FormalName, int_param: InterestParam, app_param: Optional[BinaryStr]):
        logging.debug("Interest Received: {}".format(Name.to_str(int_name), int_param))
        aio.ensure_future(self._process_insert(int_name, int_param, app_param))

    @staticmethod
    def get_current_time() -> int:
        return int(time.time())


    async def _process_insert(self, int_name: FormalName, int_param: InterestParam, app_param: Optional[BinaryStr]):
        cmd_param = CatalogCommandParameter.parse(app_param)
        name = cmd_param.name
        name = name + ['fetch_map']

        # ACK
        logging.debug("Sending ACK for insert request")
        self.app.put_data(int_name, "".encode(), freshness_period=500)

        # INTEREST
        data_bytes = None
        n_retries = 3
        while n_retries > 0:
            try:
                nonce_name = name + [str(gen_nonce())]
                logging.debug("Sending interest on : {}".format(Name.to_str(name)))
                _, _, data_bytes = await self.app.express_interest(nonce_name, must_be_fresh=True, can_be_prefix=False)
                break
            except InterestNack:
                logging.error("NACK")
                return None
            except InterestTimeout:
                logging.error("TIMEOUT")
            n_retries -= 1

        if data_bytes is None:
            return

        data_recvd = CatalogDataListParameter.parse(data_bytes)
        insert_list = data_recvd.insert_data_names
        delete_list = data_recvd.delete_data_names
        logging.debug("Insert {} names. Delete {} names,".format(len(insert_list), len(delete_list)))

        cur_time = WriteHandle.get_current_time()
        data_names = [Name.to_str(insert_param.data_name) for insert_param in insert_list]
        names = [Name.to_str(insert_param.name) for insert_param in insert_list]
        expire_times = [cur_time + int(insert_param.expire_time_ms) for insert_param in insert_list]
        self.storage.put_batch(data_names, names, expire_times)

        data_names = [Name.to_str(delete_param.data_name) for delete_param in delete_list]
        names = [Name.to_str(delete_param.name) for delete_param in delete_list]
        self.storage.remove_batch(data_names, names)

import asyncio as aio
from ndn.app import NDNApp
from ndn.encoding import NonStrictName, FormalName, InterestParam, BinaryStr, Name, Component
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
    """
    Handles the insertion Protocol for catalog. Involves a 4 way routine.
    Client ---Interest for insertion---> Catalog
    Catalog ---ACK---> Client
    Catalog ---Request for data---> Client
    Client ---Data for insertion and deletion---> Catalog
    """
    def __init__(self, app: NDNApp, storage: SqliteStorage, read_handle: ReadHandle):
        super(WriteHandle, self).__init__(app, storage)
        self.m_read_handle = read_handle
        self.prefix = None
        self.storage = storage
        self.processes = {}

    async def listen(self, prefix: NonStrictName):
        """
        Starts listening on /catalog_prefix/insert
        :param prefix: the prefix for the catalog
        """
        self.prefix = prefix
        logging.info("For INSERT Registered To: {}".format(Name.to_str(self.prefix + ['insert'])))
        self.app.route(self.prefix + ['insert'])(self._on_insert)

        logging.info("For CHECK Registered To: {}".format(Name.to_str(self.prefix + ['check'])))
        self.app.route(self.prefix + ['check'])(self._on_check)

    def _on_insert(self, int_name: FormalName, int_param: InterestParam, app_param: Optional[BinaryStr]):
        """
        Callback for insertion request interest.
        :param int_name:
        :param int_param:
        :param app_param:
        """
        logging.debug("Interest Received: {}".format(Name.to_str(int_name), int_param))
        aio.ensure_future(self._process_insert(int_name, int_param, app_param))

    @staticmethod
    def get_current_time() -> int:
        return int(time.time())

    async def _process_insert(self, int_name: FormalName, int_param: InterestParam, app_param: Optional[BinaryStr]):
        """
        Called when an insert interest is received. Extracts the client name from the app params for forwarding hint.
        Sends a ACK and then a data fetch interest to the client.
        Performs SQLite operations based on the data insertion/deletion request received.
        :param int_name:
        :param int_param:
        :param app_param:
        :return:
        """
        nonce = int(Component.to_str(int_name[-2]))
        self.processes[nonce] = False
        cmd_param = CatalogCommandParameter.parse(app_param)
        name = cmd_param.name
        name = name + ['fetch_map']

        # ACK
        logging.info("Sending ACK for insert request")
        self.app.put_data(int_name, "".encode(), freshness_period=500)

        # INTEREST
        data_bytes = None
        n_retries = 3
        while n_retries > 0:
            try:
                nonce_name = name + [str(gen_nonce())]
                logging.info("Sending interest on : {}".format(Name.to_str(name)))
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
        logging.info("Insert {} names. Delete {} names,".format(len(insert_list), len(delete_list)))

        cur_time = WriteHandle.get_current_time()
        data_names = [Name.to_str(insert_param.data_name) for insert_param in insert_list]
        names = [Name.to_str(insert_param.name) for insert_param in insert_list]
        expire_times = [cur_time + int(insert_param.expire_time_ms) for insert_param in insert_list]
        self.storage.put_batch(data_names, names, expire_times)

        data_names = [Name.to_str(delete_param.data_name) for delete_param in delete_list]
        names = [Name.to_str(delete_param.name) for delete_param in delete_list]
        self.storage.remove_batch(data_names, names)

        self.processes[nonce] = True

    def _on_check(self, int_name: FormalName, int_param: InterestParam, app_param: Optional[BinaryStr]):
        """
        Handler for status check requests from insertion clients.
        :param int_name:
        :param int_param:
        :param app_param:
        :return:
        """
        process_id = int(Component.to_str(int_name[-2]))
        if process_id not in self.processes:
            response = CatalogResponseParameter()
            response.status = 404
            self.app.put_data(int_name, response.encode(), freshness_period=500)
            return

        status = self.processes[process_id]
        response = CatalogResponseParameter()
        if status:
            response.status = 200
            self.app.put_data(int_name, response.encode(), freshness_period=500)
        else:
            response.status = 201
            self.app.put_data(int_name, response.encode(), freshness_period=500)

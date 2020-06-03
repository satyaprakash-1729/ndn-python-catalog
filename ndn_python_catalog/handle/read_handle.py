import asyncio as aio
from ndn.app import NDNApp
from ..storage import SqliteStorage
from ndn.encoding import FormalName, InterestParam, BinaryStr, Name
from typing import Optional
from ..command import CatalogRequestParameter
import logging


class ReadHandle(object):
    """
    Handles all data to name mapping requests from clients. Reads the SQLite table for mappings
    and returns a list of mappings found separated by |.
    """
    def __init__(self, app: NDNApp, storage: SqliteStorage, prefix: str):
        self.app = app
        self.storage = storage
        aio.ensure_future(self.listen(Name.from_str(prefix)))

    async def listen(self, prefix):
        """
        Starts listening on the catalog's prefix for "query" requests.
        :param prefix: Prefix of the catalog.
        """
        logging.info("REGISTERED TO: {}".format(Name.to_str(prefix + ['query'])))
        self.app.route(prefix + ['query'])(self._on_interest)

    def _on_interest(self, int_name: FormalName, int_param: InterestParam, app_param: Optional[BinaryStr]):
        """
        Callback for query interest.
        :param int_name:
        :param int_param:
        :param app_param:
        :return:
        """
        aio.ensure_future(self._process_interest(int_name, int_param, app_param))

    async def _process_interest(self, int_name: FormalName, int_param: InterestParam, app_param: Optional[BinaryStr]):
        """
        Extracts the data name from the app params, and queries database for mappings.
        The mappings are then sent delimited by |.
        If nothing found empty data returned.
        :param int_name:
        :param int_param:
        :param app_param:
        :return:
        """
        print("------------------------------------------------------------------")
        app_param_parsed = CatalogRequestParameter.parse(app_param)
        data_name = app_param_parsed.data_name

        query_key = Name.to_str(data_name)
        logging.info("Name recvd: {}".format(query_key))
        name_bytes = self.storage.get(query_key)
        if name_bytes is not None:
            response = "|".join(name_bytes)
            logging.info("Data Sent: {}".format(response))
            self.app.put_data(int_name, content=response.encode(), freshness_period=500)
        else:
            self.app.put_data(int_name, content="".encode(), freshness_period=500)

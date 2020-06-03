import os
import sys
import logging
sys.path.insert(1, os.path.join(sys.path[0], '..'))
import asyncio as aio
from ndn.app import NDNApp
from ndn.encoding import Name, FormalName, InterestParam, BinaryStr
from typing import Optional, List, Tuple
from ndn.types import InterestNack, InterestTimeout
from command.catalog_command import CatalogCommandParameter, CatalogResponseParameter,\
    CatalogDataListParameter, CatalogInsertParameter, CatalogDeleteParameter
from ndn.security import KeychainDigest
from ndn.utils import gen_nonce


def config_logging():
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)


class CommandChecker(object):
    def __init__(self, prefix: str, app: NDNApp, insert_data_names: List[CatalogInsertParameter],
                 delete_data_names: List[CatalogDeleteParameter], catalog_name: str):
        self.app = app
        self.insert_data_names = insert_data_names
        self.delete_data_names = delete_data_names
        self.prefix = prefix
        self.catalog_name = catalog_name
        self.nonce = 0

    async def listen(self):
        """
        Starts listening for /prefix/fetch_map interests and sends insertion data to
        the catalog when requests is received.
        """
        name = Name.from_str(self.prefix) + ["fetch_map"]
        logging.debug("Listening: {}".format(Name.to_str(name)))
        self.app.route(name)(self._on_interest)

    async def check_insert(self) -> CatalogResponseParameter:
        """
        Sends an interest to the catalog and waits for acknowledgement which is basically an
        empty data packet. Once it gets an acknowledgement it knows that the catalog received the
        request. The module then does nothing and waits for data request from the catalog. Once
        the request is received the client responds with a list of insertions and deletions.
        :param catalog_name: the name of the catalog to which to send the insertion request.
        """
        method = 'insert'
        cmd_param = CatalogCommandParameter()
        cmd_param.name = self.prefix
        cmd_param_bytes = cmd_param.encode()

        name = Name.from_str(self.catalog_name)
        name += [method]
        self.nonce = gen_nonce()
        name += [str(self.nonce)]
        logging.info("Name: {}".format(Name.to_str(name)))
        try:
            aio.ensure_future(self.send_interest(name, cmd_param_bytes))
        except InterestNack:
            logging.debug(">>>NACK")
            return
        except InterestTimeout:
            logging.debug(">>>TIMEOUT")
            return

    async def send_interest(self, name: FormalName, cmd_param_bytes: bytes):
        """
        Sends interest to the catalog.
        :param name: name to send the interest to
        :param cmd_param_bytes: app parameters containing client prefix.
        """
        _, _, data_bytes = await self.app.express_interest(
            name, app_param=cmd_param_bytes, must_be_fresh=True, can_be_prefix=False)
        logging.info("> ACK RECVD: {}".format(bytes(data_bytes)))

    def _on_interest(self, int_name: FormalName, int_param: InterestParam, app_param: Optional[BinaryStr]):
        """
        Callback for data request from Catalog.
        :param int_name: the interest name received.
        :param int_param: the interest params received.
        :param app_param: the app params received.
        """
        logging.info("FETCH REQUEST {}".format(Name.to_str(int_name)))
        aio.ensure_future(self._process_interest(int_name, int_param, app_param))

    async def _process_interest(self, int_name: FormalName, int_param: InterestParam, app_param: Optional[BinaryStr]):
        """
        Makes a new CatalogDataListParameter object containing all the insertion params and deletion params.
        Every insert parameter contains the data name, the name to map the data to and the expiry time for
        insertions. Also, checks the status of insertion request.
        :param int_name: the interest name received.
        :param int_param: the interest params received.
        :param app_param: the app params received.
        """
        cmd_param = CatalogDataListParameter()
        cmd_param.insert_data_names = self.insert_data_names
        cmd_param.delete_data_names = self.delete_data_names
        cmd_param = cmd_param.encode()

        self.app.put_data(int_name, bytes(cmd_param), freshness_period=500)

        # CHECK STATUS
        await aio.sleep(5)
        logging.info("Status Check Request Sent...")
        name = Name.from_str(self.catalog_name)
        name += ['check']
        name += [str(self.nonce)]
        name += [str(gen_nonce())]
        _, _, data_bytes = await self.app.express_interest(
            name, must_be_fresh=True, can_be_prefix=False)
        response = CatalogResponseParameter.parse(data_bytes)
        logging.info("Status Received: {}".format(response.status))
        self.app.shutdown()


def create_insert_parameter(data_name: str, name: str, expire_time_ms: int):
    """
    Creates an insertion param.
    :param data_name:
    :param name:
    :param expire_time_ms:
    :return: the insertion param.
    """
    param = CatalogInsertParameter()
    param.data_name = data_name
    param.name = name
    param.expire_time_ms = expire_time_ms
    return param


def create_delete_parameter(data_name: str, name: str):
    """
    Creates a deletion param.
    :param data_name:
    :param name:
    :return: the deletion param.
    """
    param = CatalogDeleteParameter()
    param.data_name = data_name
    param.name = name
    return param


def get_time(hrs: int, mins: int, secs: int):
    """
    Gives the time in seconds for hr:min:sec
    :param hrs:
    :param mins:
    :param secs:
    :return: time in seconds
    """
    return (hrs*60 + mins)*60 + secs


if __name__ == "__main__":
    config_logging()
    app = NDNApp()
    commChecker = CommandChecker("producer", app, [create_insert_parameter("data30", "testrepo", get_time(0, 150, 0)),
                                                   create_insert_parameter("data24", "testrepo", get_time(0, 150, 0))],
                                 [create_delete_parameter("data24", "testrepo1")], "/catalog")
    aio.ensure_future(commChecker.listen())
    app.run_forever(after_start=commChecker.check_insert())

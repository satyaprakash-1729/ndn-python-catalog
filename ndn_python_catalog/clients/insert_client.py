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
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)


class CommandChecker(object):
    def __init__(self, prefix: str, app: NDNApp, insert_data_names: List[CatalogInsertParameter],
                 delete_data_names: List[CatalogDeleteParameter]):
        self.app = app
        self.insert_data_names = insert_data_names
        self.delete_data_names = delete_data_names
        self.prefix = prefix

    async def listen(self):
        name = Name.from_str(self.prefix) + ["fetch_map"]
        logging.debug("Listening: ", Name.to_str(name))
        self.app.route(name)(self._on_interest)

    async def check_insert(self, catalog_name: str) -> CatalogResponseParameter:
        method = 'insert'
        cmd_param = CatalogCommandParameter()
        cmd_param.name = self.prefix
        cmd_param_bytes = cmd_param.encode()

        name = Name.from_str(catalog_name)
        name += [method]
        name += [str(gen_nonce())]
        logging.debug("Name: {}".format(Name.to_str(name)))
        try:
            aio.ensure_future(self.send_interest(name, cmd_param_bytes))
        except InterestNack:
            logging.debug(">>>NACK")
            return None
        except InterestTimeout:
            logging.debug(">>>TIMEOUT")
            return None
        # return cmd_response

    async def send_interest(self, name: FormalName, cmd_param_bytes: bytes):
        _, _, data_bytes = await self.app.express_interest(
            name, app_param=cmd_param_bytes, must_be_fresh=True, can_be_prefix=False)
        logging.debug("> ACK RECVD: {}".format(bytes(data_bytes)))

    def _on_interest(self, int_name: FormalName, int_param: InterestParam, app_param: Optional[BinaryStr]):
        logging.debug("> FETCH REQUEST {}".format(int_name))
        aio.ensure_future(self._process_interest(int_name, int_param, app_param))

    async def _process_interest(self, int_name: FormalName, int_param: InterestParam, app_param: Optional[BinaryStr]):
        cmd_param = CatalogDataListParameter()
        cmd_param.insert_data_names = self.insert_data_names
        cmd_param.delete_data_names = self.delete_data_names
        cmd_param = cmd_param.encode()

        self.app.put_data(int_name, bytes(cmd_param), freshness_period=500)


def create_insert_parameter(data_name: str, name: str, expire_time_ms: int):
    param = CatalogInsertParameter()
    param.data_name = data_name
    param.name = name
    param.expire_time_ms = expire_time_ms
    return param


def create_delete_parameter(data_name: str, name: str):
    param = CatalogDeleteParameter()
    param.data_name = data_name
    param.name = name
    return param


def get_time(hrs: int, mins: int, secs: int):
    return (hrs*60 + mins)*60 + secs


if __name__ == "__main__":
    config_logging()
    app = NDNApp()
    commChecker = CommandChecker("producer", app, [create_insert_parameter("data5", "testrepo3", get_time(0, 5, 0)),
                                                   create_insert_parameter("data5", "testrepo8", get_time(0, 5, 0))],
                                 [])
    aio.ensure_future(commChecker.listen())
    app.run_forever(after_start=commChecker.check_insert("/catalog"))

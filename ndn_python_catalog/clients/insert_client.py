import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], '..'))
import asyncio as aio
from ndn.app import NDNApp
from ndn.encoding import Name, FormalName, InterestParam, BinaryStr
from typing import Optional, List
from ndn.types import InterestNack, InterestTimeout
from command.catalog_command import CatalogCommandParameter, CatalogResponseParameter, CatalogDataListParameter
from ndn.security import KeychainDigest
from ndn.utils import gen_nonce


class CommandChecker(object):
    def __init__(self, prefix: str, app: NDNApp, insert_data_names: List[str], delete_data_names: List[str]):
        self.app = app
        self.insert_data_names = insert_data_names
        self.delete_data_names = delete_data_names
        self.prefix = prefix

    async def listen(self):
        name = Name.from_str(self.prefix) + ["fetch_map"]
        print("Listening: ", Name.to_str(name))
        self.app.route(name)(self._on_interest)

    async def check_insert(self, catalog_name: str) -> CatalogResponseParameter:
        method = 'insert'
        cmd_param = CatalogCommandParameter()
        cmd_param.repo_name = self.prefix
        cmd_param_bytes = cmd_param.encode()

        name = Name.from_str(catalog_name)
        name += [method]
        name += [str(gen_nonce())]
        print(">>>>>>>>>", Name.to_str(name))
        try:
            aio.ensure_future(self.send_interest(name))
        except InterestNack:
            print(">>>NACK")
            return None
        except InterestTimeout:
            print(">>>TIMEOUT")
            return None
        # return cmd_response

    async def send_interest(self, name: FormalName):
        _, _, data_bytes = await self.app.express_interest(
            name, must_be_fresh=True, can_be_prefix=True)
        print(">>> ACK RECVD: ", bytes(data_bytes))

    def _on_interest(self, int_name: FormalName, int_param: InterestParam, app_param: Optional[BinaryStr]):
        print(">>>> FETCH REQUEST", int_name)
        aio.ensure_future(self._process_interest(int_name, int_param, app_param))

    async def _process_interest(self, int_name: FormalName, int_param: InterestParam, app_param: Optional[BinaryStr]):
        cmd_param = CatalogDataListParameter()
        cmd_param.name = self.prefix
        cmd_param.insert_data_names = self.insert_data_names
        cmd_param.dummy = 0
        cmd_param.delete_data_names = self.delete_data_names
        cmd_param = cmd_param.encode()

        self.app.put_data(int_name, bytes(cmd_param), freshness_period=0)


if __name__ == "__main__":
    app = NDNApp(keychain=KeychainDigest())
    commChecker = CommandChecker("testrepo", app, [], ["data4", "data5"])
    aio.ensure_future(commChecker.listen())
    app.run_forever(after_start=commChecker.check_insert("/catalog16"))

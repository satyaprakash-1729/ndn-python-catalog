import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from ndn.app import NDNApp
from ndn.encoding import Name
from ndn.types import InterestNack, InterestTimeout
from command.catalog_command import *


class InterestChecker(object):
    def __init__(self, app: NDNApp):
        self.app = app

    async def check_interest(self, data_name: str, catalog_name: str):
        return await self._check(data_name, catalog_name)

    async def _check(self, repo_name: str,
                     catalog_name: str):

        cmd_param = CatalogRequestParameter()
        cmd_param.data_name = 'data1'
        cmd_param_bytes = cmd_param.encode()

        name = Name.from_str(catalog_name)
        try:
            _, _, data_bytes = await self.app.express_interest(
                    name, app_param=cmd_param_bytes, must_be_fresh=True, can_be_prefix=True, lifetime=6000)
            print("DATA Recvd: ", data_bytes.decode('utf-8'))
        except InterestNack:
            print(">>>NACK")
            return None
        except InterestTimeout:
            print(">>>TIMEOUT")
            return None
        finally:
            app.shutdown()
        # return cmd_response


if __name__ == "__main__":
    app = NDNApp()
    intChecker = InterestChecker(app)
    app.run_forever(after_start=intChecker.check_interest("data1", "/catalog1"))

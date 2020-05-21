import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from ndn.app import NDNApp
from ndn.encoding import Name
from ndn.types import InterestNack, InterestTimeout
from command.catalog_command import *
from ndn.security import KeychainDigest
from ndn.utils import gen_nonce


class InterestChecker(object):
    def __init__(self, app: NDNApp):
        self.app = app

    async def check_interest(self, data_name: str, catalog_name: str, repo_name: str):
        return await self._check(data_name, catalog_name, "query", repo_name)

    async def _check(self, data_name: str,
                     catalog_name: str, method: str, repo_name: str):

        cmd_param = CatalogRequestParameter()
        cmd_param.data_name = 'data1'
        cmd_param_bytes = cmd_param.encode()

        name = Name.from_str(catalog_name)
        name += [method]
        name += [str(gen_nonce())]
        print("Sending interest to ", Name.to_str(name))
        try:
            _, _, data_bytes = await self.app.express_interest(
                    name, must_be_fresh=True, can_be_prefix=True, lifetime=10000)
            data_recvd = bytes(data_bytes)
            print(data_recvd)
            assert bytes(repo_name, encoding='utf-8') == data_recvd
            print("Repo Name Correct!")
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
    app = NDNApp(keychain=KeychainDigest())
    intChecker = InterestChecker(app)
    app.run_forever(after_start=intChecker.check_interest("data20", "/catalog16", repo_name="/testrepo"))

import os
import sys
import logging
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from ndn.app import NDNApp
from ndn.encoding import Name
from ndn.types import InterestNack, InterestTimeout
from command.catalog_command import *
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


class InterestChecker(object):
    def __init__(self, app: NDNApp):
        self.app = app

    async def check_interest(self, data_name: str, catalog_name: str):
        return await self._check(data_name, catalog_name, "query")

    async def _check(self, data_name: str,
                     catalog_name: str, method: str):
        """
        Sends an interest with the given data name in the app parameters to the catalog.
        The catalog responds with a list of repo forwarding hints that hold this data.
        :param data_name: the data name to repo name mapping to be requested from the catalog
        :param catalog_name: name / prefix of the catalog
        :param method: whether insert or query interest
        """
        cmd_param = CatalogRequestParameter()
        cmd_param.data_name = data_name
        cmd_param_bytes = cmd_param.encode()

        name = Name.from_str(catalog_name)
        name += [method]
        name += [str(gen_nonce())]
        logging.debug("Sending interest to {}".format(Name.to_str(name)))
        try:
            _, _, data_bytes = await self.app.express_interest(
                    name, app_param=cmd_param_bytes, must_be_fresh=True, can_be_prefix=False, lifetime=4000)
            data_recvd = bytes(data_bytes)
            logging.debug("Data Recvd: {}".format(data_recvd))
        except InterestNack:
            logging.debug(">>>NACK")
            return
        except InterestTimeout:
            logging.debug(">>>TIMEOUT")
            return
        finally:
            app.shutdown()


if __name__ == "__main__":
    config_logging()
    app = NDNApp()
    intChecker = InterestChecker(app)
    app.run_forever(after_start=intChecker.check_interest("data5", "/catalog"))

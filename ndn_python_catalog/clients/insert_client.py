import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from ndn.app import NDNApp
from ndn.encoding import NonStrictName, Component, DecodeError, NameField, TlvModel
from ndn.types import InterestNack, InterestTimeout
from command.catalog_command import CatalogCommandParameter, CatalogResponseParameter


class CommandChecker(object):
    def __init__(self, app: NDNApp):
        self.app = app

    async def check_insert(self, repo_name: NonStrictName, catalog_name: NonStrictName) -> CatalogResponseParameter:
        return await self._check('insert', repo_name, catalog_name)

    async def _check(self, method: str, repo_name: str,
                     catalog_name: str):
        cmd_param = CatalogCommandParameter()
        cmd_param.data_name = 'data1'
        cmd_param.repo_name = repo_name
        cmd_param_bytes = cmd_param.encode()

        name = [Component.from_str(catalog_name)]
        print(">>>>>>>>>", name)
        name.append(Component.from_str(method))
        print(">>>>>>>>>", name)
        # name.append(Component.from_bytes(cmd_param_bytes))
        # print(">>>>>>>>>", name)
        try:
            data_name, meta_info, content = await self.app.express_interest(
                    name, app_param=cmd_param_bytes, must_be_fresh=False, can_be_prefix=False, lifetime=1000)
            # try:
            #     cmd_response = CatalogResponseParameter.parse(content)
            # except DecodeError:
            #     return None
            # except Exception:
            #     pass
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
    commChecker = CommandChecker(app)
    app.run_forever(after_start=commChecker.check_insert("testrepo", "catalog1"))

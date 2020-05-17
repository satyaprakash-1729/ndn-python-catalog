import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from ndn.app import NDNApp
from ndn.encoding import NonStrictName, Component, DecodeError
from ndn.types import InterestNack, InterestTimeout
from command.catalog_command import CatalogCommandParameter, CatalogResponseParameter


class CommandChecker(object):
    def __init__(self, app: NDNApp):
        self.app = app

    async def check_insert(self, repo_name: NonStrictName) -> CatalogResponseParameter:
        return await self._check('insert', repo_name)

    async def _check(self, method: str, repo_name: NonStrictName) -> CatalogResponseParameter:
        cmd_param = CatalogCommandParameter()
        cmd_param.data_name = '/data1'
        cmd_param.repo_name = repo_name
        cmd_param_bytes = cmd_param.encode()

        name = repo_name[:]
        name.append(method)
        name.append(Component.from_bytes(cmd_param_bytes))

        try:
            data_name, meta_info, content = await self.app.express_interest(
                name, must_be_fresh=True, can_be_prefix=False, lifetime=1000)
        except InterestNack as e:
            return None
        except InterestTimeout:
            return None

        try:
            cmd_response = CatalogResponseParameter.parse(content)
        except DecodeError as exc:
            return None
        except Exception as e:
            pass
        return cmd_response


if __name__ == "__main__":
    app = NDNApp()
    commChecker = CommandChecker(app)
    commChecker.check_insert("testrepo")
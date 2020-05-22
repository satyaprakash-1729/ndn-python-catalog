import asyncio as aio
from ndn.app import NDNApp
from ..storage import SqliteStorage
from ndn.encoding import FormalName, InterestParam, BinaryStr, Name
from typing import Optional
from ..command import CatalogRequestParameter


class ReadHandle(object):
    def __init__(self, app: NDNApp, storage: SqliteStorage, prefix: str):
        self.app = app
        self.storage = storage
        aio.ensure_future(self.listen(Name.from_str(prefix)))

    async def listen(self, prefix):
        print("REGISTERED TO: ", Name.to_str(prefix + ['query']))
        self.app.route(prefix + ['query'])(self._on_interest)

    def _on_interest(self, int_name: FormalName, int_param: InterestParam, app_param: Optional[BinaryStr]):
        aio.ensure_future(self._process_interest(int_name, int_param, app_param))

    async def _process_interest(self, int_name: FormalName, int_param: InterestParam, app_param: Optional[BinaryStr]):
        app_param_parsed = CatalogRequestParameter.parse(app_param)
        data_name = app_param_parsed.data_name

        query_key = Name.to_str(data_name)
        name_bytes = self.storage.get(query_key)
        print(name_bytes)
        if name_bytes is not None:
            self.app.put_data(int_name, content=name_bytes.encode(), freshness_period=500)
        else:
            self.app.put_data(int_name, content="".encode(), freshness_period=500)

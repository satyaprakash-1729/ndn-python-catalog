import asyncio
import logging
from ndn.app import NDNApp
from ndn.encoding import Name, Component

from catalog_command import CatalogCommandParameter, CatalogResponseParameter
from ndn_python_repo.storage import Storage


class CommandHandle(object):
    def __init__(self, app: NDNApp, storage: Storage):
        self.app = app
        self.storage = storage
        self.m_processes = dict()

    async def listen(self, prefix: Name):
        raise NotImplementedError

    def reply_with_response(self, int_name, response: CatalogResponseParameter):
        logging.info('Reply to command: {}'.format(Name.to_str(int_name)))
        response_bytes = response.encode()
        self.app.put_data(int_name, response_bytes, freshness_period=1000)

    @staticmethod
    def decode_cmd_param_bytes(name) -> CatalogCommandParameter:
        param_bytes = Component.get_value(name[-1])
        return CatalogCommandParameter.parse(param_bytes)

    async def schedule_delete_process(self, process_id: int):
        await asyncio.sleep(60)
        if process_id in self.m_processes:
            del self.m_processes[process_id]

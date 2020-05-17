import asyncio as aio
import logging
from ndn.app import NDNApp
from ndn.encoding import Name
from ndn_python_repo.storage import Storage


class ReadHandle(object):
    def __init__(self, app: NDNApp, storage: Storage):
        self.app = app
        self.storage = storage
        self.listen(Name.from_str('/'))

    def listen(self, prefix):
        self.app.route(prefix)(self._on_interest)
        logging.info(f'Read handle: listening to {Name.to_str(prefix)}')

    def unlisten(self, prefix):
        aio.ensure_future(self.app.unregister(prefix))
        logging.info(f'Read handle: stop listening to {Name.to_str(prefix)}')

    def _on_interest(self, int_name, int_param, _app_param):
        if int_param.must_be_fresh:
            return
        data_bytes = self.storage.get_data_packet(int_name, int_param.can_be_prefix)
        if data_bytes is None:
            return
        self.app.put_raw_packet(data_bytes)
        logging.info(f'Read handle: serve data {Name.to_str(int_name)}')

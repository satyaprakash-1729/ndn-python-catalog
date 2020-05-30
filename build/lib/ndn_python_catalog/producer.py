from ndn.app import NDNApp
from ndn.encoding import Name, NonStrictName, Component, InterestParam
from typing import List
import asyncio as aio

class Producer(object):
	def __init__(self, app: NDNApp, prefix: NonStrictName, data_names: List[NonStrictName]):
		self.app = app
		self.prefix = prefix
		self.data_names = data_names

	def listen(self):
		for data_name in data_names:
			self.app.route(self.prefix + data_name)(self._on_interest)
			print(">>> LISTENING FOR: ", self.prefix + data_name)

	def _on_interest(self, int_name, int_param, app_param):
		aio.ensure_future(self._process_msg_interest(int_name, int_param, app_param))

	async def _process_msg_interest(self, int_name, int_param, app_param):
		content = "hello world".encode()
		self.app.put_data(int_name, content=content, freshness_period=10000)
		print("Interest Recvd: ", int_name)


if __name__ == "__main__":
	app = NDNApp()
	prefix = "/producer1"
	data_names = ["/A/B", "/A/C"]
	producer = Producer(app, prefix, data_names)
	producer.listen()
	try:
		app.run_forever()
	except FileNotFoundError:
		print('Error: could not connect to NFD.')

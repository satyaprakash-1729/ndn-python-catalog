from ndn.app import NDNApp
from ndn.encoding import Name, NonStrictName, Component, InterestParam
from ndn.types import InterestNack, InterestTimeout, InterestCanceled, ValidationFailure
from typing import List
import ndn.utils
import asyncio as aio


class Consumer(object):
	def __init__(self, app: NDNApp, name: NonStrictName):
		self.name = name
		self.app = app

	async def send_interest(self, prefix):
		try:
			timestamp = ndn.utils.timestamp()
			int_name = Name.from_str(prefix)
			print(">>>> ", Name.to_str(int_name))
			data_name, meta, content = await self.app.express_interest(int_name, must_be_fresh=True, can_be_prefix=True, lifetime=6000)
			if content is not None:
				print("DATA: ", Name.to_str(data_name), " -- ", bytes(content))
		except InterestNack as e:
			print(f'Nacked with reason={e.reason}')
		except InterestTimeout:
			print(f'Timeout')
		except InterestCanceled:
			print(f'Canceled')
		except ValidationFailure:
			print(f'Data failed to validate')
		finally:
			app.shutdown()


if __name__ == "__main__":
	app = NDNApp()
	consumer = Consumer(app, "consumer1")
	app.run_forever(after_start=consumer.send_interest('/producer1/A/C'))

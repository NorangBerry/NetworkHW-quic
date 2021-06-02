import asyncio

import time
from http3_client import run
from typing import Deque, Dict, Optional
from aioquic.asyncio.client import connect
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.h3.events import H3Event
from aioquic.quic.configuration import QuicConfiguration
from aioquic.h3.connection import H3_ALPN
import os 
import datetime

from aioquic.quic.connection import QuicConnection
import httpx
from aioquic.h3.connection import H3_ALPN, H3Connection

HTTP2_URLS=['https://172.17.90.8:8000']
HTTP3_URLS=['https://172.17.90.8:8001']
PATHS = ['/']
async def quic():
	configuration = QuicConfiguration(
		is_client=True, alpn_protocols= H3_ALPN
	)
	for url in HTTP3_URLS:
		for path in PATHS:
			await run(configuration=configuration,url=f'{url}{path}')
	# http3_loop = asyncio.get_event_loop()
	# http3_loop.run_until_complete(
	# 			run(configuration=configuration)
	# )
async def http2():
	async with httpx.AsyncClient(http2=True, verify=False) as client:
		for url in HTTP2_URLS:
			before = datetime.datetime.now()
			for path in PATHS:
				await client.get(f'{url}{path}')
				after = datetime.datetime.now()
				print(f'http2: {(after-before).total_seconds() * 1000}')


if __name__ == "__main__":
	for i in range(5):
		http2_loop = asyncio.new_event_loop()
		http2_loop.run_until_complete(
					http2()
			)
		http3_loop = asyncio.new_event_loop()
		http3_loop.run_until_complete(
					quic()
			)
		time.sleep(2)
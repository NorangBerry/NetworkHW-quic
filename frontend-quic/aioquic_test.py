import asyncio
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

async def quic():
	configuration = QuicConfiguration(
		is_client=True, alpn_protocols= H3_ALPN
	)
	await run(configuration=configuration)
	# http3_loop = asyncio.get_event_loop()
	# http3_loop.run_until_complete(
	# 			run(configuration=configuration)
	# )
async def http2():
	async with httpx.AsyncClient(http2=True, verify=False) as client:
		before = datetime.datetime.now()
		await client.get('https://192.168.0.2:8000')
		after = datetime.datetime.now()
		print(f'http2: {(after-before).total_seconds() * 1000}')


if __name__ == "__main__":
	http2_loop = asyncio.new_event_loop()
	http2_loop.run_until_complete(
				http2()
		)
	http3_loop = asyncio.new_event_loop()
	http3_loop.run_until_complete(
				quic()
		)
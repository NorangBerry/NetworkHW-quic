import asyncio

import time
import csv
from http3_client import run
from aioquic.quic.configuration import QuicConfiguration
from aioquic.h3.connection import H3_ALPN
import datetime

import httpx
from aioquic.h3.connection import H3_ALPN

HTTP2_URLS=['https://172.17.90.8:8000']
HTTP3_URLS=['https://172.17.90.8:8001']
PATHS = ['/','/image']

async def quic(index):
	configuration = QuicConfiguration(
		is_client=True, alpn_protocols= H3_ALPN
	)
	ret = {'INDEX':index,'TYPE':'QUIC'}
	for url in HTTP3_URLS:
		for j, path in enumerate(PATHS):
			ret[f'PATH{j}'] = f'{url}{path}'
			diff = await run(configuration=configuration,url=f'{url}{path}')
			ret[f'TIME{j}'] = diff
	return ret

async def http2(index):
	ret = {'INDEX':index,'TYPE':'HTTP2'}
	async with httpx.AsyncClient(http2=True, verify=False) as client:
		for url in HTTP2_URLS:
			before = datetime.datetime.now()
			for j, path in enumerate(PATHS):
				ret[f'PATH{j}'] = f'{url}{path}'
				res = await client.get(f'{url}{path}')
				after = datetime.datetime.now()
				diff = int((after-before).total_seconds() * 1000)
				print(f'http2/{path}: {diff}')
				ret[f'TIME{j}'] = diff
	return ret

def write_csv(ret_tcp,ret_quic):
	with open('out.csv','a') as fd:
		writer = csv.DictWriter(fd, fieldnames=ret_tcp.keys())
		writer.writerow(ret_tcp)
		writer.writerow(ret_quic)

if __name__ == "__main__":
	for i in range(5):
		http2_loop = asyncio.new_event_loop()
		ret_tcp = http2_loop.run_until_complete(
					http2(i)
			)
		http3_loop = asyncio.new_event_loop()
		ret_quic = http3_loop.run_until_complete(
					quic(i)
			)
		write_csv(ret_tcp,ret_quic)
		time.sleep(60*10)

import asyncio

import time
import csv
from http3_client import run
from aioquic.quic.configuration import QuicConfiguration
from aioquic.h3.connection import H3_ALPN
import datetime

import httpx
from aioquic.h3.connection import H3_ALPN

HTTP2_URLS=['https://?:8000', 'https://??:8000']
HTTP3_URLS=['https://?:8001', 'https://??:8001']
PATHS = ['/','/image']

async def quic(index):
	configuration = QuicConfiguration(
		is_client=True, alpn_protocols= H3_ALPN
	)
	ret = []
	for url in HTTP3_URLS:
		json = {'INDEX':index,'TYPE':'QUIC', "URL":url}
		for j, path in enumerate(PATHS):
			json[f'PATH{j}'] = f'{path}'
			diff = await run(configuration=configuration,url=f'{url}{path}')
			json[f'TIME{j}'] = diff
		ret.append(json)
	return ret

async def http2(index):
	ret = []
	async with httpx.AsyncClient(http2=True, verify=False) as client:
		for url in HTTP2_URLS:
			json = {'INDEX':index,'TYPE':'HTTP2', "URL":url}
			before = datetime.datetime.now()
			for j, path in enumerate(PATHS):
				json[f'PATH{j}'] = f'{url}{path}'
				res = await client.get(f'{url}{path}')
				after = datetime.datetime.now()
				diff = int((after-before).total_seconds() * 1000)
				print(f'http2/{path}: {diff}')
				json[f'TIME{j}'] = diff
			ret.append(json)
	return ret

def write_csv(ret_tcp,ret_quic):
	with open('out.csv','a') as fd:
		writer = csv.DictWriter(fd, fieldnames=ret_tcp[0].keys())
		for row in ret_tcp:
			writer.writerow(row)
		for row in ret_quic:
			writer.writerow(row)

if __name__ == "__main__":
	for i in range(100):
		http2_loop = asyncio.new_event_loop()
		ret_tcp = http2_loop.run_until_complete(
					http2(i)
			)
		http3_loop = asyncio.new_event_loop()
		ret_quic = http3_loop.run_until_complete(
					quic(i)
			)
		write_csv(ret_tcp,ret_quic)
		time.sleep(60*1)

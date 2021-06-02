import argparse
import asyncio
import os
import pickle
import ssl
import time
from collections import deque
from typing import BinaryIO, Callable, Deque, Dict, List, Optional, cast
from urllib.parse import urlparse

import wsproto
import wsproto.events

import aioquic
from aioquic.asyncio.client import connect
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.h3.connection import H3_ALPN, H3Connection
from aioquic.h3.events import (
	DataReceived,
	H3Event,
	HeadersReceived,
	PushPromiseReceived,
)
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import QuicEvent
from aioquic.tls import CipherSuite, SessionTicket

USER_AGENT = "aioquic/" + aioquic.__version__


class URL:
	def __init__(self, url: str) -> None:
		parsed = urlparse(url)

		self.authority = parsed.netloc
		self.full_path = parsed.path
		if parsed.query:
			self.full_path += "?" + parsed.query
		self.scheme = parsed.scheme


class HttpRequest:
	def __init__(
		self, method: str, url: URL, content: bytes = b"", headers: Dict = {}
	) -> None:
		self.content = content
		self.headers = headers
		self.method = method
		self.url = url

class HttpClient(QuicConnectionProtocol):
	def __init__(self, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)

		self.pushes: Dict[int, Deque[H3Event]] = {}
		self._http: Optional[H3Connection] = None
		self._request_events: Dict[int, Deque[H3Event]] = {}
		self._request_waiter: Dict[int, asyncio.Future[Deque[H3Event]]] = {}

		self._http = H3Connection(self._quic)

	async def get(self, url: str, headers: Dict = {}) -> Deque[H3Event]:
		"""
		Perform a GET request.
		"""
		return await self._request(
			HttpRequest(method="GET", url=URL(url), headers=headers)
		)

	def http_event_received(self, event: H3Event) -> None:
		if isinstance(event, (HeadersReceived, DataReceived)):
			stream_id = event.stream_id
			if stream_id in self._request_events:
				# http
				self._request_events[event.stream_id].append(event)
				if event.stream_ended:
					request_waiter = self._request_waiter.pop(stream_id)
					request_waiter.set_result(self._request_events.pop(stream_id))

			elif event.push_id in self.pushes:
				# push
				self.pushes[event.push_id].append(event)

		elif isinstance(event, PushPromiseReceived):
			self.pushes[event.push_id] = deque()
			self.pushes[event.push_id].append(event)

	def quic_event_received(self, event: QuicEvent) -> None:
		#	pass event to the HTTP layer
		if self._http is not None:
			for http_event in self._http.handle_event(event):
				self.http_event_received(http_event)

	async def _request(self, request: HttpRequest) -> Deque[H3Event]:
		stream_id = self._quic.get_next_available_stream_id()
		self._http.send_headers(
			stream_id=stream_id,
			headers=[
				(b":method", request.method.encode()),
				(b":scheme", request.url.scheme.encode()),
				(b":authority", request.url.authority.encode()),
				(b":path", request.url.full_path.encode()),
			],
			end_stream=True
		)
		waiter = self._loop.create_future()
		self._request_events[stream_id] = deque()
		self._request_waiter[stream_id] = waiter
		
		self.transmit()

		return await asyncio.shield(waiter)


async def perform_http_request(
	client: HttpClient,
	url: str
) -> None:
	# perform request
	start = time.time()
	http_events = await client.get(url)
	elapsed = time.time() - start
	parsed = urlparse(url)
	print(f'http3/{parsed.path}: {elapsed*1000}')

	# print speed
	octets = 0
	for http_event in http_events:
		if isinstance(http_event, DataReceived):
			octets += len(http_event.data)
			


def process_http_pushes(
	client: HttpClient,
) -> None:
	for _, http_events in client.pushes.items():
		octets = 0
		for http_event in http_events:
			if isinstance(http_event, DataReceived):
				octets += len(http_event.data)
			elif isinstance(http_event, PushPromiseReceived):
				for header, value in http_event.headers:
					if header == b":method":
						method = value.decode()
					elif header == b":path":
						path = value.decode()

		# output response
		write_response(
			http_events=http_events
		)


def write_response(
	http_events: Deque[H3Event]
) -> None:
	for http_event in http_events:
		if isinstance(http_event, HeadersReceived):
			headers = b""
			for k, v in http_event.headers:
				headers += k + b": " + v + b"\r\n"
			if headers:
				print(headers)
		elif isinstance(http_event, DataReceived):
			print(http_event.data)


def save_session_ticket(ticket: SessionTicket) -> None:
	"""
	Callback which is invoked by the TLS engine when a new session ticket
	is received.
	"""

async def run(
	configuration: QuicConfiguration,
	url:str
) -> None:
	# parse URL
	parsed = urlparse(url)
	assert parsed.scheme in (
		"https",
		"wss",
	), "Only https:// or wss:// URLs are supported."
	host = parsed.hostname
	port = parsed.port
	dir_path = os.path.dirname(os.path.realpath(__file__))
	pem_path = os.path.join(dir_path,"../backend-express/public.pem")
	configuration.load_verify_locations(pem_path)
	async with connect(
		host,
		port,
		configuration=configuration,
		create_protocol=HttpClient,
	) as client:
		client = cast(HttpClient, client)
		# perform request
		coros = [
			perform_http_request(
				client=client,
				url=url,
			)
		]
		await asyncio.gather(*coros)

		# process http pushes
		process_http_pushes(client=client)


if __name__ == "__main__":
	# prepare configuration
	configuration = QuicConfiguration(
		is_client=True, alpn_protocols= H3_ALPN
	)
	loop = asyncio.get_event_loop()
	loop.run_until_complete(
		run(
			configuration=configuration
		)
	)
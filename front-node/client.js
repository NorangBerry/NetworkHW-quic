const { createQuicSocket } = require('net');
const axios = require('axios');
const fs = require('fs');
const https = require('https');
const http2 = require('http2');
const req_header = fs.readFileSync(__dirname + '/sample_http_header.txt','utf8');

const socket = createQuicSocket();
const URL = '192.168.0.2'
const PORT2 = 9000
const PORT3 = 9001
async function main(){
	await test_tcp()
	await test_quic()
}
async function test_tcp(){
	const url = `https://${URL}:${PORT2}`
	const ca = fs.readFileSync(__dirname + "/public.pem")
	const client = http2.connect(url, {
		ca: ca,
		rejectUnauthorized: false
	});

	const req = client.request({
			[http2.constants.HTTP2_HEADER_SCHEME]: "https",
			[http2.constants.HTTP2_HEADER_METHOD]: http2.constants.HTTP2_METHOD_GET,
	});

	req.on('data', (chunk) => {
	});
	// req.write('Send');
	
	const before = new Date()
	req.end();
	req.on('end', () => {
		const diff = new Date().getTime() - before.getTime()
		console.log(`http2: ${diff}`)
	});
}
async function test_quic(){
	const client = await socket.connect({address:URL,port:PORT3,alpn:'h3'})
	const stream = await client.openStream();
	stream.on('data', (data) => {
	});
	const before = new Date()
	stream.end(req_header);
	stream.on('end',() =>{
		const diff = new Date().getTime() - before.getTime()
		console.log(`http3: ${diff}`)
	})
}

main()
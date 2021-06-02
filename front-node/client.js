const { createQuicSocket } = require('net');
const axios = require('axios');
const fs = require('fs');
const https = require('https');
const http2 = require('http2');
const req_header = fs.readFileSync(__dirname + '/sample_http_header.txt','utf8');
const req_header_image = fs.readFileSync(__dirname + '/sample_http_header_image.txt','utf8');

const socket = createQuicSocket();
// const URL = '192.168.0.2'
const PORT2 = 9000
const PORT3 = 9001

HTTP2_URLS=['https://172.17.90.8:9000']
HTTP3_URLS=['https://172.17.90.8:9001']
PATHS = ['/','/image']

async function main(){
	await test_tcp()
	await test_quic()
}
async function test_tcp(){
	const ca = fs.readFileSync(__dirname + "/public.pem")
	HTTP2_URLS.forEach(url =>{
		PATHS.forEach(path=>{
			const client = http2.connect(url, {
				ca: ca,
				rejectUnauthorized: false
			});
			const req = client.request({
				[http2.constants.HTTP2_HEADER_SCHEME]: "https",
				[http2.constants.HTTP2_HEADER_METHOD]: http2.constants.HTTP2_METHOD_POST,
				[http2.constants.HTTP2_HEADER_PATH]: path,
			});
			req.on('data', (chunk) => {
			});
			const before = new Date()
			req.end();
			req.on('end', () => {
				const diff = new Date().getTime() - before.getTime()
				console.log(`http2: ${path} : ${diff}`)
			});
		})
	})
}
async function test_quic(){
	HTTP3_URLS.forEach(url =>{
		PATHS.forEach(async (path)=> {
			const req_path = new URL(`${url}${path}`)
			const client = await socket.connect({address:req_path.hostname,port:req_path.port,alpn:'h3'})
			const stream = await client.openStream();
			stream.setEncoding('utf8');
			stream.on('data', (data) => {
			});
			var req = req_header_image
			if(path === '/'){
				req = req_header
			}
			const before = new Date()
			stream.end(req);
			stream.on('end',() =>{
				const diff = new Date().getTime() - before.getTime()
				console.log(`http3: ${path} : ${diff}`)
			})
		});
	});
}

main()
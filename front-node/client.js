const { createQuicSocket } = require('net');
const fs = require('fs');
const http2 = require('http2');
const { setTimeout } = require('timers');
const write_csv = require('./write_csv');
const req_header = fs.readFileSync(__dirname + '/sample_http_header.txt','utf8');
const req_header_image = fs.readFileSync(__dirname + '/sample_http_header_image.txt','utf8');

const socket = createQuicSocket();

HTTP2_URLS=['https://?:9000','https://??:9000']
HTTP3_URLS=['https://?:9001','https://??:9001']
PATHS = ['/','/image']

async function main(){
	for(var i =0;i<100;i++){
		const res_tcp = await test_tcp(i)
		const res_quic = await test_quic(i)
		write_csv(i,res_tcp,res_quic)
		//1 min
		await new Promise(resolve => setTimeout(resolve, 1000 * 60 * 1));
	}
	
}
async function test_tcp(index){
	const ca = fs.readFileSync(__dirname + "/public.pem")
	var res = []
	for(var i =0;i<HTTP2_URLS.length;i++){
		const url = HTTP2_URLS[i];
		var json = {'INDEX':index,'TYPE':'HTTP2',"URL":url}
		for(var j=0;j<PATHS.length;j++){
			const path = PATHS[j];
			json[`PATH${j}`] = `${path}`
			json[`TIME${j}`] = await send_tcp(ca,url,path)
		}
		res.push(json)
	}
	return res;
}

async function send_tcp(ca, url, path){
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

	var get_res = false;
	var diff = 0
	const before = new Date()
	req.end();
	req.on('end', () => {
		diff = new Date().getTime() - before.getTime()
		console.log(`http2: ${path} : ${diff}`)
		get_res = true
	});
	while(get_res == false){
		await new Promise(resolve => setTimeout(resolve, 1000));
	}
	return diff;
}

async function test_quic(index){
	var res = []
	for(var i =0;i<HTTP3_URLS.length;i++){
		const url = HTTP3_URLS[i];
		var json = {'INDEX':index,'TYPE':'QUIC',"URL":url}
		for(var j=0;j<PATHS.length;j++){
			const path = PATHS[j];
			json[`PATH${j}`] = `${path}`
			json[`TIME${j}`] = await send_quic(url,path)
		}
		res.push(json)
	}
	return res;
}

async function send_quic(url,path){
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
	var get_res = false
	var diff = 0
	const before = new Date()
	stream.end(req);
	stream.on('end',() =>{
		diff = new Date().getTime() - before.getTime()
		console.log(`http3: ${path} : ${diff}`)
		get_res = true
	})
	while(get_res == false){
		await new Promise(resolve => setTimeout(resolve, 1000));
	}
	return diff;
}

main()
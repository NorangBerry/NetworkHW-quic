const { createQuicSocket } = require('net');

const socket = createQuicSocket();

async function main(){
	test_quic()
}

async function test_quic(){
	const client = await socket.connect({address:'192.168.0.2',port:9001,alpn:'h3'})
	const stream = await client.openStream();
	stream.setEncoding('utf8');
	stream.end('from the client!');
  stream.on('data', (data) => {
		console.log(data)
	});
  stream.on('close', () => { console.log('close') });
	return client
}

main()
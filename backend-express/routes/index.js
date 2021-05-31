const http2 = require('http2');
const fs = require('fs');
var cors = require('cors');

const server = http2.createSecureServer({
  key: fs.readFileSync(__dirname + '/private.pem'),
  cert:  fs.readFileSync(__dirname + '/public.pem')
});
server.on('error', (err) => console.error(err));
server.on('stream', (stream, headers) => {
  // stream is a Duplex
  stream.respond({
    'content-type': 'text/html; charset=utf-8',
    ':status': 200,
		'Access-Control-Allow-Origin': '*'
  });
  stream.end('<h1>Hello World</h1>');
});

server.listen(9000);
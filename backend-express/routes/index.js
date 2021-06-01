const server_http2 = require('./http2')
const server_http3 = require('./quic')
const fs = require('fs');

const html = fs.readFileSync(__dirname + '/../sample.html','utf8');

server_http2.on('stream', (stream, headers) => {
  // stream is a Duplex
  stream.respond({
    'content-type': 'text/html; charset=utf-8',
    ':status': 200,
		'Access-Control-Allow-Origin': '*'
  });
  stream.end(html);
});
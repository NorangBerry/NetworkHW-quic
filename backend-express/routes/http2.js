const http2 = require('http2');
var cors = require('cors');
const { key, cert, port_http2 } = require('../setting');

const server = http2.createSecureServer({cert:cert, key:key, alpn:'h2'});

server.on('error', (err) => console.error(err));

server.listen(port_http2);

module.exports = server;
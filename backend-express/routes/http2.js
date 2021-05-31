const http2 = require('http2');
var cors = require('cors');
const { cert, port_http2 } = require('../setting');

const server = http2.createSecureServer(cert);

server.on('error', (err) => console.error(err));

server.listen(port_http2);

module.exports = server;
const fs = require('fs');
var cors = require('cors');

const { createQuicSocket } = require('net');
const { key, cert, port_http3 } = require('../setting');

// Create the QUIC UDP IPv4 socket bound to local IP port port_http3
const socket = createQuicSocket({ endpoint: { port: port_http3 } });

(async function() {
  await socket.listen({key:key, cert:cert,alpn:'h3'});
  console.log('The socket is listening for sessions!');
})();

module.exports = socket;
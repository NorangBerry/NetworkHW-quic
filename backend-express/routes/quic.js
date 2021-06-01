const fs = require('fs');
var cors = require('cors');

const { createQuicSocket } = require('net');
const { cert, port_http3 } = require('../setting');

// Create the QUIC UDP IPv4 socket bound to local IP port port_http3
const socket = createQuicSocket({ endpoint: { port: port_http3 } });

socket.on('session', async (session) => {
  // A new server side session has been created!

  // The peer opened a new stream!
  session.on('stream', (stream) => {
    console.log('hello happy world!')
    // Let's see what the peer has to say...
    stream.setEncoding('utf8');
    stream.on('data', console.log);
    stream.on('end', () => console.log('stream ended'));
    stream.end('from the server')
  });
});

(async function() {
  await socket.listen(cert);
  console.log('The socket is listening for sessions!');
})();

module.exports = socket;
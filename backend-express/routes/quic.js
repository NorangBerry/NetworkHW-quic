const fs = require('fs');
var cors = require('cors');

const { createQuicSocket } = require('net');
const { cert, port_http3 } = require('../setting');


const server = createQuicSocket({ endpoint: { port_http3 } });

server.listen(cert);

server.on('session', (session) => {
  // The peer opened a new stream!
  session.on('stream', (stream) => {
    // Echo server
    stream.pipe(stream);
  });
});

server.on('listening', () => {
  // The socket is listening for sessions!
  console.log(`listening on ${port}...`);
  console.log('input something!');
});

module.exports = server;
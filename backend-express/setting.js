const fs = require('fs');

const cert = {
  key: fs.readFileSync(__dirname + '/private.pem'),
  cert:  fs.readFileSync(__dirname + '/public.pem')
}

const port_http2 = 9000
const port_http3 = 9001

module.exports = {cert,port_http2,port_http3};
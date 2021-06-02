const server_http2 = require('./http2')
const server_http3 = require('./quic')
const fs = require('fs');
const mime = require("mime");

const html = fs.readFileSync(__dirname + '/../sample.html','utf8');
var image = fs.createReadStream(__dirname + '/../sample.jpg');


const sendFile = (stream, fileName) => {
  stream.respond({
    'Content-Type': 'image/jpeg',
    ':status': 200,
    'Access-Control-Allow-Origin': '*',
    'Cache-Control':'no-cache, no-store, must-revalidate'
  });
  image.pipe(stream)
  image = fs.createReadStream(__dirname + '/../sample.jpg');
  // var s = fs.createReadStream(fileName);
  // s.on('open', function () {
  //     stream.respond({
  //       'Content-Type': 'image/jpeg',
  //       ':status': 200,
  //       'Access-Control-Allow-Origin': '*'
  //     });
  //     s.pipe(stream);
  // });
};

server_http2.on('stream',async (stream, headers) => {
  const path = headers[':path']
  console.log(path)
  if(path==="/"){
    stream.respond({
      'Content-Type': 'text/html; charset=utf-8',
      ':status': 200,
      'Access-Control-Allow-Origin': '*'
    });
    stream.end(html);
  }
  else if(path==="/image"){
    sendFile(stream,__dirname + '/../sample.jpg')
  }
});

server_http3.on('session', async (session) => {
  // console.log(session)
  session.on('stream', (stream) => {
    stream.setEncoding('utf8');
    var req = ''
    stream.on('data', (data)=>{
      req += data
    });
    stream.on('end', async (data)=>{
      const path = req.split('\n')[0].split(' ')[1]
      if(path === '/'){
        stream.end(html)
      }
      else if(path == '/image'){
        image.pipe(stream)
        image = fs.createReadStream(__dirname + '/../sample.jpg');
      }
    });
  });
});

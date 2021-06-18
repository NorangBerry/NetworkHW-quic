var fs = require('fs');
var csvWriter = require('csv-write-stream')

function write_csv(index,res_tcp,res_quic){
	var writer = csvWriter()
	writer.pipe(fs.createWriteStream('out.csv', {flags: 'a'}))
	for(var i =0;i<res_tcp.length;i++){
		writer.write(res_tcp[i])
	}
	for(var i =0;i<res_quic.length;i++){
		writer.write(res_quic[i])
	}
	writer.end()
}

module.exports = write_csv;
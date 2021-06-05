var fs = require('fs');
var csvWriter = require('csv-write-stream')

function write_csv(index,res_tcp,res_quic){
	var writer = csvWriter()
	writer.pipe(fs.createWriteStream('out.csv', {flags: 'a'}))
	writer.write(res_tcp)
	writer.write(res_quic)
	writer.end()
}

module.exports = write_csv;
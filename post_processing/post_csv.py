import csv
import numpy as np

PATH = "./post_processing"
REMOTE_URL = "52.15.197.199"

def read_csv(name):
	ret = []
	with open(f'{PATH}/{name}.csv','r') as fd:
		reader = csv.DictReader(fd)
		for line in reader:
			if line['INDEX'] and line['INDEX'].isdigit():
				ret.append(line)
	return ret

def write_csv(ret_tcp,ret_quic):
	with open('out.csv','a') as fd:
		writer = csv.DictWriter(fd, fieldnames=ret_tcp.keys())
		writer.writerow(ret_tcp)
		writer.writerow(ret_quic)

def filter(src,type):
	filtered = [{'INDEX':row['INDEX'],
									'URL':('REMOTE' if REMOTE_URL in row['URL'] else 'LOCAL'),
									'TYPE':row['TYPE'],
									'TIME':row[type]} 
										for row in src]
	return filtered

def save_compare_csv(out_name,lines):
	with open(f'{PATH}/{out_name}.csv','w') as fd:
		writer = csv.DictWriter(fd, fieldnames=['INDEX','HTTP2_LOCAL','QUIC_LOCAL','HTTP2_REMOTE','QUIC_REMOTE'])
		writer.writeheader()
		for line in lines:
			index = line[0]['INDEX']
			http2_remote = None
			http3_remote = None
			http2_local = None
			http3_local = None
			for row in line:
				if row['URL'] == 'LOCAL' and row['TYPE'] == 'QUIC':
					http3_local = row['TIME']
				elif row['URL'] == 'REMOTE' and row['TYPE'] == 'QUIC':
					http3_remote = row['TIME']
				elif row['URL'] == 'LOCAL' and row['TYPE'] == 'HTTP2':
					http2_local = row['TIME']
				elif row['URL'] == 'REMOTE' and row['TYPE'] == 'HTTP2':
					http2_remote = row['TIME']
			writer.writerow({'INDEX':index,'HTTP2_LOCAL':http2_local,'QUIC_LOCAL':http3_local,'HTTP2_REMOTE':http2_remote,'QUIC_REMOTE':http3_remote})

def node_vs_django(name,node,django):
	with open(f'{PATH}/{name}.csv','w') as fd:
		writer = csv.DictWriter(fd, fieldnames=['INDEX','NODE_HTTP2_LOCAL','NODE_QUIC_LOCAL','NODE_HTTP2_REMOTE','NODE_QUIC_REMOTE'
																						,'DJANGO_HTTP2_LOCAL','DJANGO_QUIC_LOCAL','DJANGO_HTTP2_REMOTE','DJANGO_QUIC_REMOTE'])
		writer.writeheader()
		for i in range(len(node)):
			node_row = node[i]
			django_row = django[i]
			row = {}
			for item in node_row:
				if item['URL'] == 'LOCAL' and item['TYPE'] == 'QUIC':
					row['NODE_QUIC_LOCAL'] = item['TIME']
				elif item['URL'] == 'REMOTE' and item['TYPE'] == 'QUIC':
					row['NODE_QUIC_REMOTE'] = item['TIME']
				elif item['URL'] == 'LOCAL' and item['TYPE'] == 'HTTP2':
					row['NODE_HTTP2_LOCAL'] = item['TIME']
				elif item['URL'] == 'REMOTE' and item['TYPE'] == 'HTTP2':
					row['NODE_HTTP2_REMOTE'] = item['TIME']

			for item in django_row:
				if item['URL'] == 'LOCAL' and item['TYPE'] == 'QUIC':
					row['DJANGO_QUIC_LOCAL'] = item['TIME']
				elif item['URL'] == 'REMOTE' and item['TYPE'] == 'QUIC':
					row['DJANGO_QUIC_REMOTE'] = item['TIME']
				elif item['URL'] == 'LOCAL' and item['TYPE'] == 'HTTP2':
					row['DJANGO_HTTP2_LOCAL'] = item['TIME']
				elif item['URL'] == 'REMOTE' and item['TYPE'] == 'HTTP2':
					row['DJANGO_HTTP2_REMOTE'] = item['TIME']
			writer.writerow(row)


if __name__ == "__main__":
	out_node = read_csv('out_node')
	out_django = read_csv('out_django')

	text_node = filter(out_node,'TIME0')
	save_compare_csv('plain_send_node',np.reshape(text_node,(-1,4)))
	text_python = filter(out_django,'TIME0')
	save_compare_csv('plain_send_python',np.reshape(text_python,(-1,4)))

	img_node = filter(out_node,'TIME1')
	save_compare_csv('img_send_node',np.reshape(img_node,(-1,4)))
	img_python = filter(out_django,'TIME1')
	save_compare_csv('img_send_python',np.reshape(img_python,(-1,4)))

	node_vs_django('total_plain',np.reshape(text_node,(-1,4)),np.reshape(text_python,(-1,4)))
	node_vs_django('total_img',np.reshape(img_node,(-1,4)),np.reshape(img_python,(-1,4)))
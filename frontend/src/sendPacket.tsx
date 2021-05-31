
import React from 'react'
import axios from 'axios'
const URL = "https://192.168.0.2:9000/"

interface Props{
}

interface States{
	QUIC:number;
	TCP:number;
}

class SendPacket extends React.Component<Props,States> {
	constructor(props:any){
		super(props);
		this.state={QUIC:NaN, TCP:NaN}
	}

	componentDidMount(){
		this.sendTCP().then(() =>{
			this.sendQUIC();
		});
		
	}

	async sendQUIC(){
		
	}

	async sendTCP(){
		const before = new Date();
		return axios.get(URL).then((res: any) => {
			const after = new Date();
			this.setState({TCP:after.getTime() - before.getTime()})
		})
	}
	render(){
		return (
			<>
			<div>
				HTTP 3.0: {this.state.TCP}
			<div>
			</div>
				HTTP 2.0: {this.state.QUIC}
			</div>
			</>
	)}
}
  
  export default SendPacket;
  
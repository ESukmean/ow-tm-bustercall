import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';

import imgTM from './assets/tm.png';
import * as Bootstrap from 'react-bootstrap';
import { useState, useEffect } from "react";

function App() {
	const [loginInfo, setLoginInfo] = useState({
		'result': false,
		'msg': '로그인이 필요합니다'
	});
	const [phoneNoMiddle, setPhoneNoMiddle] = useState('');
	const [phoneNoEnd, setPhoneNoEnd] = useState('');
	const [password, setPassword] = useState('');
	const [processRegister, setProcessRegister] = useState(false);

	const buildPhoneNo = () => "010" + phoneNoMiddle.toString() + phoneNoEnd.toString();
	const buildFormData = () => { 
		let formData = new FormData(); 
		const phoneNo = parseInt(buildPhoneNo()).toString();
		if (phoneNo.length < 9 || phoneNo.length > 10) { alert('부정확한 전화번호입니다.'); return false; }
		formData.append('phoneNo', buildPhoneNo()); 

		if (password.length < 8) { alert('비밀번호는 최소 8글자 이상이어야 합니다.'); return false; }
		formData.append('password', password); 
		
		return formData; 
	};
	const handleLoginBtn = () => {
		let formData = buildFormData();
		fetch("/api/" + buildPhoneNo(), {method: 'POST', body: formData}).then((resp) => resp.json()).then((json) => {
			setLoginInfo(json);

			if (json.result === false) { alert(json.msg); return; }
		});
	};
	const handleRegisterBtn = () => {
		if (buildFormData() === false) return;
		setProcessRegister(true);
	};
	
	return (
		// <Router>
			<div class="main-card">
				<header>
					<img src={imgTM} alt="완전 난장판"/>
					<h1>완전 난장판 알리미</h1>
				</header>
				<Bootstrap.Form>
					<Bootstrap.Form.Label>알림 받을 전화번호 (SMS)</Bootstrap.Form.Label>
					<Bootstrap.Form.Row>
						<Bootstrap.Form.Group as={Bootstrap.Col}><Bootstrap.Form.Control value="010" readonly="true" /></Bootstrap.Form.Group>
						<Bootstrap.Form.Group as={Bootstrap.Col}><Bootstrap.Form.Control placeholder="9800" value={phoneNoMiddle} onChange={(e) => setPhoneNoMiddle(e.target.value)} minLength="4" maxLength="4" required/></Bootstrap.Form.Group>
						<Bootstrap.Form.Group as={Bootstrap.Col}><Bootstrap.Form.Control placeholder="0336" value={phoneNoEnd} onChange={(e) => setPhoneNoEnd(e.target.value)} minLength="4" maxLength="4" required/></Bootstrap.Form.Group>
					</Bootstrap.Form.Row>
					<Bootstrap.Form.Label>비밀번호</Bootstrap.Form.Label>
					<Bootstrap.Form.Control type="password" value={password} onChange={(e) => setPassword(e.target.value)} minLength="8" placeholder="비밀번호 (최소 8글자)" required/>
					<br/>
					<Bootstrap.Container fluid>
  					<Bootstrap.Row>
							<Bootstrap.Col style={{paddingLeft: 0}}><Bootstrap.Button variant="primary" block onClick={handleLoginBtn}>로그인</Bootstrap.Button></Bootstrap.Col>
							<Bootstrap.Col style={{paddingRight: 0}}><Bootstrap.Button variant="light" block onClick={handleRegisterBtn}>등록</Bootstrap.Button></Bootstrap.Col>
						</Bootstrap.Row>
					</Bootstrap.Container>
				</Bootstrap.Form>
				<div style={{padding: '16px'}}>
					{loginInfo.result == false && <Bootstrap.Alert variant="danger">{ loginInfo.msg.split('\n').map(line => { return (<span>{line}<br /></span>)}) }</Bootstrap.Alert> }
				</div>
				{processRegister && <RegisterForm handleClose={() => setProcessRegister(false)} formData={buildFormData()} /> }
			</div>
		// </Router>
	);
}

const RegisterForm = (props) => {
	const { handleClose, formData } = props;
	const [battleTag, setBattleTag] = useState('');
	const submit = () => {
		formData.append('battleTag', battleTag);

		fetch("/api/" + formData.get('phoneNo'), {method: 'PUT', body: formData}).then((resp) => resp.json()).then((json) => {
			alert(json.msg);
			handleClose();
		});
	};

	return (
		<Bootstrap.Modal show={true} onHide={handleClose}>
			<Bootstrap.Modal.Header closeButton>
				<Bootstrap.Modal.Title>배틀테그 확인</Bootstrap.Modal.Title>
			</Bootstrap.Modal.Header>

			<Bootstrap.Modal.Body>
				<Bootstrap.Form.Control type="text" value={battleTag} onChange={(e) => setBattleTag(e.target.value)} placeholder="배틀테그를 입력해주세요" />
			</Bootstrap.Modal.Body>

			<Bootstrap.Modal.Footer>
				<Bootstrap.Button variant="secondary" onClick={handleClose}>취소(닫기)</Bootstrap.Button>
				<Bootstrap.Button variant="primary" onClick={submit}>저장(심사 요청)</Bootstrap.Button>
			</Bootstrap.Modal.Footer>
		</Bootstrap.Modal>
	);
}


export default App;

document.addEventListener('DOMContentLoaded', () => {
	
	var socket = io.connect('http://' + document.domain + ':' + location.port);
	let room = "Lounge";
	let user = "";
	var i, x = "";

	joinRoom("Lounge");
	send();
	
	// Display incoming messages
	socket.on('message', data => {
		
		const p = document.createElement('p');
		const span_username = document.createElement('span');
		const span_timestamp = document.createElement('span');
		const br = document.createElement('br');
		
		if (data.username) {
			span_username.innerHTML = data.username;
			span_timestamp.innerHTML = data.time_stamp;
			p.innerHTML = span_username.outerHTML + br.outerHTML + data.msg + br.outerHTML + span_timestamp.outerHTML;
			document.querySelector('#display-message-section').append(p);			
		} else {
			printSysMsg(data.msg)
			
		}

	});
	
	socket.on('echo', data => {
		
		const p = document.createElement('p');
		const span_username = document.createElement('span');
		const br = document.createElement('br');
		
		if (data.username) {
			span_username.innerHTML = data.username;
			p.innerHTML = span_username.outerHTML + br.outerHTML;
			document.querySelector('#display-online_user-section').append(p);				
		} else {
			printSysMsg(data.msg)
			
		}

	});
	
	
	function send(){
		socket.emit('send_message', {'username': username});
	}
	
	
	
	// send message
	document.querySelector('#send_message').onclick = () => {
		
		socket.send({'msg': document.querySelector('#user-message').value, 'username': username, 'room': room});
		// Clear input area
		document.querySelector('#user-message').value = ' ';
	};
	
	document.querySelector('#logout-btn').onclick = () => {
		logout();
		
	};
	
	//Room Selection
	document.querySelectorAll('.select-room').forEach(p => {
		p.onclick = () => {
 			let newRoom = p.innerHTML
			if (newRoom === room){
				msg = `You are already in ${room} room.`;
				printSysMsg(msg);
			} else {
				leaveRoom(room);
                joinRoom(newRoom);
				room = newRoom;
			}
		};
	});
	
	/* Tried implementing personal chats
	
	//user Selection
	document.querySelectorAll('.user-selection').forEach(p => {
		p.onclick = () => {
 			let newuser = p.innerHTML
			if (newuser === user){
				msg = `You are already chatting with ${user}.`;
				printSysMsg(msg);
			} else {
				leavepersonal(user);
                joinpersonal(newuser);
				user = newuser;
			}
		};
	});
	
	
	// leaveuser Function
	function leavepersonal(user){
		socket.emit('leavepersonal', {'username': username, 'room': user});
	}
		
	// joinRoom Function
	function joinpersonal(user){
		socket.emit('joinpersonal', {'username': username, 'room': user});
		
		//Autofocus
		document.querySelector('#user-message').focus();
		
		document.querySelector('#display-message-section').innerHTML = '';
		
	}
	
	*/
	
	// leaveRoom Function
	function leaveRoom(room){
		socket.emit('leave', {'username': username, 'room': room});
	}
		
	// joinRoom Function
	function joinRoom(room){
		socket.emit('join', {'username': username, 'room': room});
		
		//Autofocus
		document.querySelector('#user-message').focus();
		
		document.querySelector('#display-message-section').innerHTML = '';
		
	}	
	
	function logout(){
		socket.emit('logout', {'username': username, 'room': room});
	}
	
	// Print system message
	function printSysMsg(msg){
		const p = document.createElement('p');
		p.innerHTML = msg;
		document.querySelector('#display-message-section').append(p);
	}
		
	
	
	
});
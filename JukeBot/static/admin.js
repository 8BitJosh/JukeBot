$(document).ready(function() {

	// setup socket connection
	namespace = '/admin';
	var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

// connect
	socket.on('connect', function(){
		var cookie = getCookie('Jukebot')
		socket.emit('connected', cookie);
	});

	socket.on('reloadpage', function(){
		$(location).attr('href', '/login')
	});

	socket.on('currentConfig', function(msg){
		$.each(msg, function(index, item){
			if(index == 'voteSkipNum' || index == 'shuffleLimit'){
				$('#' + index).val(item);
			}
			else{
				$('input:radio[name=' + index + ']:nth(0)').prop("checked", item);
				$('input:radio[name=' + index + ']:nth(1)').prop("checked", !item);
			}
		});
	});

	socket.on('logs', function(msg){
		$('#log').text(msg);
	});

	$('button#submit').click(function(event) {
		var settings = $('#settings').serializeArray()
		var processed = {};
		$.each(settings, function(index, item){
			if(item.name == 'voteSkipNum' || item.name == 'shuffleLimit'){
				processed[item.name] = item.value;
			}
			else if(item.value == 'true'){
				processed[item.name] = true;
			}
			else if(item.value == 'false'){
				processed[item.name] = false;
			}
		});		
		processed['cookie'] = getCookie('Jukebot');
		socket.emit('updateConfig', processed);
	});

	$('#logout').click(function(event){
		var cookie = getCookie('Jukebot');
		socket.emit('logout', cookie);
	});

});

function getCookie(cname) {
	var name = cname + "=";
	var decodedCookie = decodeURIComponent(document.cookie);
	var ca = decodedCookie.split(';');
	for(var i = 0; i <ca.length; i++) {
		var c = ca[i];
		while (c.charAt(0) == ' ') {
			c = c.substring(1);
		}
		if (c.indexOf(name) == 0) {
			return c.substring(name.length, c.length);
		}
	}
	return "";
}
$(document).ready(function() {

	$.get("ip");

	$('button#login').click(function(event) {
		data = md5('JukeBot' + $('#password').val());

		$.post('postlogin', {login: data}, function(data){
			$(location).attr('href', '/admin')
		});

	});

});


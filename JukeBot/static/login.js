$(document).ready(function() {

	$.get("ip");

	$('button#login').click(function(event) {
		data = md5($('#username').val() + $('#password').val());

		$.post('postlogin', {login: data}, function(data){
			$(location).attr('href', '/admin')
		});

	});

});


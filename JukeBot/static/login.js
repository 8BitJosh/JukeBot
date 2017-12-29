$(document).ready(function() {

	$.get("ip");
	
	$(window).keydown(function(event){
		if(event.keyCode == 13) {
			event.preventDefault();
			return false;
		}
	});

	$('button#login').click(function(event) {
		data = md5('JukeBot' + $('#password').val());

		$.post('postlogin', {login: data}, function(data){
			$(location).attr('href', '/admin')
		});

	});

});


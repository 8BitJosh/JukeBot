$(document).ready(function() {

    namespace = '/main';

    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

    socket.on('connect', function(){
        socket.emit('connected', {data: 'client connected'});
    });
    
    socket.on('response', function(msg) {
        $('#user_alerts').text(msg.data);
    });
    
    socket.on('sent_playlist', function(msg) {
        $('#playlist_table tr:gt(0)').remove();
        $('#nowplay_table tr:gt(0)').remove();
        $.each(msg, function(index, item) {
          if(index == '-'){
            $('<tr>').html("<td>" + index + "</td><td>" + "There is no song playing" + "</td>").appendTo('#nowplay_table');
        }
        else if(index == '0'){
            $('<tr>').html("<td>" + "-" + "</td><td>" + item + "</td>").appendTo('#nowplay_table');
        }
        else{
            $('<tr>').html("<td>" + index + "</td><td>" + item + "</td><td>" + 
                "<button id='del' class='btn btn-sm btn-success'><span class='glyphicon glyphicon-remove'></span></button>" +
                "</td>").appendTo('#playlist_table');
        }
    });
    });
    
    window.setInterval(function() {
        socket.emit('ping');
    }, 1000);

    $('form#send').submit(function(event) {
        socket.emit('sent_song', {data: $('#title_sent').val()});
        $('form#send')[0].reset();
        return false;
    });

    $('button#skip').click(function(event) {
        socket.emit('song_skip');
        return false;
    });
    
    $('button#shuffle').click(function(event) {
        socket.emit('song_shuffle');
        return false;
    });
    
    $('button#clearall').click(function(event) {
        socket.emit('clear_playlist');
        return false;
    });

    $('#playlist_table').on('click', '#del', function(){
        var index = $(this).closest('tr').index();
        var val = $('table#playlist_table tr:eq(' + index + ') td:eq(' + 1 + ')').text();
        socket.emit('delete', {data: index, title: val});
        return false;
    });
});
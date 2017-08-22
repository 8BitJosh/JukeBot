$(document).ready(function() {

    namespace = '/main';

    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

    function genTime(time){
        var minutes = Math.floor(time / 60);
        var seconds = time - minutes * 60;
        seconds = seconds > 9 ? "" + seconds: "0" + seconds;
        return (String(minutes) + ':' + seconds);
    }

    socket.on('connect', function(){
        socket.emit('connected', {data: 'client connected'});
    });

    socket.on('duration', function(msg) {
        if(msg.pos == 0){
            var pro = 0;
        }
        else{
            var pro = Math.round(100 * (msg.pos/msg.dur))
        }
        
        $('.progress-bar').css('width', pro+'%');
        $('#timer').text(genTime(msg.pos) + '/' + genTime(msg.dur));
    });

    socket.on('volume_set', function(msg) {
        var vol = msg.vol;
        $('#volume').val(vol);
    });

    $('#volume').on('change', function(){
        var vol = $('#volume').val();
        console.log(vol);
        socket.emit('volume', {'vol': vol});
    });

    socket.on('pause_button', function(msg){
        $('button#pause').text(msg.data);
    });
    
    socket.on('response', function(msg) {
        $('#user_alerts').text(msg.data);
        setTimeout(clearMsg, 5000);
    });
    
    function clearMsg(){
        $('#user_alerts').empty();
    }

    socket.on('sent_playlist', function(msg) {
        $('#playlist_table tr:gt(0)').remove();
        $.each(msg, function(index, item) {
          if(index == '-'){
            $('#nowplay').text("There is no song playing");
            $('#page_title').text("JukeBot");
        }
        else if(index == '0'){
            $('#nowplay').text(item);
            var str = item.slice(item.search("]")+ 2);
            $('#page_title').text(str);
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
        socket.emit('button', {data: 'skip'});
        return false;
    });
    
    $('button#shuffle').click(function(event) {
        socket.emit('button', {data: 'shuffle'});
        return false;
    });
    
    $('button#clearall').click(function(event) {
        socket.emit('button', {data: 'clear'});
        return false;
    });

    $('button#pause').click(function(event) {
        socket.emit('button', {data: 'pause'});
        return false;
    });

    $('#playlist_table').on('click', '#del', function(){
        var index = $(this).closest('tr').index();
        var val = $('table#playlist_table tr:eq(' + index + ') td:eq(' + 1 + ')').text();
        socket.emit('delete', {data: index, title: val});
        return false;
    });
});
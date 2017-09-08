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
        socket.emit('connected');
        getUserIP(function(ip){
            socket.emit('device', ip);
        });
    });

    socket.on('disconnect', function(){
        socket.emit('disconnect');
    });

    var lastSync = 0;
    var syncInterval = 20000;

    setInterval(function() {
        var now = new Date().getTime();
        if((now - lastSync) > syncInterval){
            lastSync = new Date().getTime();
            socket.emit('sendAll');
        }
    }, 5000);

    socket.on('duration', function(msg) {
        position = msg.position;
        duration = msg.length;
        paused = (msg.paused == 1) ? true : false; 
    });

    var position = 0;
    var duration = 0;
    var paused = true;

    window.setInterval(function(){
        if(paused != true){
            position++;
        }

        var progress = (position == 0) ? 0 : Math.round(100 * (position/duration));

        $('.progress-bar').css('width', progress + '%');
        $('#timer').text(genTime(position) + '/' + genTime(duration));
    }, 1000);

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
        $('#user_alerts').text(' ');
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
            else if(index == 'dur'){
                $('#totalDur').text('Total Duration - ' + item);
            }
            else{
                $('<tr>').html("<td>" + index + "</td><td>" + item + "</td><td>" + 
                    "<button id='del' class='btn btn-sm btn-success'><span class='glyphicon glyphicon-remove'></span></button>" +
                    "</td>").appendTo('#playlist_table');
                }
        });
    });
    
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

function getUserIP(onNewIP) {
    //compatibility for firefox and chrome
    var myPeerConnection = window.RTCPeerConnection || window.mozRTCPeerConnection || window.webkitRTCPeerConnection;
    var pc = new myPeerConnection({
        iceServers: []
    }),
    noop = function() {},
    localIPs = {},
    ipRegex = /([0-9]{1,3}(\.[0-9]{1,3}){3}|[a-f0-9]{1,4}(:[a-f0-9]{1,4}){7})/g,
    key;

    function iterateIP(ip) {
        if (!localIPs[ip]) onNewIP(ip);
        localIPs[ip] = true;
    }
     //create a bogus data channel
    pc.createDataChannel("");

    // create offer and set local description
    pc.createOffer().then(function(sdp) {
        sdp.sdp.split('\n').forEach(function(line) {
            if (line.indexOf('candidate') < 0) return;
            line.match(ipRegex).forEach(iterateIP);
        });
        
        pc.setLocalDescription(sdp, noop, noop);
    }).catch(function(reason) {
        // Handle the failure to connect
    });

    //listen for candidate events
    pc.onicecandidate = function(ice) {
        if (!ice || !ice.candidate || !ice.candidate.candidate || !ice.candidate.candidate.match(ipRegex)) return;
        ice.candidate.candidate.match(ipRegex).forEach(iterateIP);
    };
}

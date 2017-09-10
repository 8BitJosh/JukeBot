$(document).ready(function() {

// setup socket connection
    namespace = '/main';
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

// connect / disconnect
    socket.on('connect', function(){
        socket.emit('connected');
        getUserIP(function(ip){
            socket.emit('device', ip);
        });
    });

    socket.on('disconnect', function(){
        socket.emit('disconnect');
    });

// Get all data from server on long interval to keep in sync
    var lastSync = 0;
    var syncInterval = 20000;

    setInterval(function() {
        var now = new Date().getTime();
        if((now - lastSync) > syncInterval){
            lastSync = new Date().getTime();
            socket.emit('sendAll');
        }
    }, 5000);

// Progress bar webpage code
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


// Set slider value from server when another user changes volume
    socket.on('volume_set', function(msg) {
        var vol = msg.vol;
        $('#volume').val(vol);
    });

// User sets volume slider
    $('#volume').on('change', function(){
        var vol = $('#volume').val();
        socket.emit('volume', {'vol': vol});
    });

// change name of pause button from server
    socket.on('pause_button', function(msg){
        $('button#pause').text(msg.data);
    });

// Set text in blue box
    socket.on('response', function(msg) {
        $('#user_alerts').text(msg.data);
        setTimeout(function(){
            $('#user_alerts').text(' ');
        }, 5000);
    });

// Update Main Now Playing playlist
    socket.on('sent_playlist', function(msg) {
        $('#playlist_table tr:gt(0)').remove();
        $.each(msg, function(index, item) {
            if(index == '-'){
                $('#nowplay').text("There is no song playing");
                $('#page_title').text("JukeBot");
            }
            else if(index == '0'){
                $('#nowplay').text(item);
                var str = item.slice(item.search("]") + 2);
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

// Update list of playlist avaliable on the server + dropdown list
    socket.on('playlistList', function(msg) {
        $('#ServerPlaylistTable tr:gt(0)').remove();
        $('#playlistSelection').find('option').not(':first').remove();
         $.each(msg, function(index, item) {
            $('<tr>').html("<td>[" + genTime(item.dur) + "]</td><td>" + index + "</td><td>" + 
                    "<button id='add' class='btn btn-sm btn-success'><span class='glyphicon glyphicon-plus'></span></button>" +
                    "</td>").appendTo('#ServerPlaylistTable');

            $('#playlistSelection').append($('<option>', {
                value: index,
                text: index 
            }));
        });
    });

// Main header buttons
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
    
    $('button#pause').click(function(event) {
        socket.emit('button', {data: 'pause'});
        return false;
    });

// Now playing queue buttons
    $('button#clearall').click(function(event) {
        socket.emit('button', {data: 'clear'});
        return false;
    });

    $('#playlist_table').on('click', '#del', function(){
        var index = $(this).closest('tr').index();
        var val = $('table#playlist_table tr:eq(' + index + ') td:eq(' + 1 + ')').text();
        socket.emit('delete', {data: index, title: val});
        return false;
    });

// Playlist Add buttons
    $('#ServerPlaylistTable').on('click', '#add', function(){
        var index = $(this).closest('tr').index();
        var val = $('table#ServerPlaylistTable tr:eq(' + index + ') td:eq(' + 1 + ')').text();
        socket.emit('addPlaylist', {title: val});
        return false;
    });
        return false;
    });

// Playlist creator buttons
    $('button#NewEmptyPlaylist').click(function(event) {
        var savename = $('#EmptyPlaylistName').val();
        $('form#sendNameempty')[0].reset();
        $('#newPlaylistDialog').modal('hide');
        socket.emit('newempty', {name: savename});
        return false;
    });

    $('button#NewQueuePlaylist').click(function(event) {
        var savename = $('#QueuePlaylistName').val();
        $('form#sendNameQueue')[0].reset();
        $('#SaveQueueDialog').modal('hide');
        socket.emit('savequeue', {name: savename});
        return false;
    });

    $('button#NewQueueClose').click(function(event) {
        $('form#sendNameQueue')[0].reset();
        $('#SaveQueueDialog').modal('hide');
        return false;
    });

    $('form#addNewSong').submit(function(event) {
        var playname = $('#currentplaylist').text();
        if(playname == 'Playlist:' || $('#newSongName').val() == ''){
            return false;
        }
        socket.emit('add_song', {data: $('#newSongName').val(), playlistname: playname});
        $('form#addNewSong')[0].reset();
        return false;
    });

// playlist dropdown select handler
    $('#playlistSelection').change(function() {
        socket.emit('getplaylist', {data : this.value});
        return false;
    });

    socket.on('selectedplaylist', function(msg){
        $('#PlaylistSongsTable tr:gt(0)').remove();
        $.each(msg, function(index, item) {
            if(index == 'data'){
                $('#totalPlayDur').text('Total Duration - ' + genTime(item.dur));
                $('#currentplaylist').text(item.name);
            }
            else{
                $('<tr>').html("<td>" + index + "</td><td>" + genTime(item.dur) + "</td><td>"+ item.title + "</td><td>" + 
                    "<button id='delEdit' class='btn btn-sm btn-success'><span class='glyphicon glyphicon-remove'></span></button>" +
                    "</td>").appendTo('#PlaylistSongsTable');
            }
        });
    });

    $('#PlaylistSongsTable').on('click', '#delEdit', function() {
        var index = $(this).closest('tr').index();
        var val = $('table#PlaylistSongsTable tr:eq(' + index + ') td:eq(' + 2 + ')').text();
        var playname = $('#currentplaylist').text();
        socket.emit('removePlaySong', {title : val, index:index-1, playlistname: playname});
        return false
    });

});

function genTime(time){
    var h = Math.floor(time / 3600);
    var m = Math.floor(time % 3600 / 60);
    var s = Math.floor(time % 3600 % 60);

    var hours = h > 0 ? String(h) + ':' : '' ;
    var minutes = h > 0 ? '0' + String(m) + ':' : String(m) + ':'; 
    var seconds = s > 9 ? "" + s: "0" + s ;
    return (hours + minutes + seconds) ;
}

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

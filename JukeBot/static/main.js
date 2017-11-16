$(document).ready(function() {

    var ip = '';
    $.get(
        "ip",
        function(data) {
            ip = data;
        }
    );

// setup socket connection
    namespace = '/main';
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

// connect
    socket.on('connect', function(){
        socket.emit('connected', ip);
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

// Refresh after wake from sleep
    // var lastCheck = new Date().getTime();

    // setInterval(function() {
    //     var now = new Date().getTime();
    //     if((now - lastCheck) > 1000){
    //         window.location.reload();
    //         console.log(now);
    //     }
    //     lastCheck = new Date().getTime();
    // }, 100);

// Progress bar webpage code
    socket.on('duration', function(msg) {
        position = msg.position;
        duration = msg.length;
        paused = (msg.paused == 1) ? true : false;
    });

    var position = 0;
    var duration = 0;
    var paused = true;

    //window.location.reload();
    //refreshes the webpage

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
        socket.emit('volume', {'vol': vol, 'ip': ip});
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
            $('<tr>').html("<td>[" + genTime(item.dur) + "]</td><td>" + index + "</td>" +
                    "<td><button id='add' class='btn btn-sm btn-success'><span class='glyphicon glyphicon-plus'></span></button></td>" +
                    "<td><button id='remove' class='btn btn-sm btn-danger'><span class='glyphicon glyphicon-remove'></span></button></td>").appendTo('#ServerPlaylistTable');

            $('#playlistSelection').append($('<option>', {
                value: index,
                text: index
            }));
        });
    });

// Main header buttons
    $('form#send').submit(function(event) {
        socket.emit('sent_song', {data: $('#title_sent').val(), 'ip': ip});
        $('form#send')[0].reset();
        return false;
    });

    $('button#skip').click(function(event) {
        socket.emit('button', {data: 'skip', 'ip': ip});
        return false;
    });

    $('button#shuffle').click(function(event) {
        socket.emit('button', {data: 'shuffle', 'ip': ip});
        return false;
    });

    $('button#pause').click(function(event) {
        socket.emit('button', {data: 'pause', 'ip': ip});
        return false;
    });

    $('button#ClearAllPlaylist').click(function(event) {
        $('#ClearAllDialog').modal('hide');
        socket.emit('button', {data: 'clear', 'ip': ip});
        return false;
    });

    $('button#ClearAllClose').click(function(event) {
        $('#ClearAllDialog').modal('hide');
        return false;
    });


    $('#playlist_table').on('click', '#del', function(){
        var index = $(this).closest('tr').index();
        var val = $('table#playlist_table tr:eq(' + index + ') td:eq(' + 1 + ')').text();
        socket.emit('delete', {data: index, title: val, 'ip': ip});
        return false;
    });

// Playlist Add buttons
    $('#ServerPlaylistTable').on('click', '#add', function(){
        var index = $(this).closest('tr').index();
        var val = $('table#ServerPlaylistTable tr:eq(' + index + ') td:eq(' + 1 + ')').text();
        socket.emit('addPlaylist', {title: val, 'ip': ip});
        return false;
    });

    $('#ServerPlaylistTable').on('click', '#remove', function(){
        var index = $(this).closest('tr').index();
        var val = $('table#ServerPlaylistTable tr:eq(' + index + ') td:eq(' + 1 + ')').text();

        var userinput = window.prompt("Enter the name of the playlist you are deleting", "");

        if (userinput == null || userinput == ""){
            return false;
        }
        else {
            socket.emit('removePlaylist', {index: index-1, "userinput" : userinput, title: val, 'ip': ip});
            return false;
        }
    });

// Playlist creator buttons
    $('button#NewEmptyPlaylist').click(function(event) {
        var savename = $('#EmptyPlaylistName').val();
        $('form#sendNameempty')[0].reset();
        $('#newPlaylistDialog').modal('hide');
        socket.emit('newempty', {name: savename, 'ip': ip});
        return false;
    });

    $('button#NewQueuePlaylist').click(function(event) {
        var savename = $('#QueuePlaylistName').val();
        $('form#sendNameQueue')[0].reset();
        $('#SaveQueueDialog').modal('hide');
        socket.emit('savequeue', {name: savename, 'ip': ip});
        return false;
    });

    $('button#NewQueueClose').click(function(event) {
        $('form#sendNameQueue')[0].reset();
        $('#SaveQueueDialog').modal('hide');
        return false;
    });

    $('button#NewEmptyClose').click(function(event) {
        $('form#sendNameempty')[0].reset();
        $('#newPlaylistDialog').modal('hide');
        return false;
    });

    $('form#addNewSong').submit(function(event) {
        var playname = $('#currentplaylist').text();
        if(playname == 'Playlist:' || $('#newSongName').val() == ''){
            return false;
        }
        socket.emit('add_song', {data: $('#newSongName').val(), playlistname: playname, 'ip': ip});
        $('form#addNewSong')[0].reset();
        return false;
    });

// playlist dropdown select handler
    $('#playlistSelection').change(function() {
        socket.emit('getplaylist', {data : this.value, 'ip': ip});
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
        socket.emit('removePlaySong', {title : val, index: index-1, playlistname: playname, 'ip': ip});
        return false;

    });

});

function genTime(time){
    var h = Math.floor(time / 3600);
    var m = Math.floor(time % 3600 / 60);
    var s = Math.floor(time % 3600 % 60);

    var hours = h > 0 ? String(h) + ':' : '' ;
    var minutes = m > 9 ? String(m) + ':' : "0" + String(m) + ':';
    var seconds = s > 9 ? "" + s: "0" + s ;
    return (hours + minutes + seconds) ;
}


$.fn.scrollView = function () {
    return this.each(function () {
        $('html, body').animate({
            scrollTop: $(this).offset().top
        }, 500);
    });
}

if (!String.prototype.format) {
  String.prototype.format = function() {
    var args = arguments;
    return this.replace(/{(\d+)}/g, function(match, number) { 
      return typeof args[number] != 'undefined'
        ? args[number]
        : match
      ;
    });
  };
}


function vote(song_id) {
    $.get('vote/'+song_id, function(data) {
       console.log(data);
       getInfo();
    });
}

var num_slides = 0;

var places = ['1<sup>st</sup>', '2<sup>nd</sup>', '3<sup>rd</sup>', '4<sup>th</sup>', '5<sup>th</sup>'];

var last_vote = 0;
var last_place = 0;

function addSlide(name, artists, img, votes, song_id) {
    var slide_num = num_slides;
    if(slide_num==0) {
        //display carousel
        $('#carouselExampleIndicators').show();
    }
    var active = slide_num == 0 ? 'active' : '';
    var plural = votes == 1 ? '' : 's';

    if (votes < last_vote) {
        last_place += 1;
    }
    last_vote = votes;

    // format params: 0 slide_num, 1 active, 2 song_id, 3 img, 4 name, 5 artists, 6 votes, 7 plural, 8 place
    var inner_txt = '<div id="slide-{0}" class="carousel-item {1}" style="width:300px;"> <span hidden>{2}</span><img class="d-block w-100" src="{3}" alt="slide"> <div class="carousel-caption d-md-block"><h1 class="slide-place">{8}</h1><h5 class="slide-name">{4}</h5> <p class="slide-artist">{5}</p> <p class="slide-vote"> {6} Vote{7}</p><button class="slide_btn btn">Vote</button></div> </div>'.format(
        slide_num, active, song_id, img, name, artists, votes, plural, places[last_place]);
    $('#inner').append(inner_txt);

    var ind_txt = '<li data-target="#carouselExampleIndicators" data-slide-to="{0}" class="{1}" li>'.format(slide_num, active);
    $('#indicators').append(ind_txt);

    num_slides++;

    $('.slide_btn').click(function() {
        var id = $(this).parent().parent().find('span').html();
        console.log('ID: ' + id);
        vote(id);
    });
    
}


function setSlide(index, name, artists, img, votes, song_id) {
    if (index >= num_slides) {
        // add new slide
        addSlide(name, artists, img, votes, song_id);
        return;
    }

    if (votes < last_vote) {
        last_place += 1;
    }
    last_vote = votes;

    //update slide params
    var $ele = $('#slide-'+index);
    $ele.find('img').attr('src', img);
    $ele.find('.slide-name').html(name);
    $ele.find('.slide-artist').html(artists);
    var plural = votes == 1 ? '' : 's';
    $ele.find('.slide-vote').html(votes + ' Vote' + plural);
    $ele.find('span').html(song_id);
    $ele.find('.slide-place').html(places[last_place]);


}



var time_left = 0;
var queued = false
function updateTimeLeft(time) {
    time_left = time;
    // $('#next').html('Time left to vote: ');
    var seconds = Math.max(time % 60, 0);
    var minutes = Math.max((time-seconds) / 60, 0);
    // if (minutes > 0) {
        // pad seconds
    var zero = seconds < 10 ? '0': '';
    $('#timer').html(minutes + ':' + zero + seconds);
    // } else
        // $('#queued').html(seconds + ' seconds');


}

function getInfo() {
    $.get('info/', function(data) {
        console.log(data);
            
        if (!data['on']) {
            $('#off_info').show();
            $('#whole_div').hide();
            return;
        } else {
            $('#off_info').hide();
            $('#whole_div').show();
        }
       // $('#current').html(data['current']=='Not currently playing music' ? 'Not currently playing music' : data['current']['name'] + '  -  ' + data['current']['artists']);
       if (data['current'] != 'Not currently playing music') {
        console.log('hi');
           $('#current_song').html(data['current']['name']);
           $('#current_artist').html(data['current']['artists']);
           $('#current_img').attr('src', data['current']['artwork']);
       }
        queued = data['queued'] != 'None';
        if (queued) {
            $('#time_div').hide();
            $('#next_div').show();
            $('#next_song').html(data['queued']['name']);
            $('#next_artist').html(data['queued']['artists']);
            $('#next_img').attr('src', data['queued']['artwork']);
        } else{
            $('#time_div').show();
            $('#next_div').hide();
            var time = Math.max(0, Math.round((data['current']['duration'] - data['current']['time']) / 1000) - 30);
            //this condition prevents timer spasming
            if(Math.abs(time - time_left) > 3)
                updateTimeLeft(time);
        }
        // $('#queued').html(queued ? data['queued']['name'] + '  -  ' + data['queued']['artists'] : 'None');
        // $('#voting').html('');
        last_vote = 0;
        last_place = 0;
        for (var i = 0; i < data['voting'].length; i++) {
            var votes = data['voting'][i]['votes'];
            var name = data['voting'][i]['name'];
            var img = data['voting'][i]['artwork'];
            var artists = data['voting'][i]['artists'];
            var song_id = data['voting'][i]['song_id'];
            setSlide(i, name, artists, img, votes, song_id);
            // var txt = data['voting'][i]['name'] + '  -  ' + data['voting'][i]['artists'];
            // txt += '<br> Votes: ' + data['voting'][i]['votes']
            // // var remove = '  <button class="remove-btn" id="remove-'+data['voting'][i]['id']+'">Remove</button>';
            // $('#voting').append('<li>'+txt+'</li>');
        }

        if (data['voting'].length < num_slides || data['voting'].length == 0) {
            // clear all
            $('#indicators').html('');
            $('#inner').html('');
            num_slides = 0;
            $('#carouselExampleIndicators').hide();
        }

        

         $('.remove-btn').click(function() {
            var id = $(this).attr('id').split('-')[1];
            console.log(id);
            $.get('remove/'+id, function(data) {
                console.log(data);
               getInfo();
            })
        });
    });
}

function onSearch() {
    console.log($('#search').val());

    $.get('search/?q=' + $('#search').val(), function(data) {
        console.log(data);
        var songs = data['songs'];
        // $('#results').html('<tr><th>Name</th><th>Artists</th><th>Album</th><th>Length</th></tr>');
        $('#results').html('');
        for (var i = 0; i < songs.length; i++) {

            var html = '<div class="search-obj"><button class="btn btn-success" id="result-{0}">Vote</button><div class="name">{1}</div><div class="artist">{2}</div></div>'.format(songs[i]['id'], songs[i]['name'], songs[i]['artists'])
            $('#results').append(html);
        }

        //scroll to results
        $('#results').scrollView();

        $('.search-obj button').click(function() {
            var id = $(this).attr('id').split('-')[1];
            console.log(id);
            vote(id);
        });
    })
}

$(document).ready(function() {

    getInfo();

    setInterval(function(){
        //refresh
        console.log('updating');
        getInfo();
    }, 2000);

    $('#search-btn').click(function() {
        onSearch();
    });
    $('#search').keypress(function(event) {
        if ( event.which == 13 ) {
             onSearch();
          }
    });

    setInterval(function(){
        if (time_left > 1);
        updateTimeLeft(time_left - 1);

    }, 1000)

   // setSlide(0, 'name', 'artists', 'http://waybeyond.in/wp-content/uploads/2017/11/linkedin-thumbnail.png', 2, 'fdsfd');


    
});

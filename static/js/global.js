$( document ).ready(function() {

  $('textarea').autogrow({onInitialize: true});

  //Cloner for infinite input lists
  $(".circle--clone--list").on("click", ".circle--clone--add", function(){
    var parent = $(this).parent("li");
    var copy = parent.clone();
    parent.after(copy);
    copy.find("input, textarea, select").val("");
    copy.find(".skills_tag").children('span').remove();
    copy.find('.skill_autocomplete').autocomplete({ serviceUrl: '/ajax/skills/', autoSelectFirst: true});
    copy.find("*:first-child").focus();

    copy.find("input, textarea, select").prop('id', function(index, id) {
            return id.replace(/form-\d+-/g,"form-"+$('#id_form-TOTAL_FORMS').val()+"-");
    });
    copy.find("input, textarea, select").prop('name', function(index, name) {
            return name.replace(/form-\d+-/g,"form-"+$('#id_form-TOTAL_FORMS').val()+"-");
    });
    //Increment total forms in inline forms
    $('#id_form-TOTAL_FORMS').val( function(i, oldval) {
        return ++oldval;
    });

  });


  $(".circle--clone--list").on("click", "li:not(:only-child) .circle--clone--remove", function(){
    var parent = $(this).parent("li");
    parent.remove();
  });

  // Adds class to selected item
  $(".circle--pill--list a").click(function() {
    $(".circle--pill--list a").removeClass("selected");
    $(this).addClass("selected");
  });

  // Adds class to parent div of select menu
  $(".circle--select select").focus(function(){
   $(this).parent().addClass("focus");
   }).blur(function(){
     $(this).parent().removeClass("focus");
   });

  // Clickable table row
  $(".clickable-row").click(function() {
      var link = $(this).data("href");
      var target = $(this).data("target");

      if ($(this).attr("data-target")) {
        window.open(link, target);
      }
      else {
        window.open(link, "_self");
      }
  });

  // Custom File Inputs
  var input = $(".circle--input--file");
  var text = input.data("text");
  var state = input.data("state");
  input.wrap(function() {
    return "<a class='button " + state + "'>" + text + "</div>";
  });

  //Change background after avatar file select
  $("input#id_avatar").change(function () {
    $("div#avatar_background").css('background-image', 'none');
    $(this).siblings("span").html("Click 'Save Changes' <br/>to upload new image");
  });
});


// To use the csrftoken with ajax
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
            // Only send the token to relative URLs i.e. locally.
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }
});

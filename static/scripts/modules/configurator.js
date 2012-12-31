require(["jquery", "lib/farbtastic/farbtastic"], function($) {
  $(function() {

    var serializeParams = function(obj) {
      var compiled = [];
      for (key in obj) {
        if(obj[key]) {
          compiled.push([key,obj[key]].join('='));
        }
      }
      return compiled.join('&');
    };

    var updateUri = function() {
      var baseUrl = "http://fpoimg.com";
      var width = $.trim($('#param-width').val()) || "";
      var height = $.trim($('#param-height').val()) || "";
      var wh = width || "";
          wh = height && wh ? wh + "x" + height : wh
      var uri = wh ? baseUrl + "/" + wh : "/300x250?text=preview";
      var args = serializeParams({
        text: $('#param-text').val(),
        bg_color: $('#param-bgcolor').val().replace('#', ''),
        text_color: $('#param-textcolor').val().replace('#', '')
      });
      uri += args ? "?" + args : "";
      
      $('#uri').val(uri);
      $('#preview').attr('src', uri);
    }
    $('#bg-colorpicker').farbtastic(function(value){
      $('#param-bgcolor').val(value);  
    });
    $('#text-colorpicker').farbtastic(function(value){
      $('#param-textcolor').val(value);  
    });
    $('#param-bgcolor').focus(function(){
      $('#bg-colorpicker').css("display", "block");
    }).blur(function(){
      $('#bg-colorpicker').css("display", "none");
      updateUri();
    });
    $('#param-textcolor').focus(function(){
      $('#text-colorpicker').css("display", "block");
    }).blur(function(){
      $('#text-colorpicker').css("display", "none");
      updateUri();
    });
    $('.param').change(function(){updateUri();});
    $('#iab').change(function(){
      var dim_txt = $(this).val().split(' - ');
      var wh = dim_txt[0].split('x');
      $('#param-width').val(wh[0]);
      $('#param-height').val(wh[1]);
      $('#param-text').val(dim_txt[1]);
      updateUri();
    });
    updateUri();
  });
});

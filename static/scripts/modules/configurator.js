require(["jquery", "lib/farbtastic/farbtastic"], function($) {
  $(function() {

    var $pWidth = $('#param-width');
    var $pHeight = $('#param-height');
    var $pText = $('#param-text');
    var $pBgColor = $('#param-bgcolor');
    var $pTextColor = $('#param-textcolor');
    var $uri = $('#uri');
    var $pTextColor = $('#param-textcolor');
    var $preview = $('#preview');
    var $bgColorPicker = $('#bg-colorpicker');
    var $textColorPicker = $('#text-colorpicker');
    var $uriWidth = $('#uri-width');
    var $uriHeight = $('#uri-height');

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
      var baseUrl = "http://" + document.location.host;
      var width = $.trim($pWidth.val()) || "";
      var height = $.trim($pHeight.val()) || "";
      var wh = width || "";
          wh = height && wh ? wh + "x" + height : wh
      var uri = (wh ? "/" + wh : "");

      var args = ""
      if(wh) {
        args = serializeParams({
          text: $pText.val(),
          bg_color: $pBgColor.val().replace('#', ''),
          text_color: $pTextColor.val().replace('#', ''),
          c: 1 // try to track people using the configurator
        });
        uri += args ? "?" + args : "";
      }
      uri = uri ? baseUrl + uri : "";
      $uri.val(uri);
      $preview.attr('src', uri);
      $uriWidth.html(width);
      $uriHeight.html(height);
    };

    var setupListeners = function() {
      // on colorpicker change, update corresponding text input
      $bgColorPicker.farbtastic(function(value){
        $pBgColor.val(value);  
      });
      $textColorPicker.farbtastic(function(value){
        $pTextColor.val(value);  
      });

      // open the pickers when the text inputs are focused
      $pBgColor.focus(function(){
        $bgColorPicker.show('fast');
      }).blur(function(){
        $bgColorPicker.hide('fast');
        updateUri();
      });
      $pTextColor.focus(function(){
        $textColorPicker.show('fast');
      }).blur(function(){
        $textColorPicker.hide('fast');
        updateUri();
      });

      // on param value changes, update the uri
      $('.param').change(function(){updateUri();});

      // iab select menu
      $('#iab').change(function(){
        var dim_txt = $(this).val().split(' - ');
        var wh = dim_txt[0].split('x');
        $pWidth.val(wh[0]);
        $pHeight.val(wh[1]);
        $pText.val(dim_txt[1]);
        updateUri();
      });

    };

    var init = function() {
      setupListeners();
      updateUri();
    }

    init();
  });
});

require(["jquery"], function($) {
  $(function() {
    var updateUri = function() {
      var baseUrl = "http://fpoimg.com";
      var width = $('#param-width').val() || 0;
      var height = $('#param-height').val() || 0;
      $('#uri').val(baseUrl + "/" + width + "x" + height);
    }

    $('#param-width').change(function(){updateUri();});
    $('#param-height').change(function(){updateUri();});
  });
});

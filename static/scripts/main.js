require(["jquery", "lib/bootstrap/js/bootstrap.min"], function($) {
    $(function() {
        var App = {
          pageId: 'default',
          modules: {
            'generator': {}
          }
        }
        App.pageId = $.trim($(this.body).data('page-id'));
        if(App.modules[App.pageId] !== undefined) {
          require(['modules/' + App.pageId]);
        }
    });
});

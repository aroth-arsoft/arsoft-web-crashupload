function crashbox_expand(e) {
    if ($(this).is(e.target)) {
        var url = window.location.href;
        var path = window.location.pathname;
        var target_url = (path + '/').replace('//', '/') + this.id.replace(/___/g, '/');
        console.log(this.id + ' load ' + target_url);
        var xx = $(this).children('div#placeholder');
        xx.load(target_url, function() {
            $(".collapse").on('show.bs.collapse', crashbox_expand);
            }
        );
    }
}
function crashdump_docReady() {
    jQuery(document).ready(function($) {
        $(".collapse").on('show.bs.collapse', crashbox_expand);
    });
}

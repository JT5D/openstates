$(document).ready( function() {

    // make select2 work
    $("#id_abbr").select2({placeholder: "Select a State"}).change(
        function() { this.form.submit(); });
    // made form submit on change, hide submit button
    $('#state_select_submit').hide();
    $('#mainFilter .select2-container').css('width', '200px');

    // hot keys
    var doc = $(document);
    doc.bind("keydown", "alt+b", function(){window.location = '/{{abbr}}/bills/'});
    doc.bind("keydown", "alt+l", function(){window.location = '/{{abbr}}/legislators/'});
    doc.bind("keydown", "alt+c", function(){window.location = '/{{abbr}}/committees/'});
    doc.bind("keydown", "esc", function(){$('#id_q').focus()});

    // add gigya
    var ua = new gigya.socialize.UserAction();
    ua.setTitle($('title').text());
    var params = {
        containerID: 'shareBtns',
        iconsOnly: true,
        layout: 'horizontal',
        noButtonBorders: true,
        shareButtons: 'facebook,twitter',
        shortURLs: 'never',
        showCounts: 'none',
        userAction: ua
    };
    gigya.socialize.showShareBarUI(params);
});

var clickable_rows = function(selector) {
    // Make table rows clickable.
    var trs = $(selector);
    var trs_count = trs.length;
    trs.click(function(){
        var location = $(this).find("a").attr("href");
        if (location) {
            window.location = location;
            return false;
        }
    });

    // If javascript is enabled, change cursor to pointer over table rows
    // and add selected class on hover.
    trs.css('cursor', 'pointer');
    trs.hover(function(){
            $(this).addClass('selected');
        },
        function(){
            $(this).removeClass('selected');
        }
    );
};

var fix_images = function() {
    // this URL will change
    var placeholder = 'http://static.openstates.org/assets/v2/images/placeholder.png';
    $('img.legImgSmall').error(function() {
            $(this).attr("src", placeholder).attr(
                "title", "No Photo Available");
    });
};

var pjax_setup = function(){

    $('form#toggleBtns button').click(function(e){

        // Prevent the normal form submission.
        e.preventDefault();

        // Derive the form url.
        var form_url = $('form#toggleBtns').attr('action');
        var value = $(this).attr('value');
        form_url = form_url + '?chamber=' + encodeURIComponent(value);

        // Use pjax to retrieve and insert the new content.
        $.pjax({
              url: form_url,
              container: 'div[data-pjax]'
        });
    });
};


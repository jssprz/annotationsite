$(document).ready(function() {
    $('form').on('submit',function(e){
        e.preventDefault();
        form = $(this);
        $.ajax({
            type     : "POST",
            cache    : false,
            url      : $(this).attr('action'),
            data     : $(this).serialize(),
            success  : function(data) {
                console.log(data.result_msg);
                form.find('.result').first().text(data.result);
                target = form.serializeArray()[1].value;
                id = form.attr('data-item');
                indicator = $('[data-slide-to="'+id+'"]');
                indicator.removeClass('yes');
                indicator.removeClass('no');
                indicator.removeClass('maybe');
                if(target == '1'){
                    indicator.addClass('yes')
                }
                else if(target == '2'){
                    indicator.addClass('no')
                }
                else if(target == '3'){
                    indicator.addClass('maybe')
                }
            }
        });
    });

    $('input[type=radio]').on('change', function() {
        $(this).closest('form').submit();
    });
});
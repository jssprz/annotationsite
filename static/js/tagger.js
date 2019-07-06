$(document).ready(function() {
    $('form').on('submit',function(e){
        e.preventDefault();
        $.ajax({
            type     : "POST",
            cache    : false,
            url      : $(this).attr('action'),
            data     : $(this).serialize(),
            success  : function(data) {
                console.log(data.result)
            }
        });

    });

    $('input[type=radio]').on('change', function() {
        $(this).closest('form').submit();
    });
});
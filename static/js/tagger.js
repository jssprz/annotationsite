$.validator.addMethod("oneFilled", function(value, element) {
    var form = $(element).closest('form');
    if (form.find("input[name='target']:checked").val() === '1')
        return (form.find("#text").val() !== '' || form.find("#description").val() !== '');
    return true;
}, "* Debe llenar uno de los dos campos");

$(document).ready(function() {
    $('form').validate({
        rules: {
            text: { oneFilled: true },
            description: { oneFilled: true }
        },
        // highlight: function (element) {
        //     $(element).closest('.control-group').removeClass('success').addClass('error');
        // },
        // success: function (element) {
        //     element.text('OK!').addClass('valid')
        //         .closest('.control-group').removeClass('error').addClass('success');
        // }
    });

    $('form').on('submit', function(e){
        e.preventDefault();
        var form = $(this);
        if(form.valid()){
            $.ajax({
                type: "POST",
                cache: false,
                url: $(this).attr('action'),
                data: $(this).serialize(),
                success: function (data) {
                    console.log(data.result_msg);
                    form.find('.result').first().text(data.result);
                    target = form.serializeArray()[1].value;
                    id = form.attr('data-item');
                    indicator = $('[data-slide-to="' + id + '"]');
                    indicator.removeClass('yes');
                    indicator.removeClass('no');
                    indicator.removeClass('maybe');
                    if (target === '1')
                        indicator.addClass('yes');
                    else if (target === '2')
                        indicator.addClass('no');
                    else if (target === '3')
                        indicator.addClass('maybe');
                }
            });
        }
    });

    $('input[type=radio]').on('change', function() {
        var form = $(this).closest('form');
        form.find('.result').first().text('');

        if($(this).val() === '1')
            form.find('.meme-field').show();
        else{
            form.find('.meme-field').hide();
            $(this).closest('form').submit();
        }
    });
});
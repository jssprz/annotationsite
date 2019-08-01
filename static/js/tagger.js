$.validator.addMethod("oneFilled", function(value, element) {
    var form = $(element).closest('form');
    var option = form.find("input[name='target']:checked")
    if (option.val() === '1' || option.val() === '4')
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
                    indicator.removeClass('green');
                    indicator.removeClass('red');
                    indicator.removeClass('yellow');
                    indicator.removeClass('blue');
                    if (target === '1')
                        indicator.addClass('green');
                    else if (target === '2')
                        indicator.addClass('red');
                    else if (target === '3')
                        indicator.addClass('yellow');
                    else if (target === '4')
                        indicator.addClass('blue');
                }
            });
        }
    });

    $('input[type=radio]').on('change', function() {
        var form = $(this).closest('form');
        form.find('.result').first().text('');

        if($(this).val() === '1' || $(this).val() === '4')
            form.find('.meme-field').show();
        else{
            form.find('.meme-field').hide();
            $(this).closest('form').submit();
        }
    });
});
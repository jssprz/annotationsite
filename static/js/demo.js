$(document).ready(function() {
    var csrftoken = Cookies.get('csrftoken');

    loading_elemment = $('#loading_msg')
    $.ajax({
        type: "POST",
        cache: false,
        url: loading_elemment.attr('data-url'),
        headers: {'X-CSRFToken': csrftoken},
        success: function (data) {
            console.log(data.result);
            if (data.result == 'data initialized'){
                loading_elemment.hide();
                $('#searcher').show();
            }
        }
    });

    $('form').validate({
        rules: {
            query: { required: true },
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
                    result_elmment = form.find('.result').first()
                    result_elmment.empty();
                    if(data.result_msg == 'OK'){
                        for(var i=0; i<data.query_result.length; i++){
                            console.log(data.query_result[i])
                            url = data.query_result[i].img_url;
                            result_elmment.append('<div class="col-sm-4"><img src="'+url+'" style="width: 100%;"></div>')
                        }
                    }
                    else if(data.result_msg == 'Error'){
                        result_elmment.append('<span style="color=red;">Su consulta no tiene palabras válidas para esta versión :(</span>')
                    }
                }
            });
        }
    });
});
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

    $('form').on('submit', function(e){
        e.preventDefault()

        // Fetch form to apply custom Bootstrap validation
        var form = $(this);

        form.addClass('was-validated');

        if (form[0].checkValidity() === false) {
          e.stopPropagation()
        }
        else {
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
                        result_elmment.append('<span style="color: red;">Su consulta no tiene palabras válidas para esta versión :(</span>')
                    }
                }
            });
        }
    });
});
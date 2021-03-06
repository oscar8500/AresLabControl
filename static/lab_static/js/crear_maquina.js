function validateForm() {

        if (validarFechas()) {
            $("#formMaquina").submit();
        }

    return false;
}

/*$("#id_estado").click(function(e){

    var fechaIni=$("#id_fechaInicialDisp").val();
    var fechaFin=$("#id_fechaFinalDisp").val();

    if( fechaIni=="" || fechaFin=="" ){
        e.preventDefault();
        $("#id_estado").attr("checked",false);
        $("#mensajes-error").append('<div class="alert alert-danger col-md-6"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>' +
                'Debe tener fechas de disponibilidad para estar activo</div>');

    }
});*/
function validarFechas() {
    if (new Date($("#id_fechaInicialDisp").val()) >= new Date($("#id_fechaFinalDisp").val())) {

        $("#mensajes-error").append('<div class="alert alert-danger col-md-6"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>' +
            'La fecha inicial debe ser menor que la fecha final</div>');
        return false;
    }
    return true;
}
function iniciarFechas(defaultDateEnd, defaultDateStart, minDateEnd, minDateStart) {

    $('#id_fechaFinalDisp').datetimepicker({
        locale: 'es',
        showTodayButton: true,
        format: 'YYYY-MM-DD HH:mm',
        stepping: 30,
        minDate: new Date(),
        //defaultDate: defaultDateEnd
    });

    $('#id_fechaInicialDisp').datetimepicker({
        locale: 'es',
        showTodayButton: true,
        format: 'YYYY-MM-DD HH:mm',
        stepping: 30,
        minDate: new Date(),
        //defaultDate: defaultDateStart
    });

    if (minDateEnd != null) {
        $('#id_fechaInicialDisp').data("DateTimePicker").options({minDate: minDateStart});
        $('#id_fechaFinalDisp').data("DateTimePicker").options({minDate: minDateEnd});
    }

}


$(function() {
    $(".date_form_input").datepicker ({
        endDate: '-1d',
        format: "yyyy-mm-dd",
        autoclose: true
        });
});

function handleSubmitBtnClick() {
    const submit_btn = $('#submit-btn');
    submit_btn.click(function (e) {
        e.preventDefault();
        getResults();
    })
}

function showDetails() {
    const show_data_btn = $('#show-data-btn');
    show_data_btn.click(function () {
        show_data_btn.hide();
        $('#hide-data-btn').show();
        $('#details-table').show();
    })
}

function hideDetails() {
    const hide_data_btn = $('#hide-data-btn');
    hide_data_btn.click(function () {
        hide_data_btn.hide();
        $('#show-data-btn').show();
        $('#details-table').hide();
    })
}

function showSpinner() {
    $('#search-btn').click(function () {
        $('.spinner-div').show()
    })
}


$(document).ready(function() {
    $('.spinner-div').hide();
    $('#hide-data-btn').hide();
    $('#details-table').hide();
    handleSubmitBtnClick();
    showDetails();
    hideDetails();
    // showSpinner();
});
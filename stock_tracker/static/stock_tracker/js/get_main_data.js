

var i = 0;
var total_start_time = Date.now();
function getResults() {
    if (i === 0) {
        console.log('Data fetching started');
        total_start_time = Date.now();
        $('#myTable tbody').empty();
        results = []
    }
    i++;
    const start_time = Date.now();
    const url = '/get-search-results/';
    $('#submit-btn').text('JSON ('+i+'/'+280+')');

    $.ajax({
        url: url,
        type: "POST",
        data:  {
            'percentage': $('#percentage').val(),
            'volume': $('#volume').val(),
            'start_date': $('#startDate').val(),
            'end_date': $('#endDate').val(),
            'i': i,
        },
        dataType: 'json',
        success: function(json_results) {
            results = results.concat(json_results);
            if (i < 280) {
                const end_time = Date.now();
                const total_time = Math.round((end_time-start_time)/1000);
                const cumulative_time = Math.round((end_time-total_start_time)/1000);
                console.log('');
                console.log('Chunk '+ i + '/280');
                console.log('       Chunk time:', total_time, 'seconds');
                console.log('  Cumulative time:', cumulative_time, 'seconds');
                console.log('    Total results:', results.length, 'records');
                getResults();
            } else {
                i=0;
                const total_end_time = Date.now();
                console.log('');
                console.log('finished in:', (total_end_time-total_start_time)/1000);
                console.log('Total number of results:', results.length);
                displayResults()
            }

        },
        error: function () {
            console.log('js error')
        }
    });
}


function displayResults() {
    const start_date = $('#startDate').val();
    const end_date = $('#endDate').val();

    const rows = results.map(function (result) {
        var symbol_td = '<td><a href="/results/' + result.symbol + '/'+ start_date +'/'+ end_date +'">'+result.symbol+'</a></td>';
        var exchange_td = '<td>' + result.exchange + '</td>';
        var country_td = '<td>' + result.country + '</td>';
        var increase_td = '<td>' + result.increase + '</td>';
        var start_price_td = '<td>' + result.start_price + '</td>';
        var end_price_td = '<td>' + result.end_price + '</td>';
        var volume_td = '<td>' + result.volume + '</td>';

        return (
            '<tr>'+symbol_td+exchange_td+country_td+increase_td+start_price_td+end_price_td+volume_td+'</tr>'
        )
    });

    $("#myTable tbody").append(rows);
    $("#myTable").tablesorter();

    console.log('results:', results);
}


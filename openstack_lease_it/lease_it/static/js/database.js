// 7 * 25 * 60 * 60 * 1000 = 604800000
const HEARTBEAT_TIMEOUT = 604800000;

/*
    buildDatabaseView create a full display of Da on div_name
*/
function buildDatabaseView(div_name) {
    var table_columns = [
        { data: 'instance_id' },
        { data: 'heartbeat_at' },
        { data: 'leased_at' },
        { data: 'lease_end' }
    ];
    $('#table-' + div_name).DataTable({
        ajax: {
            url: '/database',
            dataSrc: function(instances) {
                return instances;
            }
        },
        columns: table_columns,
        lengthChange: false,
        pageLength: 25,
        columnDefs: [
            {
                targets: [0],
                render: function ( data, type, row ) {
                    var now = new Date();
                    var lease_end = new Date(row.lease_end);
                    // If a VM has a lease_end date before today, we can delete it
                    if (lease_end < now - HEARTBEAT_TIMEOUT) {
                        return buildDatabaseRowMenu(data) +
                               formatText(data, MAX_STRING_LENGTH);
                    } else {
                        return formatText(data, MAX_STRING_LENGTH);
                    }
                }
            }],
        drawCallback: function(settings, json) {
            $(".tooltipped").tooltip();
        },
    });
}

/*
    buildDatabaseRowMenu build a menu for each row of Database Table
*/
function buildDatabaseRowMenu(data) {
    var menu = '<a class="btn-floating waves-effect waves-light tiny" onClick="swapDatabaseRowMenu(\'' + data + '\')">' +
               '<i class="material-icons" id="database-icon-' + data + '">chevron_right</i></a> ' +
               '<span hidden id="database-delete-' + data + '">' +
               '<a class="btn-floating waves-effect waves-light red lighten-2" ' +
               'onClick="deleteDatabase(\'' + data + '\')">' +
               '<i class="material-icons">delete</i></a></span> ';
    return menu;
}

/*
    swapDatabaseRowMenu swap on/off the delete button
*/
function swapDatabaseRowMenu(button) {
    if ($('#database-delete-' + button).css('display') == 'none') {
        $('#database-icon-' + button).text('chevron_left');
    } else {
        $('#database-icon-' + button).text('chevron_right');
    }
    $('#database-delete-' + button).toggle();
}

/*
    deleteDatabase delete entry in database
*/
function deleteDatabase(instance) {
    return $.getJSON("/database/" + instance, function(data){
    }).success(function(data){
        notify(data);
    });
}
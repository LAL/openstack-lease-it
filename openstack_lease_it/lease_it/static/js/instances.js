/*
  Retrieve useful information about OpenStack
  a dictionnary of instances
   * Id of instance
   * User
   * Creation date
   * Last time we see the instance
   * Last lease date
   * Lease expiration
*/
/* Global variables
 - MAX_USERNAME_LENGTH: Maximum length of username
*/
const MAX_STRING_LENGTH = 30;

/*
    buildInstancesView create a full display of Instance on div_name
*/
function buildInstancesView(div_name, get_option, show_user){
    var table_columns = [
        { data: 'name' },
        { data: 'project' },
        { data: 'created_at' },
        { data: 'lease_end' }
    ];
    if (show_user) {
        table_columns.unshift({data: 'user'});
    }
    $('#table-' + div_name).DataTable({
        ajax: {
            url: '/instances?' + get_option,
            dataSrc: function(instances) {
                /* We add a lease button @ the end of the End Of Life line */
                for (let instance=0; instance < instances.length; instance++) {
                    instances[instance].lease_end = formatLeaseBtn(instances[instance].lease_end,
                        instances[instance].id
                    );
                }
                return instances;
            }
        },
        columns: table_columns,
        lengthChange: false,
        pageLength: 25,
        columnDefs: [
            {
                targets: [0, 1, 2],
                render: function ( data, type, row ) {
                        return buildInstanceRowMenu(data) + formatText(data, MAX_STRING_LENGTH);
                }
            }],
        drawCallback: function(settings, json) {
            $(".tooltipped").tooltip();
        },
    });
    $( "#progress-bar-" + div_name ).hide();
}

/*
    Update lease status on click
*/
function updateLease(instance) {
    return $.getJSON("/instances/" + instance, function(data){
    }).success(function(data){
        notify(data);
    });
}

/*
    Format text to be displayed
*/
function formatText(text, length) {
    var response = text;
    if (response.length > length) {
        response = '<span class="tooltipped" data-position="top" data-delay="50"' +
                   'data-tooltip="' + text + '">' + text.substr(0, length) + "… </span>";
    }
    return response;
}

/*
    Add lease button at the end of the date
*/
function formatLeaseBtn(date, instance) {
    return date += '<span class="waves-effect waves-light ' +
                   ' new badge hoverable"' +
                   ' data-badge-caption="new lease" onClick="updateLease(\''+
                   instance + '\')"></span>';
}


/*
    buildDatabaseRowMenu build a menu for each row of Database Table
*/
function buildInstanceRowMenu(data) {
    var menu = '<a class="btn-floating waves-effect waves-light tiny" onClick="swapDatabaseRowMenu(\'' + data + '\')">' +
               '<i class="material-icons" id="database-icon-' + data + '">chevron_right</i></a> ' +
               '<span hidden id="database-delete-' + data + '">' +
               '<a class="btn-floating waves-effect waves-light red lighten-2"' +
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

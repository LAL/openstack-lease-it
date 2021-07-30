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
function buildInstancesView(div_name, get_option, is_admin){
    var table_columns = [
        { data: 'name' },
        { data: 'project' },
        { data: 'created_at' },
        { data: 'lease_end' }
    ];
    if (is_admin) {
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
                render: function ( data, type, row, meta ) {
                        var now = new Date();
                        var lease_end = new Date(row.lease_end.slice(0,10));
                        if (meta.col == 0 && (div_name == "admin-instances" || div_name == "instances")) {
                                return buildInstanceRowMenu(data, row, is_admin) + formatText(data, MAX_STRING_LENGTH);
                        }
                        else {
                              	return formatText(data, MAX_STRING_LENGTH);
                        };
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
    buildInstanceRowMenu build a menu for each row of Instance Table
*/
function buildInstanceRowMenu(data, row, is_admin) {
        if (is_admin) {
            var menu = '<a class="btn-floating waves-effect waves-light tiny" onClick="swapInstanceRowMenu(\'' + row.id + '\')">' +
                       '<i class="material-icons" id="instance-admin-icon-' + row.id + '">chevron_right</i></a> ' +
                       '<span hidden id="instance-admin-delete-' + row.id + '">' +
                       '<a class="btn-floating waves-effect waves-light red lighten-2"' +
                       'onClick="deleteDatabase(\'' + row.id + '\')">' +
                       '<i class="material-icons">delete</i></a></span> ';
        }
        else {
                    var menu = '<a class="btn-floating waves-effect waves-light tiny" onClick="swapInstanceRowMenu(\'' + row.id + '\')">' +
                           '<i class="material-icons" id="instance-icon-' + row.id + '">chevron_right</i></a> ' +
                           '<span hidden id="instance-delete-' + row.id + '">' +
                           '<a class="btn-floating waves-effect waves-light red lighten-2"' +
                           'onClick="deleteDatabase(\'' + row.id + '\')">' +
                           '<i class="material-icons">delete</i></a></span> ';

            };
    return menu;
}

/*
    swapInstanceRowMenu swap on/off the delete button
*/
function swapInstanceRowMenu(button) {
    if ($('#instance-delete-' + button).css('display') == 'none') {
        $('#instance-icon-' + button).text('chevron_left');
    }
    if ($('#instance-admin-delete-' + button).css('display') == 'none') {
        $('#instance-admin-icon-' + button).text('chevron_left');
    }
    else {
	$('#instance-icon-' + button).text('chevron_right');
        $('#instance-admin-icon-' + button).text('chevron_right');

    }
    $('#instance-delete-' + button).toggle();
    $('#instance-admin-delete-' + button).toggle();
}


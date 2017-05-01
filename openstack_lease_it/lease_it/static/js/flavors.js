
/*
  Retrieve useful information about OpenStack
  a dictionnary of flavor and for each flavor
   * CPU allocated by flavor
   * RAM allocated by flavor
   * Disk allocated by flavor
   * Total VM w/ this flavor that can be run on Cloud
   * Maximum VM w/ this flavor that can be run on Cloud if it s empty
*/
function flavorsStatus() {
    return $.getJSON("/flavors", function(data) {
        return data;
    });
}

/*
    Each flavor information is disabled by a materializeCSS card buildCard
    build a div contain all information for a specific flavor w/ its specific
    details (CPU / RAM / Disk / Free / Max)
*/
function buildFlavorView(flavor, details) {
    var flavor_underscore = details.name.replace(/\./g,"");
    return  '<div class="col s12 m6 l4 xl3"' +
            '     data-name="' + flavor_underscore + '"' +
            '     data-cpu="' + details.cpu + '"' +
            '     data-ram="' + details.ram + '"' +
            '     data-disk="' + details.disk + '"' +
            '     data-free="' + details.free + '"' +
            '     data-max="' + details.max + '"' +
            '>' +
            '  <div class="card hoverable">' +
            '    <div class="card-image activator">' +
            '      <div class="activator" id="' + flavor_underscore + '"></div>' +
            '    </div>' +
            '    <div class="card-content">' +
            '      <span class="card-title activator">' + flavor +
            '       <i class="material-icons right">more_vert</i>' +
            '      </span>' +
            '    </div>' +
            '    <div class="card-reveal">' +
            '      <span class="card-title">' + flavor +
            '      <i class="material-icons right">close</i>' +
            '      </span>' +
            '      <ul class="collection">' +
            '          <li class="collection-item"><div><span class="badge">' + details.cpu + '</span>CPU</div></li>' +
            '          <li class="collection-item"><div><span class="badge">' + details.ram + ' MB</span>RAM</div></li>' +
            '          <li class="collection-item"><div><span class="badge">' + details.disk + ' GB</span>Disk</div></li>' +
            '      </ul>' +
            '      </div>' +
            '    </div>' +
            '  </div>' +
            '</div>';
}

/*
  Create highcharts for Flavor dashboard
*/
function buildHighCharts(flavor, details) {
    /*
        flavor can have . in name that is not a valid name for
        HTML id or class. We remove it.
    */
    var flavor_underscore = details.name.replace(/\./g,"");
    return new Highcharts.Chart({ //nosonar
        /*
            solidgauge is easiest to read
        */
        chart: {
            renderTo: flavor_underscore,
            type: 'solidgauge',
            height: 150,
            background: {
                shape: 'arc'
            },
        },

        title: null, // No title needed

        pane: {
            size: '200%', // As the image will be splited by 2, we double up the size to can all spaces
            startAngle: -90, // Only half circle
            endAngle: 90, // Only half circle
            center: [ '50%', '100%' ], // Fix the center point as by default it s defined for circle
            background: null,
        },

        yAxis: [{
            stops: [
                [0.1, '#DF5353'], // Red if less than 10% available
                [0.3, '#DDDF0D'], // Orange if less than 30% avaible
                [0.4, '#55BF3B'] // Green for another cases
            ],
            min: 0,
            max: details.max, // Scale is based on the maximum flavor we can launch
        }],
        series:[{
            data : [ details.free ],
            dataLabels: { // Just a custom format
                format: '<div style="text-align:center"><span style="font-size:25px">{y}</span></div>',
                borderWidth: 0,
            },
        }],
    });
}

/*
    buildFlavorView create a full display of Flavor on div_name
*/
function buildFlavorsView(flavors, flavor_min, div_name){
    $(div_name).html('');
    $.each(flavors, function(flavor, details){
        if (details.free > flavor_min) {
            $(buildFlavorView(flavor, details)).appendTo(div_name);
            buildHighCharts(flavor, details);
        }
    });
}
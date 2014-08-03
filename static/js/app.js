var orgullopr = {
	SCRIPT_ROOT: '',
	init: function() {
		this.SCRIPT_ROOT = '{{ request.script_root|tojson|safe }}'; // application location
	},
	showForm: function() {
		$('.form-wrapper').show();
		$('.button-wrapper').hide();
	},
	hideForm: function() {
		$('.form-wrapper').hide();
		$('.button-wrapper').show();
	}
};

var mapOperator = {
    puertoRico: {},
    pueblos: {},
    tooltip: {},
    init: function() {
			this.tooltip = d3.select('#map').append('div').attr('class', 'tooltip');
			var config = {
				node: $('#map')[0],
				tiles: ['pueblos'],
				size: 'medium',
				'background-color': 'rgba(104,203,245,1)',
				'stroke-color': 'rgba(255,255,255,1)',
				'stroke-width': 2,
				'mouseover-stroke-width': 5,
				'mouseover-labels': true,
				on_ready: this.bindActions,
  			events: {
					on_click: this.seeTownVideos
  			}

    	};
    	this.puertoRico = new AtlasPR(config);
			return this;
    },

    seeTownVideos: function(feature, svg_path) {
        window.open("/explora#" + feature.properties.NAME, "_self");
    },
    getTownVideos: function(feature, svg_path) {
    	var videos = {};
    	$.ajax({
    		type: 'GET',
    		url: '/municipios/' + feature.properties.NAME,
    		contentType: 'application/json',
    		dataType: 'json',
    		success: function(data) {
    			for (var i = 0; i < data.length; i++) {
    				var li = $('<li />', { class: 'new'} ).append($('<iframe />', {
    					src: data[i]['youtube_vid_id'],
    					name: data[i]['name']
    				}));
    				$('ul').append(li.html());
    			}
    		}
    	});
    },

    bindActions: function() {
        var pueblos = mapOperator.puertoRico.svg.selectAll('.pueblos');
        pueblos.on('mouseover', function(d, i) {
					d3.select(this).style('stroke-width', 5);
					$('#name').text(d.properties.NAME);
				})
        .on('mouseout',  function(d,i) {
					d3.select(this).style('stroke-width', 3);
          $('#name').text('');
        });
    }
}

    $(document).ready(function() {
    $('#btnSort').click(function(e) {
        $("#ddlList").html($('#ddlList option').sort(function(x, y) {
            return $(x).text() < $(y).text() ? -1 : 1;
        }))
        $("#ddlList").get(0).selectedIndex = 0;
        e.preventDefault();
    });

    $('#btnSortVal').click(function(e) {
        $("#ddlList").html($('#ddlList option').sort(function(x, y) {
            return $(x).val() < $(y).val() ? -1 : 1;
        }))
        $("#ddlList").get(0).selectedIndex = 0;
        e.preventDefault();
    });
});

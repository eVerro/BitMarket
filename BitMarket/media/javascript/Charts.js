function CreateCharts(leftCurrency, rightCurrency, dateRange) {
	// Glucose Average by Day chart
	var avgByDayOptions = {
		chart : {
			renderTo : 'chart_panel',
			type : 'line',
		},
		legend : {
			enabled : false
		},
		title : {
			text : 'Średnie ceny '+ rightCurrency +' w '+ leftCurrency
		},
		subtitle : {
			text : 'Ostatni miesiąc'
		},
		xAxis : {
			title : {
				text : 'Dzień'
			},
			labels : {
				rotation : -45
			}
		},
		yAxis : {
			min : 0,
			title : {
				text : 'Cena'
			}
		},
		series : [{}],
	};

	var chartDataUrl = "/chart_data?leftCurr=" + leftCurrency + "&rightCurr=" + rightCurrency + "&dateRange=" + dateRange;
	$.getJSON(chartDataUrl, function(data) {
		avgByDayOptions.xAxis.categories = data['chart_data']['dates'];
		avgByDayOptions.series[0].name = 'Średnia cena';
		avgByDayOptions.series[0].data = data['chart_data']['values'];
		var chart = new Highcharts.Chart(avgByDayOptions);
	});

}

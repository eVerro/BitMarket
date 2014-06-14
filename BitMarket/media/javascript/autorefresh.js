var left_table_scroll = 0;
var right_table_scroll = 0;
var history_table_scroll = 0;

var left_curr;
var right_currency;

function AutoRefreshWallet(left_currency, right_currency) {
	Dajaxice.BitMarket.index.createTable(Dajax.process, {
		'left_currency' : left_currency,
		'right_currency' : right_currency
	});

	left_curr = left_currency;
	right_curr = right_currency;
	

	var refresh_rate = 5;
	var last_user_action = 0;
	var has_focus = false;

	

	function reset() {
		last_user_action = 0;
	}

	function windowHasFocus() {
		has_focus = true;
	}

	function windowLostFocus() {
		has_focus = false;
	}

	setInterval(function() {
		last_user_action++;
		refreshCheck();
	}, 1000);

	function refreshCheck() {
		var focus = window.onfocus;
		if (last_user_action >= refresh_rate && document.readyState == "complete") {

			recreateTable();
			reset();

		}

	}


	window.addEventListener("focus", windowHasFocus, false);
	window.addEventListener("blur", windowLostFocus, false);
	window.addEventListener("click", reset, false);
	window.addEventListener("mousemove", reset, false);
	window.addEventListener("keypress", reset, false);
}

function recreateTable(){
	left_table_scroll = $(".form_table #left_table tbody").scrollTop();
	right_table_scroll = $(".form_table #right_table tbody").scrollTop();
	history_table_scroll = $(".form_table #history_table tbody").scrollTop();
	
	Dajaxice.BitMarket.index.createTable(Dajax.process, {
				'left_currency' : left_curr,
				'right_currency' : right_curr
			});
}

function scrollRefresh() {

		$(".form_table #left_table tbody").scrollTop(left_table_scroll);
		$(".form_table #right_table tbody").scrollTop(right_table_scroll);
		$(".form_table #history_table tbody").scrollTop(history_table_scroll);
	}
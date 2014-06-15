var scroll_position;

function RefreshTable() {
	
	Dajaxice.BitMarket.index.createOpenOrders(Dajax.process);
	
}

function cancelCommission(commId){
	scroll_position = $('#open_orders_table tbody').scrollTop();
	Dajaxice.BitMarket.index.cancelComm(Dajax.process,{'comm_id':commId});
	$('#msg_label').css('color', 'green');
	$('#msg_label').html('Anulowano zlecenie.');
	$('#msg_label').slideDown();
	setTimeout(function(){$('#msg_label').slideUp();}, 3000);
}

function setScrollPosition(){
	$('#open_orders_table tbody').scrollTop(scroll_position);
	
}

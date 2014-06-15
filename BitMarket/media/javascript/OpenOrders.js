function RefreshTable() {
	
	Dajaxice.BitMarket.index.createOpenOrders(Dajax.process);
	
}

function cancelCommission(commId){
	
	Dajaxice.BitMarket.index.cancelComm(Dajax.process,{'comm_id':commId});
	$('#msg_label').css('color', 'green');
	$('#msg_label').html('Anulowano zlecenie.');
	$('#msg_label').slideDown();
	setTimeout(function(){$('#msg_label').slideUp();}, 3000);
}


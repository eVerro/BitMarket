function isNumberKey(evt) {
	var charCode = (evt.which) ? evt.which : event.keyCode;
	if (charCode > 31 && (charCode != 46 && (charCode < 48 || charCode > 57)))
		return false;
	return true;
	
}

function validate(site) {

	var First_Amount = $("#First_Amount_"+site).val();
	var Second_Amount = $("#Second_Amount_"+site).val();

	if (First_Amount != "" && Second_Amount != "") {
		if (site == 'L') {
			Dajaxice.BitMarket.index.validate(Dajax.process, {
				'first_amount' : First_Amount,
				'second_amount' : Second_Amount,
				'site' : site
			});
		}
		if (site == 'R') {
			Dajaxice.BitMarket.index.validate(Dajax.process, {
				'first_amount' : First_Amount,
				'second_amount' : Second_Amount,
				'site' : site
			});
		}
	}
	else
	{
		Dajaxice.BitMarket.index.resetFields(Dajax.process,{
			'site':site
			});	
	}
}

function createCommission(type, first_cryptocurrency, second_cryptocurrency){
	if (type=='buy'){
		var first_amount = new Decimal($('#First_Amount_L').val());
		var second_amount = new Decimal($('#Second_Amount_L').val());
		var end_date = $('#datepicker_L').val()+' '+$('#timepicker_L').val();
		
		Dajaxice.BitMarket.index.createCommision(Dajax.process,{
			'source_amount':first_amount.toString(),
			'destination_amount':first_amount.mul(second_amount).toString(), 
			'source_wallet_name':first_cryptocurrency, 
			'destination_wallet_name':second_cryptocurrency,
			'end_date': end_date
			});
	}
	else
	{
		var first_amount = new Decimal($('#First_Amount_R').val());
		var second_amount = new Decimal($('#Second_Amount_R').val());
		var end_date = $('#datepicker_R').val()+' '+$('#timepicker_R').val();
		
		Dajaxice.BitMarket.index.createCommision(Dajax.process,{
			'source_amount':first_amount.toString(),
			'destination_amount':first_amount.div(second_amount).toString(), 
			'source_wallet_name':second_cryptocurrency, 
			'destination_wallet_name':first_cryptocurrency,
			'end_date': end_date
			});
	}
}

function show_err (){
	$('#msg_label').css('color', 'red');
	$('#msg_label').html('Masz niewystarczającą ilość pieniędzy lub wpisałeś złą date .');
	$('#msg_label').slideDown();
	setTimeout(function(){$('#msg_label').slideUp();}, 3000);
}

function show_msg (){
	$('#msg_label').css('color', 'green');
	$('#msg_label').html('Dodano zlecenie.');
	$('#msg_label').slideDown();
	setTimeout(function(){$('#msg_label').slideUp();}, 3000);
	setTimeout(function(){location.reload();}, 4000);
}

function show_realize_msg(){
	$('#msg_label').css('color', 'green');
	$('#msg_label').html('Zrealizowano zlecenie');
	$('#msg_label').slideDown();
	setTimeout(function(){$('#msg_label').slideUp();}, 3000);
	setTimeout(function(){location.reload();}, 4000);
	
}
function show_realize_err(){
	$('#msg_label').css('color', 'red');
	$('#msg_label').html('Brak Kasy');
	$('#msg_label').slideDown();
	setTimeout(function(){$('#msg_label').slideUp();}, 3000);	
}
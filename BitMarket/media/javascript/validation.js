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

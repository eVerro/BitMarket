function changePass(old_pass,pass,sec_pass){
	
	Dajaxice.BitMarket.index.changePass(Dajax.process,{
		'old_password':old_pass,
		'password':pass,
		'sec_password':sec_pass
		});
}

function changeEmail(old_email,email,sec_email){
	if(IsEmail(old_email)&& IsEmail(email) && IsEmail(sec_email)){
		Dajaxice.BitMarket.index.changeEmail(Dajax.process,{
		'old_email':old_email,
		'email':email,
		'sec_email':sec_email
		});
	}
	else{
		emailErr();
	}
	
	
}

function IsEmail(email) {
  var regex = /^([a-zA-Z0-9_.+-])+\@(([a-zA-Z0-9-])+\.)+([a-zA-Z0-9]{2,4})+$/;
  return regex.test(email);
}

function emailErr(){
	$('#email_msg').css('color', 'red');
	$('#email_msg').html('Niepoprawne adresy email');
	$('#email_msg').slideDown();
	resetEmail();
	setTimeout(function(){$('#email_msg').slideUp();}, 3000);
}

function passErr(){
	$('#pass_msg').css('color', 'red');
	$('#pass_msg').html('Niepoprawne hasła');
	$('#pass_msg').slideDown();
	resetPass();
	setTimeout(function(){$('#pass_msg').slideUp();}, 3000);
}

function emailSuccess(){
	$('#email_msg').css('color', 'green');
	$('#email_msg').html('Zmieniono adres email');
	$('#email_msg').slideDown();
	resetEmail();
	setTimeout(function(){$('#email_msg').slideUp();}, 3000);
}


function passSuccess(){
	$('#pass_msg').css('color', 'green');
	$('#pass_msg').html('hasło zmienione');
	$('#pass_msg').slideDown();
	resetPass();
	setTimeout(function(){$('#pass_msg').slideUp();}, 3000);	
}

function resetEmail(){
	$('#old_email').val('');
	$('#email').val('');
	$('#sec_email').val('');
}

function resetPass(){
	$('#old_password').val('');
	$('#password').val('');
	$('#sec_password').val('');
}
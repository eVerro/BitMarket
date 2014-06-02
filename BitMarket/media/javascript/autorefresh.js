function AutoRefreshWallet (source, destination){    
	Dajaxice.BitMarket.index.createTable(Dajax.process,{'source':source, 'destination':destination}); 
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
	
	setInterval(function () {
	    last_user_action++;
	    refreshCheck();
	}, 1000);
	
	function refreshCheck() {
	    var focus = window.onfocus;
	    if (last_user_action >= refresh_rate && document.readyState == "complete"){
	        Dajaxice.BitMarket.index.createTable(Dajax.process,{'source':source, 'destination':destination}); 
	        reset();
	    }
	
	}
	window.addEventListener("focus", windowHasFocus, false);
	window.addEventListener("blur", windowLostFocus, false);
	window.addEventListener("click", reset, false);
	window.addEventListener("mousemove", reset, false);
	window.addEventListener("keypress", reset, false);
}  
   
   
 
     
 
var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
document.write(unescape("%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'%3E%3C/script%3E"));

var masterTracker = null; 
var siloTracker = null;

function startAnalytics() {
  masterTracker = _gat._getTracker("UA-1876445-9");  
  masterTracker._setDomainName("none");
  masterTracker._setAllowLinker(true); 
  masterTracker._trackPageview();

  siloTracker = _gat._getTracker(thirtySevenSiloTrackerId);  
  siloTracker._setDomainName("none");
  siloTracker._trackPageview();
}

function sendOffsite(link, urchinTrackerName) {
	if (urchinTrackerName != undefined) {
		masterTracker._trackPageview(urchinTrackerName);
		siloTracker._trackPageview(urchinTrackerName);
	} else {
		masterTracker._trackPageview(link.href.split('/')[2]);
		siloTracker._trackPageview(link.href.split('/')[2]);
	}

	masterTracker._link(link.href);
	return false;
}

if (window.addEventListener) {
	window.addEventListener('load', startAnalytics, false);
} else if (window.attachEvent) {
	window.attachEvent('onload', startAnalytics);
}

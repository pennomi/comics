// Initialize the BSA network
(function(){
		let bsa_optimize = document.createElement('script');
		bsa_optimize.type='text/javascript';
		bsa_optimize.async=true;
		bsa_optimize.src='{{ comic.bsa_link }}?'+(new Date()-new Date()%600000);
		(document.getElementsByTagName('head')[0]||document.getElementsByTagName('body')[0]).appendChild(bsa_optimize);
	})();


// Kickstart the ad loading
let adNetworkLoaded = false;
let adNetworkLoadAttempts = 0;
let kickstartInterval = setInterval(function () {
	adNetworkLoadAttempts += 1;

	if (adNetworkLoadAttempts > 1200) {  // Wait a whole 2 minutes
		// Give up, this thing will never load
		clearInterval(kickstartInterval);
		return;
	}

	// If this fails, we know BSA is not yet loaded. Keep trying.
	if (!(window.bsas2s && window.bsas2s.isInitialized)) {
			return;
	}

	// Otherwise, we're good to go. Stop the loop and load the ads
	clearInterval(interval);
	adNetworkLoaded = true;
	window.refreshAds();
}, 100);  // Every 10th of a second


let adLastRefreshed = 0;
window.refreshAds = function () {
	// Can't refresh if there's no ad network
	if (!adNetworkLoaded) {
		return;
	}

	// if the ad has been refreshed recently, ignore this
	const now = new Date().getTime();
	if (now - adLastRefreshed < 5000) {  // 5 seconds
			return;
	}

	try {
		window.optimize.pushAll();
		adLastRefreshed = now;
	} catch (error) {
		console.log("Ad network failed to refresh ads.");
	}
}

"use strict";


const QUESTS = function () {

    const initializePage = function () {
        console.log("Test initialized");

        // Bind all the share buttons to the socialShare function

    };

    const socialShare = function (platform, url, title, message) {
        if (platform === "navigator") {

        }

        console.log("Sharing to " + platform + ": " + url + " -- " + message);
        var options = 'toolbar=0,status=0,resizable=1,width=626,height=436';
        window.open(url, 'sharer', options);

        return true;
    };

    const navigatorShare = function (url, title, message) {
        if (!navigator.share) {
            return false;
        }
        navigator.share({
            url: url,
            text: text,
            title: title,
        });
    };

    // Run the initialization and then publish any variables that need to be public.
    return {
        initializePage: initializePage,
        socialShare: socialShare,
        navigatorShare: navigatorShare,
    };
}();

document.addEventListener("DOMContentLoaded", function(event) {
    QUESTS.initializePage();
});

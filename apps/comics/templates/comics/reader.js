"use strict";

var COMICS = function () {

    // Set up some global variables
    var CACHE = {};
    var COMIC = {
        "title": "{{ comic.title }}",
    };
    var NUM_ACTIVE_REQUESTS = 0;

    var bodyTag = document.getElementsByTagName("body")[0];
    var DISCOURSE_URL = bodyTag.dataset.discourseUrl;

    // Convenience function to set opacity on a query
    function setOpacity(querySelector, newOpacity) {
        document.querySelectorAll(querySelector).forEach(function (e) { e.style.opacity = newOpacity; });
    }

    // Make the current comic's data appear in the page
    function loadDataIntoDOM(pageData) {
        // Browser State
        var newTitle = pageData.title + " | " + COMIC.title;
        document.title = pageData.title;

        // Compute Tag HTML
        var tagHTML = "";
        pageData.tag_types.forEach(function (tagType) {
            var tagStrings = "";
            tagType.tags.forEach(function (tag){
                if (tag.icon !== "") {
                    tagStrings += `<a class="tag" style="background-image: url(${tag.icon});" href="${tag.url}">${tag.title}</a>`;
                } else {
                    tagStrings += `<a class="tag" href="${tag.url}">${tag.title}</a>`;
                }
            });

            tagHTML += `<p>${tagType.title}: ${tagStrings}</p>`;
        });

        // Page Content
        document.getElementById("comic-title").innerHTML = pageData.title;
        document.getElementById("comic-tags").innerHTML = tagHTML;
        document.getElementById("comic-post-date").innerHTML = pageData.posted_at;
        document.getElementById("comic-post").innerHTML = pageData.post;
        document.getElementById("comic-transcript").innerHTML = pageData.transcript;
        document.getElementById("comic-image").src = pageData.image;
        document.getElementById("comic-image").title = pageData.alt_text;
        setOpacity("#comic-image", 0.5);
        setOpacity("#comic-image-spinner", 1);

        if (sessionStorage.getItem("admin") === "true") {
            document.getElementById("staff-text").style.display = "block";
            document.getElementById("staff-link").href = pageData.admin;
        }

        // Navigation Buttons
        recalculateNavigationVisibility();
    }

    // Make the navigation buttons appear or disappear
    function recalculateNavigationVisibility() {
        // TODO: Do this with a CSS class
        if (NUM_ACTIVE_REQUESTS > 0) {
            setOpacity(".comic-navigation", 0.5);
        } else {
            setOpacity(".comic-navigation", 1);
        }

        var page = getActivePageData()

        if (page === undefined) {
            // We're still loading
            return;
        }

        // TODO: Change these into CSS class for "hidden"
        if (page.slug === page.last) {
            setOpacity(".navigation-next, .navigation-last", 0);
        } else {
            setOpacity(".navigation-next, .navigation-last", 1);
        }
        if (page.slug === page.first) {
            setOpacity(".navigation-previous, .navigation-first", 0);
        } else {
            setOpacity(".navigation-previous, .navigation-first", 1);
        }

        document.querySelectorAll(".navigation-first, .navigation-previous, .navigation-next, .navigation-last").forEach(function (e) { e.blur(); });
    }

    function imageLoaded() {
        setOpacity("#comic-image", 1);
        setOpacity("#comic-image-spinner", 0);
    }

    function getActivePageData() {
        return CACHE[getComicAndPageFromActiveUrl().pageSlug];
    }

    // Kickstart the page load
    function initializePage() {
        requestPageData(getComicAndPageFromActiveUrl().pageSlug, function (response) {
            navigateToPage(response.slug, false);
        });
    };

    function navigateToPage(pageSlug, pushState=true) {
        var pageData = CACHE[pageSlug];

        // This should never happen, but it's protection
        if (pageData === undefined) {
            console.log("Can't navigate, unknown destination. " + pageSlug);
            return;
        }

        // We don't push the state on the initial load or if using the back/forward buttons
        // We also don't care if there are outstanding requests in those cases
        if (pushState) {
            if (NUM_ACTIVE_REQUESTS > 0) {
                console.log("Can't navigate, " + NUM_ACTIVE_REQUESTS + " active requests.");
                return;
            }
            window.history.pushState(pageData, pageData.title, '/comic/' + pageData.slug + "/");
        }

        // Render the new page
        loadDataIntoDOM(pageData);

        // If we're currently not able to see the top of the next page, scroll up to it
        var readerElement = document.getElementById("reader");
        readerElement.scrollIntoView({behavior: "smooth"});

        // Tell Google Analytics that we successfully loaded the page
        if ("ga" in window && ga.getAll !== undefined) {
            var tracker = ga.getAll()[0];
            if (tracker) {
                tracker.set('page', window.location.pathname);
                tracker.send('pageview');
            }
        }

        // Try to refresh the ad
        refreshAd();

        // Try to refresh the comments
        refreshDiscourseComments();

        // Cache all the pages we can navigate to from this page
        requestPageData(pageData.first, function (response) { });
        requestPageData(pageData.previous, function (response) { });
        requestPageData(pageData.next, function (response) { });
        requestPageData(pageData.last, function (response) { });
    }

    // The next 4 functions perform the navigation.
    function firstButtonPressed() {
        navigateToPage(getActivePageData().first);
        return false;
    }

    function previousButtonPressed() {
        navigateToPage(getActivePageData().previous);
        return false;
    }

    function nextButtonPressed() {
        navigateToPage(getActivePageData().next);
        return false;
    }

    function lastButtonPressed() {
        navigateToPage(getActivePageData().last);
        return false;
    }

    // Make an AJAX request to get data
    function requestPageData(pageSlug, callback) {
        // Don't try to get missing pages
        if (pageSlug === null) {
            return;
        }

        if (CACHE[pageSlug] !== undefined) {
            callback(CACHE[pageSlug]);
            recalculateNavigationVisibility();
            return;
        }

        // Make the nav buttons go transparent
        NUM_ACTIVE_REQUESTS += 1;
        recalculateNavigationVisibility();

        // Execute the request
        var url = "/comic/data/" + pageSlug + "/";
        var request = new XMLHttpRequest();
        request.onreadystatechange = function() {
            if (request.readyState == 4 && request.status == 200) {
                try {
                    var data = JSON.parse(request.responseText);
                } catch(err) {
                    console.log(err.message + " in " + request.responseText);
                    return;
                }

                // Run the callback and update the navigation state
                CACHE[pageSlug] = data;
                callback(data);

                // Make the nav buttons go opaque
                NUM_ACTIVE_REQUESTS -= 1;
                recalculateNavigationVisibility();

                // Pre-warm the image cache
                preloadImage(data.image);
            }
        };
        request.open("GET", url, true);
        request.send();
    }

    function preloadImage(url) {
        var img = new Image();
        img.onload = function() {
            img.src = "";
            img = null;
        }
        img.src = url;
    }

    // Implement keyboard navigation using the arrow keys
    function keyboardNav(event) {
        // handling Internet Explorer stupidity with window.event
        // @see http://stackoverflow.com/a/3985882/517705
        var keyDownEvent = event || window.event;
        var keycode = (keyDownEvent.which) ? keyDownEvent.which : keyDownEvent.keyCode;
        var LEFT = 37;
        var RIGHT = 39;
        if (keyDownEvent.altKey) {
            return true;
        }
        if (keycode === LEFT) {
            previousButtonPressed();
            return false;
        } else if (keycode === RIGHT) {
            nextButtonPressed();
            return false;
        }
        return true;
    }
    document.onkeydown = keyboardNav;

    var adLastRefreshed = new Date().getTime();
    function refreshAd() {
        try {
            // if the ad has been refreshed recently, ignore this
            var now = new Date().getTime();
            if (now - adLastRefreshed < 30000) {  // 30 seconds
                return;
            }

            // clear the element out entirely and rebind it
            var adContainer = document.getElementById("ad-banner");
            adContainer.innerHTML = `
            <ins class="adsbygoogle"
              style="display:block"
              data-ad-client="ca-{{ comic.adsense_publisher_account }}"
              data-ad-slot="{{ comic.adsense_ad_slot }}"
              data-ad-format="auto"
              data-full-width-responsive="true"></ins>
            `;

            (adsbygoogle = window.adsbygoogle || []).push({});
            adLastRefreshed = now;
        }
        catch (error) {
            console.log("Ad network not loaded, will try again next time the page navigates.");
        }
    }

    function refreshDiscourseComments() {
        if (!DISCOURSE_URL) {
            return;
        }
        try {
            var url = new URL(document.location);
            window.DiscourseEmbed = {
                discourseUrl: DISCOURSE_URL,
                discourseEmbedUrl: url.origin + url.pathname
            };

            // If the comments chain already exists, remove it
            var discourseScript = document.getElementById('discourse-script');
            if (discourseScript) {
                discourseScript.remove();
            }
            var discourseComments = document.getElementById('discourse-comments');
            if (discourseComments) {
                discourseComments.innerHTML = '';
            }

            // Create a script tag that loads the comments into the #discourse-comments tag
            var d = document.createElement('script');
            d.id = 'discourse-script';
            d.type = 'text/javascript';
            d.async = true;
            d.src = window.DiscourseEmbed.discourseUrl + 'javascripts/embed.js';
            document.getElementsByTagName('head')[0].appendChild(d);
        } catch (error) {
            console.log("Comments not loaded, will try again next time the page navigates.");
        }
    }

    function getComicAndPageFromActiveUrl() {
        var url = new URL(document.location).pathname;
        var split = url.split('/');
        return {"pageSlug": split[2]};
    }

    window.onpopstate = function(event) {
        navigateToPage(getComicAndPageFromActiveUrl().pageSlug, false);
    };

    // Run the initialization and then publish any variables that need to be public.
    return {
        initializePage: initializePage,
        firstButtonPressed: firstButtonPressed,
        previousButtonPressed: previousButtonPressed,
        nextButtonPressed: nextButtonPressed,
        lastButtonPressed: lastButtonPressed,
        imageLoaded: imageLoaded,
    };
}();

document.addEventListener("DOMContentLoaded", function(event) {
    COMICS.initializePage();
});

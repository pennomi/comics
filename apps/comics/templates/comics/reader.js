"use strict";

const COMICS = function () {

    // Set up some global variables
    const CACHE = {};
    const COMIC = {
        "title": "{{ comic.title }}",
    };
    let NUM_ACTIVE_REQUESTS = 0;

    const bodyTag = document.getElementsByTagName("body")[0];
    const DISCOURSE_URL = bodyTag.dataset.discourseUrl;

    // Convenience function to set opacity on a query
    function setOpacity(querySelector, newOpacity) {
        document.querySelectorAll(querySelector).forEach(function (e) {
            e.style.opacity = newOpacity;
        });
    }

    // Make the current comic's data appear in the page
    function loadDataIntoDOM(pageData) {
        // Browser State
        document.title = pageData.title + " | " + COMIC.title;

        // Compute Tag HTML
        let tagHTML = "";
        pageData.tag_types.forEach(function (tagType) {
            let tagStrings = "";
            tagType.tags.forEach(function (tag) {
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

        if (localStorage.getItem("admin") === "true") {
            // TODO: instead of showing/hiding this, inject it
            document.getElementById("staff-text").style.display = "block";
            document.getElementById("staff-link").href = pageData.admin;
        }

        // Navigation Buttons
        recalculateNavigationVisibility();
    }

    // Make the navigation buttons appear or disappear
    function recalculateNavigationVisibility() {
        // TODO: This might be re-rendering the page too often because it's messing with the style directly.
        // TODO: Do this with a CSS class
        if (NUM_ACTIVE_REQUESTS > 0) {
            setOpacity(".navigation-wrapper", 0.5);
        } else {
            setOpacity(".navigation-wrapper", 1);
        }

        const page = getActivePageData();

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

        document.querySelectorAll(".navigation-first, .navigation-previous, .navigation-next, .navigation-last").forEach(function (e) {
            e.blur();
        });
    }

    function imageLoaded() {
        setOpacity("#comic-image", 1);
        setOpacity("#comic-image-spinner", 0);
    }

    function getActivePageData() {
        return CACHE[getComicAndPageFromActiveUrl().pageSlug];
    }

    // Kickstart the page load
    async function initializePage() {
        // Bind the tab functionality
        initializeTabs();

        // Load the page data
        const response = await requestPageData(getComicAndPageFromActiveUrl().pageSlug);
        await navigateToPage(response.slug, false);
    }

    async function navigateToPage(pageSlug, pushState = true) {
        const pageData = CACHE[pageSlug];

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
        const readerElement = document.getElementById("reader-panel");
        readerElement.scrollIntoView({behavior: "smooth"});

        // Tell Google Analytics that we successfully loaded the page
        if ("ga" in window && ga.getAll !== undefined) {
            var tracker = ga.getAll()[0];
            if (tracker) {
                tracker.set('page', window.location.pathname);
                tracker.send('pageview');
            }
        }

        // Try to refresh the ads
        refreshAds();

        // Try to refresh the comments
        refreshDiscourseComments();

        // Cache all the pages we can navigate to from this page
        await Promise.all([
            requestPageData(pageData.first),
            requestPageData(pageData.previous),
            requestPageData(pageData.next),
            requestPageData(pageData.last),
        ])
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
    async function requestPageData(pageSlug) {
        // Don't try to get missing pages
        if (pageSlug === null) {
            return;
        }

        if (CACHE[pageSlug] !== undefined) {
            recalculateNavigationVisibility();
            return CACHE[pageSlug];
        }

        // Make the nav buttons go transparent
        NUM_ACTIVE_REQUESTS += 1;
        recalculateNavigationVisibility();

        // Execute the request
        const response = await fetch("/comic/data/" + pageSlug + "/");
        const data = await response.json()

        // Run the callback and update the navigation state
        CACHE[pageSlug] = data;

        // Make the nav buttons go opaque
        NUM_ACTIVE_REQUESTS -= 1;
        recalculateNavigationVisibility();

        // Pre-warm the image cache
        preloadImage(data.image);

        return data;
    }

    function preloadImage(url) {
        let img = new Image();
        img.onload = function () {
            img.src = "";
            img = null;
        }
        img.src = url;
    }

    // Implement keyboard navigation using the arrow keys
    function keyboardNav(event) {
        // handling Internet Explorer stupidity with window.event
        const keycode = (event.which) ? event.which : event.keyCode;
        const LEFT = 37;
        const RIGHT = 39;
        if (event.altKey) {
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

    let adLastRefreshed = 0;
    function refreshAds() {
        try {
            // if the ad has been refreshed recently, ignore this
            const now = new Date().getTime();
            if (now - adLastRefreshed < 5000) {  // 5 seconds
                return;
            }

            window.optimize.pushAll()
        } catch (error) {
            console.log("Ad network not loaded, will try again next time the page navigates.");
        }
    }

    function refreshDiscourseComments() {
        if (!DISCOURSE_URL) {
            return;
        }
        try {
            const url = new URL(document.location);
            window.DiscourseEmbed = {
                discourseUrl: DISCOURSE_URL,
                discourseEmbedUrl: url.origin + url.pathname
            };

            // If the comments chain already exists, remove it
            const discourseScript = document.getElementById('discourse-script');
            if (discourseScript) {
                discourseScript.remove();
            }
            const discourseComments = document.getElementById('discourse-comments');
            if (discourseComments) {
                discourseComments.innerHTML = '';
            }

            // Create a script tag that loads the comments into the #discourse-comments tag
            const d = document.createElement('script');
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
        const url = new URL(document.location).pathname;
        const split = url.split('/');
        return {"pageSlug": split[2]};
    }

    function initializeTabs() {
        document.querySelectorAll('.tab').forEach(function (element) {
            element.addEventListener('click', function (event) {
                const target = event.target.dataset.target;
                activateTab(target);
            });
        });

        let activeTab = localStorage.getItem("comics.activeTab");
        if (activeTab === null || !["info-frame", "comments-frame", "quests-frame"].includes(activeTab)) {
            activeTab = "info-frame";
        }
        activateTab(activeTab);
    }

    function activateTab(target) {
        localStorage.setItem("comics.activeTab", target);

        // Set tab styling
        document.querySelectorAll('.tab').forEach(function (element) {
            if (element.dataset.target === target) {
                element.classList.add("active");
            } else {
                element.classList.remove("active");
            }
        });

        // Set content styling
        document.querySelectorAll('.tab-content-area').forEach(function (element) {
            if (element.id === target) {
                element.style.display = "block";
            } else {
                element.style.display = "none";
            }
        });
    }

    window.onpopstate = function (event) {
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

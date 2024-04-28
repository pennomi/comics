
function initializePopups() {
    // Try to open one after 5 seconds
    window.setTimeout(attemptToShowPopup, 5000);

    // Clicking on the bg should close it
    document.querySelectorAll("dialog").forEach(e => {
        e.addEventListener('click', () => closePopup(e));
    });
}

function attemptToShowPopup() {
    const timeout = 1000 * 60 * 60 * 6;  // 6 hours

    // Check if we've shown a popup recently
    if (sessionStorage.lastInvite != null) {
        let timeSinceLastShown = Date.now() - sessionStorage.lastInvite;
        if (timeSinceLastShown < timeout) {
            return;
        }
    }

    // Try to show the popup
    const e = document.querySelector(".dialog-invitation");
    if (e === null || e.open) {
        return;
    }
    e.showModal();
    sessionStorage.lastInvite = Date.now();
}

function closePopup(e) {
    e.classList.add("is-hidden");
    e.addEventListener(
        "animationend",
        function () {
            if (e.classList.contains("is-hidden")) {
                e.classList.remove("is-hidden");
                e.close();
            }
        },
        false
    );
}

document.addEventListener("DOMContentLoaded", function(event) {
    initializePopups();
});

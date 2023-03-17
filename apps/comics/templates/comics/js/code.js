const secretCode = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a'];
let currentIndex = 0;

// add keydown event listener
document.addEventListener('keydown', function (e) {
    const requiredKey = secretCode[currentIndex];

    if (e.key === requiredKey) {
        currentIndex++;

        // if the last key is reached, activate cheats
        if (currentIndex === secretCode.length) {
            activateCheats();
            currentIndex = 0;
        }
    } else {
        currentIndex = 0;
    }
});

function activateCheats() {
    console.log("CHEATS ACTIVATED!")
    const dialog = document.createElement('dialog');
    dialog.innerHTML = `<img class="dialog-image" src="{{ comic.secret_image.url }}"/>`;
    document.body.appendChild(dialog);

    // Clicking on the bg should close it
    dialog.addEventListener('click', () => closePopup(dialog));

    // Show it
    dialog.showModal();
}
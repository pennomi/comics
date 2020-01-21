function filterResults(inputElement) {
    // Declare variables
    var query = inputElement.value.toLowerCase();

    var tiles = document.querySelectorAll(".archive-tile");
    tiles.forEach(function (tile) {
        tile.hidden = tile.dataset.title.toLowerCase().indexOf(query) == -1;
    });
}

function sortResults(selectElement) {
    var selection = selectElement.value;

    // Define common sorting functions
    var alphabetical = function(a, b) {
        return a.dataset.title.toLowerCase().localeCompare(b.dataset.title.toLowerCase());
    }
    var mostAppearances = function(a, b) {
        return parseInt(b.dataset.count) - parseInt(a.dataset.count);
    }
    var fewestAppearances = function(a, b) {
        return parseInt(a.dataset.count) - parseInt(b.dataset.count);
    }

    // Sort the array
    var tiles = Array.from(document.querySelectorAll(".archive-tile"));
    tiles.sort({
        alphabetical: alphabetical,
        mostAppearances: mostAppearances,
        fewestAppearances: fewestAppearances,
    }[selection]);

    // Reorder the elements
    tiles.forEach(function (tile) {
        tile.parentNode.appendChild(tile);
    });
}
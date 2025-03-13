document.addEventListener("DOMContentLoaded", function () {
    const filterOptions = document.querySelectorAll(".filter-option");
    const selectedFilterElement = document.getElementById("selectedFilter");
    const pageTitle = document.getElementById("pageTitle");

    const filterTextMap = {
        all: "View All Artworks",
        discount: "View Discount Artworks",
        auction: "View Auction Artworks",
    };

    // Get the filter value from URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const filter = urlParams.get("filter") || "all";

    // Update text content based on filter
    const filterText = filterTextMap[filter] || "View All Artworks";
    selectedFilterElement.textContent = filter === "all" ? "All Artworks" : filter.charAt(0).toUpperCase() + filter.slice(1);
    pageTitle.textContent = filterText;

    // Add click event listener for dynamic updates
    filterOptions.forEach(option => {
        option.addEventListener("click", function (event) {
            event.preventDefault(); // Prevent default link behavior
            const selectedFilter = this.getAttribute("data-filter").toLowerCase();
            const filterText = filterTextMap[selectedFilter] || "View All Artworks";
            selectedFilterElement.textContent = selectedFilter === "all" ? "All Artworks" : selectedFilter.charAt(0).toUpperCase() + selectedFilter.slice(1);
            pageTitle.textContent = filterText;

            // Navigate to the new URL
            const newUrl = this.getAttribute("href");
            window.location.href = newUrl;
        });
    });
});
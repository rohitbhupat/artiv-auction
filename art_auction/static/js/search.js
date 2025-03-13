let allItems = [];

document.addEventListener("DOMContentLoaded", function () {
    let fetchContainer = document.querySelector(".search-container");
    let fetchUrl = fetchContainer ? fetchContainer.getAttribute("data-fetch-url") : null;

    if (!fetchUrl) {
        console.error("Fetch URL not found! Check your template.");
        return;
    }

    console.log("Fetching from:", fetchUrl);

    fetch(fetchUrl)
        .then(response => response.json())
        .then(data => {
            if (data.artworks && data.catalogues && data.purchase_category) {
                allItems = [
                    ...data.artworks.map(a => ({
                        name: a.product_name,
                        url: `/viewdetails/${a.id}/` // Artwork detail URL
                    })),
                    ...data.catalogues.map(c => ({
                        name: c.cat_name,
                        url: `/cat/${c.id}/` // Catalogue URL
                    })),
                    ...data.purchase_category.map(p => ({
                        name: p.name,
                        url: `/purchase-cat/${p.id}/` // Purchase category URL
                    }))
                ];
            } else {
                console.error("Invalid response format:", data);
            }
            console.log("Fetched Data:", allItems);
        })
        .catch(error => console.error("Error fetching artworks:", error));
});

function fetchSuggestions() {
    let input = document.getElementById("searchBox").value.toLowerCase();
    let suggestionsList = document.getElementById("suggestions-list");

    if (!suggestionsList || !input.length) {
        suggestionsList.style.display = "none";
        return;
    }

    suggestionsList.innerHTML = "";  // Clear previous suggestions

    let filtered = allItems
        .filter(item => item.name.toLowerCase().includes(input)) 
        .slice(0, 5);

    if (filtered.length > 0) {
        suggestionsList.style.display = "block";
        filtered.forEach(suggestion => {
            let div = document.createElement("div");
            div.classList.add("suggestion-item");
            div.textContent = suggestion.name;
            div.setAttribute("data-url", suggestion.url);
            
            // Click redirection
            div.onclick = function() {
                window.location.href = suggestion.url;
            };

            suggestionsList.appendChild(div);
        });
    } else {
        suggestionsList.style.display = "none";
    }
}

// Hide suggestions when clicking outside
document.addEventListener("click", function(event) {
    if (!event.target.closest(".search-container")) {
        let suggestionsList = document.getElementById("suggestions-list");
        if (suggestionsList) suggestionsList.style.display = "none";
    }
});

document.addEventListener("DOMContentLoaded", function () {
    let searchBox = document.getElementById("searchBox");
    if (searchBox) {
        searchBox.addEventListener("keyup", fetchSuggestions);
        
        // Redirect when Enter is pressed
        searchBox.addEventListener("keypress", function (event) {
            if (event.key === "Enter") {
                event.preventDefault();
                let firstResult = document.querySelector(".suggestion-item");
                if (firstResult) {
                    window.location.href = firstResult.getAttribute("data-url");
                }
            }
        });
    }
});

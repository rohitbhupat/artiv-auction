(function () {
  const theme = localStorage.getItem("theme") || "auto";
  const prefersDarkScheme = window.matchMedia(
    "(prefers-color-scheme: dark)"
  ).matches;
  const isDarkMode =
    theme === "dark" || (theme === "auto" && prefersDarkScheme);

  if (isDarkMode) {
    document.body.classList.add("dark-mode");
  } else {
    document.body.classList.add("light-mode");
  }
})();

// Get the button
var mybutton = document.getElementById("back-to-top-btn");

// When the user scrolls down 20px from the top of the document, show the button
window.onscroll = function () {
  scrollFunction();
};

function scrollFunction() {
  if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
    mybutton.style.display = "block";
  } else {
    mybutton.style.display = "none";
  }
}

// When the user clicks on the button, scroll to the top of the document
function topFunction() {
  document.body.scrollTop = 0; // For Safari
  document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
}

function toggleHeart(icon, productId) {
    let csrfTokenElement = document.querySelector("input[name='csrfmiddlewaretoken']");
    if (!csrfTokenElement) {
        console.error("CSRF token is missing.");
        return;
    }
    let csrfToken = csrfTokenElement.value;
    
    console.log("Sending AJAX request for product ID:", productId); // Debugging line

    fetch("/toggle_favorite/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({ product_id: productId }),
    })
    .then(response => response.json())
    .then(data => {
        console.log("Response received:", data); // Debugging line
        if (data.status === "added") {
            icon.classList.remove("fa-regular");
            icon.classList.add("fa-solid", "active");
            showAlert("Artwork added to favorites!", "success");
        } else if (data.status === "removed") {
            icon.classList.remove("fa-solid", "active");
            icon.classList.add("fa-regular");
            showAlert("Artwork removed from favorites!", "error");
        }
    })
    .catch(error => console.error("Error:", error));
}


function showAlert(message, type) {
    let alertBox = document.getElementById("alert-box");
    let alertMessage = document.getElementById("alert-message");

    alertMessage.textContent = message;

    if (type === "success") {
        alertBox.classList.remove("error"); // Remove error class if present
        // alertBox.style.backgroundColor = "#4CAF50"; // Green for success
    } else if (type === "error") {
        alertBox.classList.add("error"); // Add error class
        // alertBox.style.backgroundColor = "#FF4C4C"; // Red for error
    }

    alertBox.style.display = "block";

    setTimeout(() => {
        alertBox.style.display = "none";
    }, 3000);
}


function getCSRFToken() {
    const tokenElement = document.querySelector(
      "#csrf-form input[name=csrfmiddlewaretoken]"
    );
    return tokenElement ? tokenElement.value : "";
}

document.addEventListener("DOMContentLoaded", function () {
    console.log("Loading favorite artworks..."); // Debugging line

    fetch("/get_favorites/")
        .then(response => response.json())
        .then(data => {
            console.log("Favorites loaded:", data); // Debugging line
            data.favorites.forEach(productId => {
                const icon = document.getElementById(`heart-${productId}`);
                if (icon) {
                    icon.classList.add("fa-solid", "active");
                    icon.classList.remove("fa-regular");
                }
            });
        })
        .catch(error => console.error("Error loading favorites:", error));
});

// Example Usage: Call these functions when adding/removing from favorites
function addToFavorites() {
  showAlert("Artwork added to favorites!", "success");
}

function removeFromFavorites() {
  showAlert("Artwork removed from favorites!", "error");
}

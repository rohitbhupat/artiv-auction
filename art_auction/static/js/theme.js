document.addEventListener("DOMContentLoaded", () => {
  const themeText = document.getElementById("bd-theme-text");
  const themeItems = document.querySelectorAll(".dropdown-item[data-theme]");
  const navbar = document.getElementById("navbar");

  // Function to apply theme
  const setTheme = (theme) => {
      if (!theme) return; // Prevent applying an empty theme

      // Remove previous theme classes
      document.body.classList.remove("light-mode", "dark-mode");
      document.documentElement.classList.remove("light-mode", "dark-mode");
      navbar.classList.remove("light-mode", "dark-mode");

      // Add the new theme
      document.body.classList.add(`${theme}-mode`);
      document.documentElement.classList.add(`${theme}-mode`);
      navbar.classList.add(`${theme}-mode`);

      // Update dropdown text
      themeText.innerText = theme === "light" ? "Light Mode" : "Dark Mode";

      // Save theme selection in localStorage
      localStorage.setItem("theme", theme);
  };

  // Retrieve theme from localStorage
  let storedTheme = localStorage.getItem("theme");
  
  // If theme is missing or invalid, default to "light"
  if (!storedTheme || (storedTheme !== "light" && storedTheme !== "dark")) {
      storedTheme = "light";
      localStorage.setItem("theme", "light");
  }

  // Apply the stored theme
  setTheme(storedTheme);

  // Event listener for theme selection from dropdown
  themeItems.forEach((item) => {
      item.addEventListener("click", (e) => {
          const selectedTheme = e.target.getAttribute("data-theme");
          setTheme(selectedTheme);
      });
  });
});

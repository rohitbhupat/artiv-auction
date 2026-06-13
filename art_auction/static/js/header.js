document.addEventListener('DOMContentLoaded', function () {
    const theme = localStorage.getItem('theme') || 'auto';
    applyTheme(theme);

    document.querySelectorAll('.theme-toggle').forEach(function (item) {
        item.addEventListener('click', function () {
            const selectedTheme = this.getAttribute('data-theme');
            applyTheme(selectedTheme);
            localStorage.setItem('theme', selectedTheme);
        });
    });
});

function applyTheme(theme) {
    document.body.classList.remove('light-mode', 'dark-mode');
    if (theme === 'dark') {
        document.body.classList.add('dark-mode');
    } else if (theme === 'light') {
        document.body.classList.add('light-mode');
    } else {
        const prefersDarkScheme = window.matchMedia("(prefers-color-scheme: dark)").matches;
        document.body.classList.add(prefersDarkScheme ? 'dark-mode' : 'light-mode');
    }
}

(function() {
    const theme = localStorage.getItem('theme') || 'auto';
    const prefersDarkScheme = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const isDarkMode = theme === 'dark' || (theme === 'auto' && prefersDarkScheme);
    
    if (isDarkMode) {
    document.body.classList.add('dark-mode');
    } else {
    document.body.classList.add('light-mode');
    }
})();

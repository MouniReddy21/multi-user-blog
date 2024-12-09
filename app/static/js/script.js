// document.addEventListener("DOMContentLoaded", () => {
//     const darkModeToggle = document.getElementById("dark-mode-toggle");
//     const body = document.body;

//     darkModeToggle.addEventListener("click", () => {
//         body.classList.toggle("dark-mode");
//     });
// });

document.getElementById('dark-mode-toggle').addEventListener('click', function() {
    document.body.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
});

// Check if dark mode is already set
if (localStorage.getItem('darkMode') === 'true') {
    document.body.classList.add('dark-mode');
}

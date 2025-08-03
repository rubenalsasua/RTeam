// static/js/convocatorias.js
document.addEventListener('DOMContentLoaded', function() {
    // Funcionalidad para exportar convocatorias
    const exportButtons = document.querySelectorAll('[data-export-format]');

    exportButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const formato = this.getAttribute('data-export-format');
            const url = this.getAttribute('href') + `?formato=${formato}`;
            window.location.href = url;
        });
    });
});
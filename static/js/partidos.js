// Funciones para la gestión de partidos
document.addEventListener('DOMContentLoaded', function () {
    // Selector de liga con cambio automático
    const ligaSelector = document.getElementById('ligaSelector');
    if (ligaSelector) {
        ligaSelector.addEventListener('change', function () {
            document.getElementById('ligaForm').submit();
        });
    }
});
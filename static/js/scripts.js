document.getElementById('submit-button').addEventListener('click', () => {
    const checkboxes = document.querySelectorAll('input[name="files"]:checked');
    const selectedFiles = Array.from(checkboxes).map(cb => cb.value);

    fetch('/generate_graphs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ selected_files: selectedFiles })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Chyba: ' + data.error);
        } else {
            alert('Grafy byly úspěšně vygenerovány.');
            // Zde můžete aktualizovat obsah #graph1 a #graph2
        }
    })
    .catch(error => {
        console.error('Chyba:', error);
    });
});
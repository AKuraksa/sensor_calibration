document.addEventListener('DOMContentLoaded', function() {
    const notepadToggle = document.getElementById('notepad-toggle');
    const notepad = document.getElementById('notepad');

    notepadToggle.addEventListener('click', function() {
        if (notepad.style.right === '0px') {
            notepad.style.right = '-100%';
        } else {
            notepad.style.right = '0px';
        }
    });
});
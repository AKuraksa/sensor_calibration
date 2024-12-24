document.addEventListener('DOMContentLoaded', function() {
    const notepadToggle = document.getElementById('notepad-toggle');
    const notepad = document.getElementById('notepad');

    notepadToggle.addEventListener('click', function() {
        if (notepad.style.left === '0px') {
            notepad.style.left = '-400px';
        } else {
            notepad.style.left = '0px';
        }
    });
});
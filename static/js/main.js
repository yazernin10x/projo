// Applique les styles DaisyUI aux champs existants
function applyDaisyUIStyles(element) {
    element.querySelectorAll('select').forEach(select => {
        select.classList.add('select', 'select-bordered', 'w-full');
    });
    element.querySelectorAll('input[type="text"]').forEach(input => {
        input.classList.add('input', 'input-bordered', 'w-full');
    });
}

// Applique les styles aux formulaires existants
document.querySelectorAll('.form-item').forEach(form => {
    applyDaisyUIStyles(form);
});

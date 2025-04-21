function openModal(id, type = 'project', action = 'delete') {
    event.preventDefault();
    event.stopPropagation();
    const modal = document.getElementById(`${action}_${type}_modal_${id}`);
    if (modal) {
        modal.showModal();
    } else {
        console.error(`Modal not found for ${type} ${id}`);
    }
}

function closeModal(id, type = 'project', action = 'delete') {
    const modal = document.getElementById(`${action}_${type}_modal_${id}`);
    if (modal) {
        modal.close();
    } else {
        console.error(`Modal not found for ${type} ${id}`);
    }
}

document.addEventListener('htmx:afterSwap', function(event) {
    id_splited = event.target.id.split('-');
    buttonId = `${id_splited[0]}_${id_splited[1]}_modal_${id_splited.pop()}`
    const modal = document.getElementById(buttonId);
    if (modal) {
        modal.showModal();
    }
});
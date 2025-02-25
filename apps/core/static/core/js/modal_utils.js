function openModal(id, type = 'project', action = 'delete') {
    event.preventDefault();
    event.stopPropagation();
    const modal = document.getElementById(`${action}_${type}_modal_${id}`);
    console.log(modal);
    console.log(`${action}_${type}_modal_${id}`);
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
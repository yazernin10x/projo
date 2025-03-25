function openDeleteModal(id, type = 'project') {
    event.preventDefault();
    event.stopPropagation();
    const modal = document.getElementById(`delete_${type}_modal_${id}`);
    if (modal) {
        modal.showModal();
    } else {
        console.error(`Modal not found for ${type} ${id}`);
    }
}

function closeDeleteModal(id, type = 'project') {
    const modal = document.getElementById(`delete_${type}_modal_${id}`);
    if (modal) {
        modal.close();
    } else {
        console.error(`Modal not found for ${type} ${id}`);
    }
}
document.addEventListener('DOMContentLoaded', function () {
    const modal = new bootstrap.Modal(document.getElementById('friends-modal'));
    const closeModal = document.querySelector('.close-modal');
    const friendsList = document.getElementById('friends-list');
    const modalTitle = document.getElementById('modal-title');

    document.querySelectorAll('.open-friends-list').forEach(link => {
        link.addEventListener('click', function (event) {
            event.preventDefault();
            const type = this.getAttribute('data-type');
            const username = this.getAttribute('data-username');

            friendsList.innerHTML = '';
            modalTitle.textContent = type.charAt(0).toUpperCase() + type.slice(1);

            fetch(`/profile/get_${type}/${username}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    if (Array.isArray(data)) {
                        if (data.length > 0) {
                            data.forEach(friend => {
                                const li = document.createElement('li');
                                const a = document.createElement('a');
                                a.href = `/profile/${friend.username}`;
                                a.textContent = friend.username;
                                li.appendChild(a);
                                friendsList.appendChild(li);
                            });
                        } else {
                            friendsList.innerHTML = '<li>No users found.</li>';
                        }
                    } else {
                        friendsList.innerHTML = '<li>No users found.</li>';
                    }
                })
                .catch(error => console.error('Error fetching friends:', error));

            modal.show(); 
        });
    });

    closeModal.addEventListener('click', function () {
        modal.hide();
    });

    window.addEventListener('click', function (event) {
        if (event.target === document.getElementById('friends-modal')) {
            modal.hide(); 
        }
    });
});

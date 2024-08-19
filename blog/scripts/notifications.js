document.addEventListener('DOMContentLoaded', () => {
    const notificationsModal = document.getElementById('notificationsModal');
    const markAsReadButton = document.getElementById('mark-as-read');

    function fetchNotifications() {
        fetch('/profile/notifications')
            .then(response => response.json())
            .then(data => {
                const notificationsList = document.getElementById('notifications-list');
                notificationsList.innerHTML = '';

                if (data.notifications.length === 0) {
                    const listItem = document.createElement('li');
                    listItem.className = 'list-group-item';
                    listItem.textContent = 'No notifications';
                    notificationsList.appendChild(listItem);
                } else {
                    data.notifications.forEach(notification => {
                        const listItem = document.createElement('li');
                        listItem.className = 'list-group-item';
                        listItem.textContent = notification.message;
                        notificationsList.appendChild(listItem);
                    });
                }
            })
            .catch(error => console.error('Error fetching notifications:', error));
    }

    $(notificationsModal).on('show.bs.modal', () => {
        fetchNotifications();
    });
});

document.addEventListener('DOMContentLoaded', () => {
    async function fetchNotifications() {
        try {
            const response = await fetch('/profile/notifications');
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            const data = await response.json();
            return data.notifications;
        } catch (error) {
            console.error('Error fetching notifications:', error);
            return [];
        }
    }

    function renderNotifications(notifications) {
        const list = document.getElementById('notifications-list');
        list.innerHTML = ''; 
        notifications.forEach(notification => {
            const listItem = document.createElement('li');
            listItem.className = 'list-group-item d-flex justify-content-between align-items-center';
            listItem.innerHTML = `
                <span>${notification.message}</span>
                <button class="btn btn-sm" data-id="${notification._id}"><i class="fas fa-trash"></i></button>
            `;
            list.appendChild(listItem);
        });
    }

    async function deleteNotification(notificationId) {
        try {
            const response = await fetch(`/profile/notifications/${notificationId}`, {
                method: 'POST'
            });
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            const data = await response.json();
            if (data.message) {
                loadNotifications();
            } else {
                console.error('Error deleting notification:', data.error);
            }
        } catch (error) {
            console.error('Error deleting notification:', error);
        }
    }

    async function loadNotifications() {
        const notifications = await fetchNotifications();
        renderNotifications(notifications);
    }

    loadNotifications();

    document.getElementById('notifications-list').addEventListener('click', (event) => {
        if (event.target && event.target.matches('button')) {
            const notificationId = event.target.getAttribute('data-id');
            if (notificationId) {
                deleteNotification(notificationId);
            }
        }
    });
});

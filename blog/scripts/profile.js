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


function post_data(postId) {
    const modalContent = document.getElementById('modal-post-content');
    modalContent.innerHTML = '<p>Loading...</p>';  
    fetch(`/post_div/${postId}`)
        .then(response => response.text())
        .then(data => {
            console.log(data);
            modalContent.innerHTML = data;
            const likeButtons = document.querySelectorAll('.like-btn');

            likeButtons.forEach(button => {
                button.addEventListener('click', (event) => {
                    event.preventDefault();
                    const postUrl = button.getAttribute('data-post-url');
                    const postId = button.getAttribute('data-post-id');
                    const likesAmountElement = document.getElementById('likes_amount_' + postId);
                    const heartIcon = button.querySelector('i');
        
                    fetch(postUrl, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ postId })
                    })
                    .then(response => response.json())
                    .then(data => {
                        let currentLikes = parseInt(likesAmountElement.textContent.trim());
        
                        if (data.status === 'unliked') {
                            heartIcon.classList.remove('text-danger');
                            heartIcon.classList.add('text-secondary');
                            likesAmountElement.textContent = (currentLikes - 1).toString();
                        } else if (data.status === 'liked') {
                            heartIcon.classList.remove('text-secondary');
                            heartIcon.classList.add('text-danger');
                            likesAmountElement.textContent = (currentLikes + 1).toString();
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                    });
                });
            });

            const toggleContentButtons = document.querySelectorAll('.toggle-content-btn');
            const toggleCommentsButtons = document.querySelectorAll('.toggle-comments-btn');

            toggleContentButtons.forEach(button => {
                button.addEventListener('click', function () {
                    const targetId = button.getAttribute('data-target');
                    const postContent = document.querySelector(targetId);

                    if (postContent) {
                        if (postContent.style.display === 'none' || postContent.style.display === '') {
                            postContent.style.display = 'block';
                            button.innerHTML = '<i class="fas fa-chevron-up"></i> Hide Content';
                        } else {
                            postContent.style.display = 'none';
                            button.innerHTML = '<i class="fas fa-chevron-down"></i> Show More';
                        }
                    }
                });

                // Initially hide the content if it's longer than 200 characters
                const targetId = button.getAttribute('data-target');
                const postContent = document.querySelector(targetId);

                if (postContent && postContent.innerHTML.length > 200) {
                    postContent.style.display = 'none';
                }
            });

            toggleCommentsButtons.forEach(button => {
                button.addEventListener('click', function () {
                    const targetId = button.getAttribute('data-target');
                    const commentsSection = document.querySelector(targetId);

                    if (commentsSection) {
                        if (commentsSection.style.display === 'none' || commentsSection.style.display === '') {
                            commentsSection.style.display = 'block';
                            button.innerHTML = '<i class="fas fa-chevron-up"></i> Hide Comments';
                        } else {
                            commentsSection.style.display = 'none';
                            button.innerHTML = '<i class="fas fa-chevron-down"></i> Show More Comments (' + (commentsSection.querySelectorAll('li').length) + ')';
                        }
                    }
                });

                // Initially hide the comments section
                const targetId = button.getAttribute('data-target');
                const commentsSection = document.querySelector(targetId);

                if (commentsSection) {
                    commentsSection.style.display = 'none';
                }
            });
        })
        .catch(error => {
            console.error('Error fetching post content:', error);
            modalContent.innerHTML = '<p>Error loading content.</p>';
        });
};
document.addEventListener('DOMContentLoaded', () => {
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
});



document.addEventListener('DOMContentLoaded', () => {
    const likeButtons = document.querySelectorAll('.like-btn');

    likeButtons.forEach(button => {
        button.addEventListener('click', () => {
            const postUrl = button.getAttribute('data-post-url');
            const postId = button.getAttribute('data-post-id');
            const likesAmount = document.getElementById('likes_amount_' + postId);
            
            fetch(postUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ postId })
            })
            .then(response => response.json())
            .then(data => {
                if (data === 0) {
                    button.setAttribute("class", "btn-primary");
                    button.textContent = "Like"
                    likesAmount.textContent = "Likes: " + (parseInt(likesAmount.textContent.split(": ")[1]) - 1).toString()
                } else {
                    button.setAttribute("class", "btn-outline-primary");
                    button.textContent = "Unlike"
                    likesAmount.textContent = "Likes: " + (parseInt(likesAmount.textContent.split(": ")[1]) + 1).toString()
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    });
});
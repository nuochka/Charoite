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


document.addEventListener("DOMContentLoaded", function() {
    var simplemde = new SimpleMDE({
        element: document.getElementById("text"),
        autoDownloadFontAwesome: false, 
        spellChecker: false
    });

    var textarea = document.getElementById("text");
    if (textarea) {
        console.log("SimpleMDE initialized successfully.");
    } else {
        console.error("SimpleMDE initialization failed.");
    }
});


document.addEventListener('DOMContentLoaded', function () {
    const toggleButtons = document.querySelectorAll('.toggle-comments-btn');

    toggleButtons.forEach(button => {
        button.addEventListener('click', function () {
            const targetId = button.getAttribute('data-target');
            const commentsSection = document.querySelector(targetId);

            if (commentsSection.style.display === 'none') {
                commentsSection.style.display = 'block';
                button.classList.remove('show-more');
                button.classList.add('hide-comments');
                button.innerHTML = '<i class="fas fa-chevron-up"></i> Hide Comments';
            } else {
                commentsSection.style.display = 'none';
                button.classList.remove('hide-comments');
                button.classList.add('show-more');
                button.innerHTML = '<i class="fas fa-chevron-down"></i> Show More Comments (' + (commentsSection.querySelectorAll('.comment-container').length) + ')';
            }
        });
    });
});
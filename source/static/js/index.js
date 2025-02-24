document.addEventListener("DOMContentLoaded", function () {
    console.log("SocialApp Loaded");

    // Get the author_id from localStorage
    const authorId = localStorage.getItem('author_id');
    console.log("Author ID retrieved from localStorage:", authorId);

    if (!authorId) {
        alert("Author ID not found! Please log in.");
        return;
    }

    // Get CSRF token
    const csrfToken = getCSRFToken(); // Call the function to get the CSRF token
    console.log("CSRF Token:", csrfToken);

    // Event listener for creating a post
    document.querySelector('.post-btn').addEventListener('click', async () => {
        const title = document.getElementById('postTitle').value; // Get the post title from the input field
        const content = document.getElementById('postContent').value; // Get the post content
        const visibility = document.getElementById('visibility').value || "PUBLIC";  // Default visibility to "PUBLIC"

        if (!title || !content) {
            alert("Title and content are required!");
            return;
        }

        const postData = {
            title: title,
            content: content,  // Ensure the content is included
            visibility: visibility
        };

        try {
            const response = await fetch(`/api/authors/${authorId}/posts/`, { // Use the dynamic authorId here
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`, // Use the access token
                    'X-CSRFToken': csrfToken // Ensure the CSRF token is included
                },
                body: JSON.stringify(postData)
            });

            const data = await response.json();

            if (response.ok) {
                alert('Post created successfully!');

                // Get the new post data from the response and append it to the feed
                const newPost = data.post;

                const postFeed = document.querySelector('.posts-feed');
                const postCard = document.createElement('div');
                postCard.classList.add('post-card');
                postCard.innerHTML = `
                    <div class="post-header">
                        <img src="${newPost.author.profile_picture_url}" alt="Author Picture" class="small-profile-pic">
                        <div>
                            <h3>${newPost.author.display_name}</h3>
                            <p class="post-time">${new Date(newPost.published).toLocaleString()}</p>
                        </div>
                    </div>
                    <p>${newPost.content}</p>
                    <div class="post-footer">
                        <button class="btn">❤️ Like</button>
                        <button class="btn">💬 Comment</button>
                        <button class="btn">🔄 Share</button>
                    </div>
                `;

                // Prepend the new post to the top of the feed
                postFeed.appendChild(postCard);  // This will add the new post to the bottom of the feed


                // Optionally, clear the input fields after posting
                document.getElementById('postTitle').value = '';
                document.getElementById('postContent').value = ''; // Clear content field
            } else {
                alert('Error creating post: ' + data.message);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error creating post');
        }
    });
});

// Get CSRF token from the cookie
function getCSRFToken() {
    const cookieValue = document.cookie
        .split("; ")
        .find(row => row.startsWith("csrftoken="))
        ?.split("=")[1];

    return cookieValue || null;
}

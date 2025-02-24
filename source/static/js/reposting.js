function repost(post) {
    const credentials = Cookies.get('credentials');
    const username = atob(credentials).split(':')[0];
    const postOwneUsername = post.author.id;

    const url = `/api/authors/${username}/posts/`
    const repostTitle = "REPOST: " + post.title;
    const repostDescription = "REPOST: " + post.description;
    const contentType = "text/markdown";
    const content = "Repost from " 
                    + postOwneUsername.split('/').pop() 
                    + ":\n" + "[Link to original post](" 
                    + `/posts/${encodeURIComponent(post.id)}`
                    + ")"
    const visibility = "UNLISTED";

    const requestData = {
        "title": repostTitle,
        "description": repostDescription,
        "contentType": contentType,
        "content": content,
        "visibility": visibility
    }

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + credentials,
            'X-Original-Host': window.location.protocol + "//" + window.location.host + "/api/"
        },
        body: JSON.stringify(requestData)
    })
    .then(response => {
        if (response.ok)
            return response.json();
    })
    .then(data => {
        const newPostId = data.id;
        const newPostUrl = `/posts/${encodeURIComponent(newPostId)}`;
        window.location.href = newPostUrl;
    })
    .catch(error => {
        console.error('Error:', error);
    });

}

window.repost = repost;

document.addEventListener("DOMContentLoaded", function () { 
    credsAuth();
    const credentials = Cookies.get('credentials');
    const username = atob(credentials).split(':')[0];
    handleInbox(username, credentials);
    setInterval(() => handleInbox(username, credentials), 5000);
    
    const websiteTitle = document.getElementById('website-title');
    const loadMoreButton = document.getElementById('load-more-button');
    const loadMoreMessage = document.getElementById('load-more-message');


    const spinner = createSpinnerElement();
    const postsContainer = document.getElementById('posts-container');

    const currentUrl = window.location.href;
    const postID = decodeURIComponent(currentUrl).split('posts')[1].substring(1)
    + 'posts' + decodeURIComponent(currentUrl).split('posts')[2];
    let page = 1;
    let commentCounts = 0;
    const commentsPerPage = 5;
    let url = `/api/posts/${postID}?page=${page}&size=${commentsPerPage}`;

    fetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + credentials,
            'X-Original-Host': window.location.protocol + "//" + window.location.host + "/api/"
        },
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            spinner.style.display = 'none';
            const errorMessage = document.createElement('p');
            errorMessage.style.textAlign = 'center';
            errorMessage.style.marginTop = '24%';
            errorMessage.style.marginLeft = '10%';
            errorMessage.style.fontSize = '40px';
            errorMessage.style.fontWeight = 'bolder';
            errorMessage.textContent = 'Whoops! Seems like nothing is here!';
            postsContainer.appendChild(errorMessage);
        }
    })
    .then(data => {
        createPostElement(data);
        hideAllSpinnerElements();
        if (data.comments.src.length > 0) {
            for (let i = 0; i < data.comments.src.length; i++) {
                createPostCommentsElement(data.comments.src[i]);
                commentCounts += 1;
            }
            if (data.comments.src.length < commentsPerPage) {
                loadMoreButton.style.display = 'none';
                loadMoreMessage.style.display = 'block';
            } else {
                loadMoreButton.style.display = 'block';
                loadMoreMessage.style.display = 'none';
            }
        } else {
            loadMoreButton.style.display = 'none';
            loadMoreMessage.style.display = 'block';
        }
    })
    .catch(error => console.error('Error:', error));

    loadMoreButton.addEventListener('click', function () {
        page += 1;
        url = `/api/posts/${postID}?page=${page}&size=${commentsPerPage}`;

        fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Basic ' + credentials,
                'X-Original-Host': window.location.protocol + "//" + window.location.host + "/api/"
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.comments.src.length > 0) {
                for (let i = 0; i < data.comments.src.length; i++) {
                    createPostCommentsElement(data.comments.src[i]);
                    commentCounts += 1;
                }
                if (data.comments.src.length < commentsPerPage) {
                    loadMoreButton.style.display = 'none';
                    loadMoreMessage.style.display = 'block';
                } else {
                    loadMoreButton.style.display = 'block';
                    loadMoreMessage.style.display = 'none';
                }
            } else {
                loadMoreButton.style.display = 'none';
                loadMoreMessage.style.display = 'block';
            }
        })
        .catch(error => console.error('Error:', error));
    });


    document.getElementById('refresh-button').addEventListener('click', function(){
        location.reload();
    });
    
    document.getElementById("backtotop-button").addEventListener("click", function() {
        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });
    });

    document.getElementById('profile').addEventListener('click', function(){
        window.location.href = `/authors/${encodeURIComponent(Cookies.get('id'))}`;
    });
    document.getElementById('following').addEventListener('click', function(){
        window.location.href = `/authors/${encodeURIComponent(Cookies.get('id'))}/following`;
    });
});

function createPostElement(post) {
    const credentials = Cookies.get('credentials');
    const username = atob(credentials).split(':')[0];
    const staticUrls = document.getElementById('static-urls');
    const postsContainer = document.getElementById('posts-container');

    const postDiv = document.createElement('div');
    postDiv.classList.add('post-container');

    const userInfoDiv = document.createElement('div');
    userInfoDiv.classList.add('user-info');

    const userImg = document.createElement('img');
    userImg.src = post.author.profileImage || staticUrls.dataset.defaultUserImg;
    userImg.onerror = function () {
        userImg.src = staticUrls.dataset.userProfileImg;
    };
    userImg.width = 50;
    userImg.height = 50;
    userImg.style.borderRadius = '50%';
    userImg.style.cursor = 'pointer';
    userImg.style.transition = 'transform 0.3s ease, box-shadow 0.3s ease';
    userImg.addEventListener('mouseenter', () => {
        userImg.style.transform = 'scale(1.1)';
        userImg.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.2)';
    });
    userImg.addEventListener('mouseleave', () => {
        userImg.style.transform = 'scale(1)';
        userImg.style.boxShadow = 'none';
    });
    userImg.addEventListener('click', function(){
        window.location.href = `/authors/${encodeURIComponent(post.author.id)}`;
    });

    const userName = document.createElement('p');
    userName.textContent = post.author.displayName || "Unknown User";

    userInfoDiv.appendChild(userImg);
    userInfoDiv.appendChild(userName);

    const postContentDiv = document.createElement('div');
    postContentDiv.classList.add('post-content');
    
    const postTitle = document.createElement('h3');
    postTitle.textContent = "Title: " + post.title || "No title available";

    const postDescription = document.createElement('p');
    postDescription.textContent = "Description: " + post.description || "No description available";

    postContentDiv.appendChild(postTitle);
    postContentDiv.appendChild(postDescription);

    const postContent = document.createElement('p');
    postContent.style.whiteSpace = 'pre-wrap';
    postContent.style.overflowWrap = 'break-word';

    const postImg = document.createElement('img');
    postImg.id = "post-img";
    postImg.style.width = "50%";
    postImg.style.height = "50%";
    postImg.classList.add('thumbnail');
    postImg.loading = "lazy";
    
    if (post.contentType === "text/markdown") {
        postContent.innerHTML = renderMarkdown(post.content);
        postContentDiv.appendChild(postContent);
        postContent.classList.add('markdown-content');
    } else if (post.contentType === "image/png;base64" || post.contentType === "image/jpeg;base64" || post.contentType === "application/base64") {
        postImg.src = post.content;
        postContentDiv.appendChild(postImg);
        postImg.addEventListener('click', () => {
            openImageModal(post.content);
        });
    } else {
        postContent.textContent = post.content;
        postContentDiv.appendChild(postContent);
        handleEmbeds(post, postContent);
    }

    window.addEventListener('click', function(event) { 
        const imageModal = this.document.getElementById('image-modal');
        if(event.target === imageModal)
            imageModal.style.display = "none";
    });

    const actionsDiv = document.createElement('div');
    actionsDiv.classList.add('actions');
    const likesDiv = document.createElement('div');

    const likeImg = document.createElement('img');
    likeImg.src =  staticUrls.dataset.likeImg;
    likeImg.classList.add('like-pointer');
    likeImg.width = 30;
    likeImg.height = 30;
    likeImg.style.cursor = 'pointer';
    let liked = false;
    likeImg.addEventListener('mouseover', () => {
        likeImg.src = staticUrls.dataset.likedImg;
    });
    for (const like of post.likes.src) {
        if (like.author.id.split('/').pop() === username) {
            likeImg.src = staticUrls.dataset.likedImg;
            likeImg.classList.remove('like-pointer');
            liked = true;
            break;
        }
    }
    if (liked === false) {
        likeImg.addEventListener('mouseout', () => {
            likeImg.src = staticUrls.dataset.likeImg;
        });
    }
    const likeCount = document.createElement('a');
    likeCount.id = "like-counts";
    likeCount.textContent = `${post.likes.count || 0}`;
    likeCount.style.marginTop = '10px';

    const commentButton = document.createElement('img');
    commentButton.id = "comment-button";
    commentButton.src = staticUrls.dataset.commentImg;
    commentButton.width = 30;
    commentButton.height = 30;
    commentButton.classList.add('comment-pointer');
    commentButton.addEventListener('mouseover', () => {
        commentButton.src = staticUrls.dataset.commentedImg;
    });
    commentButton.addEventListener('mouseout', () => {
        commentButton.src = staticUrls.dataset.commentImg;
    });
    commentButton.addEventListener('click', function() {
        popUpCommentWindow(post);
    });

    const repostImg = document.createElement('img');
    repostImg.src = staticUrls.dataset.repostImg;
    repostImg.width = 30;
    repostImg.height = 30;
    repostImg.addEventListener('mouseover', () => {
        repostImg.src = staticUrls.dataset.repostedImg;
    });
    repostImg.addEventListener('mouseout', () => {
        repostImg.src = staticUrls.dataset.repostImg;
    });
    if (post.visibility === "UNLISTED" || post.visibility === "FRIENDS") {
        repostImg.classList.add('disabled');
        repostImg.classList.remove('repost-pointer');
    } else if (post.visibility === "PUBLIC") {
        repostImg.classList.add('repost-pointer');
        repostImg.addEventListener('click', function() {
            repost(post);
        });
    }

    const postLikedAuthorsImgContainer = document.createElement('div');
    postLikedAuthorsImgContainer.id = 'liked-authors';
    const maxLikes = Math.min(post.likes.src.length, 10);
    for (let i = 0; i < maxLikes; i++) {
        const like = post.likes.src[i];
        const likedAuthorImg = document.createElement('img');
        likedAuthorImg.src = like.author.profileImage;
        likedAuthorImg.onerror = function () {
            likedAuthorImg.src = staticUrls.dataset.userProfileImg;
        };
        likedAuthorImg.width = 25;
        likedAuthorImg.height = 25;
        likedAuthorImg.style.borderRadius = '50%';
        likedAuthorImg.style.marginLeft = '-10px';
        postLikedAuthorsImgContainer.appendChild(likedAuthorImg);
        postLikedAuthorsImgContainer.appendChild(likeCount);
        postLikedAuthorsImgContainer.style.display = 'flex';
        postLikedAuthorsImgContainer.style.flexWrap = 'wrap';
        postLikedAuthorsImgContainer.style.paddingLeft = '10px';
    }

    let dateStr = post.published;
    let dateObj = new Date(dateStr);
    let options = { year: 'numeric', month: 'long', day: 'numeric', hour: 'numeric', minute: 'numeric', timeZone: 'UTC'};
    let postDateStr = new Intl.DateTimeFormat('en-US', options).format(dateObj);

    const publishedDate = document.createElement('p');
    publishedDate.classList.add('published-date');
    publishedDate.textContent = postDateStr;

    actionsDiv.appendChild(likeImg);
    actionsDiv.appendChild(commentButton);
    actionsDiv.appendChild(repostImg);
    actionsDiv.appendChild(publishedDate);
    likesDiv.appendChild(postLikedAuthorsImgContainer);

    postContentDiv.appendChild(actionsDiv);
    postContentDiv.appendChild(likesDiv);

    postDiv.appendChild(userInfoDiv);
    postDiv.appendChild(postContentDiv);
    
    postsContainer.appendChild(postDiv);

    likeImg.addEventListener('click', function() {
        likeUrl = `/api/authors/${username}/liked/send/`;

        fetch(likeUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Basic ' + credentials,
                'X-Original-Host': window.location.protocol + "//" + window.location.host + "/api/"
            },
            body: JSON.stringify({
                'post': post.id,
            })
        })
        .then(response => {
            if (response.ok) {
                location.reload();
                return response.json();
            } else if (response.status === 409) {
                console.error(`user ${username} already liked this post`);
            }
        })
    });
}

function handleEmbeds(post, postContent) {
    const youtubeVideoId = extractYouTubeVideoId(post.content);
    if (youtubeVideoId) {
        const youtubeEmbed = createYouTubeEmbed(youtubeVideoId);
        postContent.appendChild(youtubeEmbed);
    }
    const spotifyEmbedUrl = extractSpotifyEmbedUrl(post.content);
    if (spotifyEmbedUrl) {
        const spotifyEmbed = createSpotifyEmbed(spotifyEmbedUrl);
        postContent.appendChild(spotifyEmbed);
    }
    if (!youtubeVideoId && !spotifyEmbedUrl)
        postContent.textContent = post.content;
}

function openImageModal(imageSrc) {
    const modalImage = document.getElementById('modal-image');
    modalImage.src = imageSrc;
    const imageModal = document.getElementById('image-modal');
    imageModal.style.display = 'block';
}

function renderMarkdown(content) {
    const htmlContent = marked.parse(content);
    const sanitizedContent = DOMPurify.sanitize(htmlContent);
    return sanitizedContent;
}

function createPostCommentsElement(comment) {
    const staticUrls = document.getElementById('static-urls');
    const credentials = Cookies.get('credentials');
    const username = atob(credentials).split(':')[0];
    const postsContainer = document.getElementById('posts-container');
    const commentsContainer = document.createElement('div');
    commentsContainer.classList.add('comments');

    const commentContainer = document.createElement('div');
    commentContainer.classList.add('comment');

    const userInfoContainer = document.createElement('div');
    userInfoContainer.classList.add('user-info');

    const userImg = document.createElement('img');
    userImg.src = comment.author.profileImage;
    userImg.onerror = function () {
        userImg.src = staticUrls.dataset.userProfileImg;
    };
    userImg.width = 50;
    userImg.height = 50;
    userImg.style.borderRadius = '50%';
    userInfoContainer.appendChild(userImg);

    const userName = document.createElement('p');
    userName.textContent = comment.author.displayName || "Unknown User";
    userInfoContainer.appendChild(userName);

    const commentContentContainer = document.createElement('div');
    commentContentContainer.classList.add('comment-content');

    const commentText = document.createElement('p');
    if (comment.contentType === 'text/markdown')
        commentText.innerHTML = renderMarkdown(comment.comment);
    else
        commentText.textContent = comment.comment || "No content";
    commentContentContainer.appendChild(commentText);

    const likeSection = document.createElement('p');

    const likeImg = document.createElement('img');
    likeImg.src = staticUrls.dataset.likeImg;
    likeImg.style.cursor = 'pointer';
    likeImg.width = 20;
    likeImg.height = 20;

    for (const like of comment.likes.src) {
        if (like.author.id.split('/').pop() === username) {
            likeImg.src = staticUrls.dataset.likedImg;
            likeImg.classList.remove('like-pointer');
            break;
        }
    }
    
    likeSection.appendChild(likeImg);

    const likeCount = document.createElement('a');
    likeCount.id = "like-counts";
    likeCount.textContent = ` ${comment.likes.count || 0}`;
    likeSection.appendChild(likeCount);

    commentContentContainer.appendChild(likeSection);

    commentContainer.appendChild(userInfoContainer);
    commentContainer.appendChild(commentContentContainer);

    commentsContainer.appendChild(commentContainer);

    postsContainer.appendChild(commentsContainer);

    likeImg.addEventListener('click', function() {
        const likeUrl = `/api/authors/${username}/liked/send/`;
        fetch(likeUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Basic ' + credentials,
                'X-Original-Host': window.location.protocol + "//" + window.location.host + "/api/"
            },
            body: JSON.stringify({
                'comment': comment.id,
            })
        })
        .then(response => {
            if (response.ok) {
                likeImg.src = staticUrls.dataset.likedImg;
                likeCount.textContent = ` ${comment.likes.count + 1}`;
                return response.json();
            } else if (response.status === 409) {
                console.error(`User ${username} already liked this post`);
            }
        });
    });
}


function credsAuth() {
    const staticUrls = document.getElementById('static-urls');
    const credentials = Cookies.get('credentials');
    
    if (credentials === null || credentials === undefined) {
        console.log(credentials)
        Cookies.remove('credentials');
        window.location.href = '/login';
        return;
    }
    
    const username = atob(credentials).split(':')[0];
    const url = `/api/authors/${username}`;

    fetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + credentials,
            'X-Original-Host': window.location.protocol + "//" + window.location.host + "/api/"
        },
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            //window.location.href = `/login`;
        }
    })
    .catch(error => {
        console.error('Error during authentication:', error);
        Cookies.remove('credentials');
        //window.location.href = '/login';
    });
}

function popUpCommentWindow(post) {
    const content = document.getElementById('content');
    const contentType = document.getElementById("content-type");
    const modal = document.getElementById('commentPostModal');
    const submit = document.getElementById('submit');

    modal.style.display = 'flex';

    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    });
    
    const credentials = Cookies.get('credentials');
    const username = atob(credentials).split(':')[0];

    document.addEventListener("keydown", function(event) {
        if (event.key === "Enter") {
            submit.click();
        }
    });
    
    submit.addEventListener('click', function(event) {
        event.preventDefault();
        const requestData = {
            "post": post.id,
            "contentType": contentType.value,
            "comment": content.value
        };
        submitComment(requestData, username);
    });
}

function submitComment(requestData, username) {
    const url = `/api/authors/${username}/commented`;
    const credentials = Cookies.get('credentials');

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
        if (response.ok) {
            location.reload();
            return response.json();
        }
    })
}

function createSpinnerElement() {
    const postsContainer = document.getElementById('posts-container');
    const spinnerContainer = document.createElement('div');
    spinnerContainer.classList.add('loading-container');
    const spinner = document.createElement('div');
    spinner.classList.add('spinner');
    spinnerContainer.appendChild(spinner);
    postsContainer.appendChild(spinnerContainer);
    return spinnerContainer;
}

function hideAllSpinnerElements() {
    const loadingContainers = document.querySelectorAll(".loading-container");
    loadingContainers.forEach(container => {
        container.style.display = "none";
    });
}

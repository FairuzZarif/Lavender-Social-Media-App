let mode = "owner";
let postDataLength = 0;

document.addEventListener("DOMContentLoaded", async function () {
    await credsAuth();
    const credentials = Cookies.get('credentials');
    const username = atob(credentials).split(':')[0];
    handleInbox(username, credentials);
    setInterval(() => handleInbox(username, credentials), 5000);
    
    const userID = Cookies.get('id');
    const urlID = decodeURIComponent(window.location.pathname.replace('/authors/', ''));
    const postOwnerData = await getPostOwnerDataByUsername(urlID, userID, credentials);
    mode = (userID === urlID) ? "owner" : "visitor";

    try {
        await Promise.all([renderNameAvatar(postOwnerData), renderFollowers(), renderFollowing(), renderPosts()]);
    } catch (error) {
        console.error('error getting stuff from server:', error);
    }
    
    const noPostsReminder = document.getElementById('no-posts-reminder');
    noPostsReminder.textContent = 'There is nothing to show right now.';
    adjustProfilePage(mode, username, credentials, postOwnerData, userID, urlID);

    document.getElementById('profile').addEventListener('click', function(){
        window.location.href = `/authors/${encodeURIComponent(Cookies.get('id'))}`;
    });

    document.getElementById('following').addEventListener('click', function(){
        window.location.href = `/authors/${encodeURIComponent(Cookies.get('id'))}/following`;
    });
});

async function adjustProfilePage(mode, username, credentials, postOwnerData, userID, urlID) {
    const editButton = document.getElementById("edit-profile");
    const interactionContainers = document.getElementsByClassName("interaction-container");
    const postHeaderContent = document.getElementById("post-header-content");

    if (mode === "owner") {
        editButton.addEventListener("click", function() {
            window.location.href = `/authors/my/edit`;
        });

    }
    else if (mode === "visitor") {
        let isRemote = false;
        if (userID.split('/')[2] !== urlID.split('/')[2]) {
            document.getElementById('follows-container').style.display = "none";
            document.getElementById('posts-container').style.display = "none";
            isRemote = true;
        }

        editButton.textContent = "Follow";

        const postOwnerUsername = postOwnerData.id.split('/').pop();
        const postOwnerFollowers = await getPostOwnerFollowersByUsername(isRemote, username, postOwnerUsername, urlID, credentials);

        if (postOwnerFollowers.isFollowing) {
            editButton.textContent = "Unfollow";
        }
        else if (!postOwnerFollowers.isFollowing && postOwnerFollowers.postOwnerFollowers === null) {
            editButton.textContent = "Follow";
        }
        else if (!postOwnerFollowers.isFollowing && postOwnerFollowers.postOwnerFollowers !== undefined) {
            postOwnerFollowers.postOwnerFollowers.followers.forEach(follower => {
                if (follower.id === Cookies.get('id'))
                    editButton.textContent = "Unfollow";
            });
        }

        for (let interactionContainer of interactionContainers) {
            interactionContainer.style.display = "none";
        }
        postHeaderContent.textContent = `${postOwnerData.displayName}'s Posts`;

        if (editButton.textContent === "Follow") {
            editButton.addEventListener("click", async function() {
                const followUrl = `/api/authors/${username}/frae/${postOwnerData.id}`;
                try {
                    const response = await fetch(followUrl, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': 'Basic ' + credentials,
                            'X-Original-Host': window.location.protocol + "//" + window.location.host + "/api/"
                        },
                    });
                    
                    if (response.ok)
                        location.reload();
                    else if (response.status === 400)
                        throw new Error('Already followed user');
                } catch (error) {
                    console.error('Error following user:', error);
                }
            });
        }
        else if (editButton.textContent === "Unfollow") {
            editButton.addEventListener("click", async function() {
                const unfollowUrl = `/api/authors/${username}/frae/${postOwnerData.id}`;
                try {
                    const response = await fetch(unfollowUrl, {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': 'Basic ' + credentials,
                            'X-Original-Host': window.location.protocol + "//" + window.location.host + "/api/"
                        },
                    });
                    
                    if (response.ok)
                        location.reload();
                    else
                        throw new Error('Error unfollowing user');
                } catch (error) {
                    console.error('Error unfollowing user:', error);
                }
            });
        }
    }
}

async function getPostOwnerFollowersByUsername(isRemote, username, postOwnerUsername, urlID, credentials) {
    let url = null;
    if(isRemote)
        url = `/api/authors/${username}/fre/${urlID}`;
    else
        url = `/api/authors/${postOwnerUsername}/followers`;
    
    let postOwnerFollowers = null;
    let isFollowing = false;
    await fetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + credentials,
            'X-Original-Host': window.location.protocol + "//" + window.location.host + "/api/"
        },
    })
    .then(response => {
        if(isRemote && response.ok)
            isFollowing = true;
        else if(isRemote && response.status === 404)
            isFollowing = false;
        else if(!isRemote && response.ok)
            return response.json();
    })
    .then(data => {
        postOwnerFollowers = data;
    });
    return {postOwnerFollowers, isFollowing};
}

async function getPostOwnerDataByUsername(urlID, userID, credentials) {
    let postOwnerData = null;
    const url = `/api/authors/${urlID}`;
    await fetch(url, {
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
        } else if (response.status === 404) {
            alert(`No such user: ${urlID}`);
            window.location.href = '/authors/' + userID;
        }
    })
    .then(data => {
        postOwnerData = data;
    });
    return postOwnerData;
}

async function renderFollowers() {
    const credentials = Cookies.get('credentials');
    const urlUsername = decodeURIComponent(window.location.href.split('/').pop()).split('/').pop();
    const urlID = decodeURIComponent(window.location.pathname.replace('/authors/', ''));
    const followerCountText = document.getElementById('follower-count');
    const followerUrl = `/api/authors/${urlUsername}/followers`;

    try {
        const response = await fetch(followerUrl, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Basic ' + credentials,
                'X-Original-Host': window.location.protocol + "//" + window.location.host + "/api/"
            },
        });
    
        const text = await response.text(); // Get the response as text first
        
        // Check if the response starts with <!DOCTYPE or <html> indicating HTML response
        if (text.startsWith("<!DOCTYPE") || text.startsWith("<html")) {
            console.warn("Ignoring HTML response for:", followerUrl);
        } else {
            // Parse JSON if it's not HTML
            const data = JSON.parse(text);
            followerCountText.textContent = `${data.followers.length} Followers`;
        }
    
    } catch (error) {
        // Only log errors that are not related to HTML responses
        if (!(error instanceof SyntaxError && error.message.includes("JSON"))) {
            console.error('Error fetching followers:', error);
        }
    }
    
    followerCountText.onclick = function() {
        window.location.href = `/authors/${encodeURIComponent(urlID)}/followers`;
    }    
}


async function renderFollowing() {
    const credentials = Cookies.get('credentials');
    const urlUsername = decodeURIComponent(window.location.href.split('/').pop()).split('/').pop();
    const urlID = decodeURIComponent(window.location.pathname.replace('/authors/', ''));
    const followingCountText = document.getElementById('following-count');
    const followingUrl = `/api/authors/${urlUsername}/following`;

    try {
        const response = await fetch(followingUrl, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Basic ' + credentials,
                'X-Original-Host': window.location.protocol + "//" + window.location.host + "/api/"
            },
        });
    
        // Check if response is not JSON (HTML response will have "<!DOCTYPE")
        const text = await response.text();
        if (text.startsWith("<!DOCTYPE") || text.startsWith("<html")) {
            console.warn("Ignoring HTML response for:", followingUrl);
        } else {
            // Convert to JSON safely only if it's a valid JSON response
            const data = JSON.parse(text);
            followingCountText.textContent = `${data.following.length} Following`;
        }
    
    } catch (error) {
        // Only log errors that are not caused by HTML responses
        if (!(error instanceof SyntaxError && error.message.includes("JSON"))) {
            console.error('Error fetching following:', error);
        }
    }
    
    followingCountText.onclick = function() {
        window.location.href = `/authors/${encodeURIComponent(urlID)}/following`;
    };
    
}


async function renderNameAvatar(postOwnerData) {
    const staticUrls = document.getElementById('static-urls');
    const usernameView = document.getElementById("username");
    usernameView.textContent = postOwnerData.displayName || "Unknown User";
    const profileAvatar = document.getElementById("profile-avatar");
    profileAvatar.src = postOwnerData.profileImage;
    profileAvatar.onerror = function () {
        profileAvatar.src = staticUrls.dataset.userProfileImg;
    };
}

function renderMarkdown(content) {
    const htmlContent = marked.parse(content);
    const sanitizedContent = DOMPurify.sanitize(htmlContent);
    return sanitizedContent;
}

function toggleInput() {
    const contentType = document.getElementById("content-type").value;
    const textarea = document.getElementById("content");
    const imageUpload = document.getElementById("image");

    if (contentType === "image/png;base64" || contentType === "image/jpeg;base64" || contentType === "application/base64") {
        textarea.style.display = "none";
        imageUpload.style.display = "block";
    } else {
        textarea.style.display = "block";
        imageUpload.style.display = "none";
    }
}

async function createPostElement(post, dataLength) {
    const staticUrls = document.getElementById('static-urls');

    const noPostsReminder = document.getElementById('no-posts-reminder');
    if (dataLength !== 0)
        noPostsReminder.style.display = 'none';

    const hostname = window.location.hostname;
    const credentials = Cookies.get('credentials');
    const username = atob(credentials).split(':')[0];
    const postsContainer = document.getElementById("posts-container");
    const postDiv = document.createElement('div');
    const postModelID = post.id.split('/').pop();
    postDiv.className = 'post-container';
    postDiv.classList.add('post');

    const title = document.createElement('h2');
    title.classList.add("post-title");
    title.textContent = "Title: " + post.title;
    title.style.color = "black";

    const description = document.createElement('h4');
    description.classList.add("post-description");
    description.textContent = "Description: " + post.description;

    const likesCommentsContainer = document.createElement('div');
    likesCommentsContainer.classList.add('interaction-container');
    likesCommentsContainer.id = 'interaction-container';

    const deleteButton = document.createElement('img');
    deleteButton.classList.add('interaction');
    deleteButton.src = staticUrls.dataset.deleteImg;
    deleteButton.width = 30;
    deleteButton.height = 30;
    deleteButton.id = 'delete-button';

    setHoverEffect(deleteButton, staticUrls.dataset.deleteImg, staticUrls.dataset.deletedImg);

    const editPostButton = document.createElement('img');
    editPostButton.classList.add('interaction');
    editPostButton.src = staticUrls.dataset.editImg;
    editPostButton.width = 30;
    editPostButton.height = 30;
    editPostButton.id = 'edit-button';

    setHoverEffect(editPostButton, staticUrls.dataset.editImg, staticUrls.dataset.editedImg);

    likesCommentsContainer.appendChild(deleteButton);
    likesCommentsContainer.appendChild(editPostButton);

    postDiv.appendChild(title);
    postDiv.appendChild(description);
    postDiv.appendChild(likesCommentsContainer);

    title.addEventListener("click", function (event) {
        event.preventDefault();
        window.location.href = `/posts/${encodeURIComponent(post.id)}`;
    });

    
    deleteButton.addEventListener('click', function() {
        const deleteUrl = `/api/authors/${username}/posts/${postModelID}`;

        fetch(deleteUrl, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Basic ' + credentials,
                'X-Original-Host': window.location.protocol + "//" + window.location.host + "/api/"
            },
        })
        .then(response => {
            if (response.ok) {
                postDiv.remove();
                postDataLength -= 1;
                if (postDataLength <= 0) {
                    noPostsReminder.style.display = 'block';
                    noPostsReminder.textContent = 'There is nothing to show right now.';
                }
            } else {
                throw new Error('Error deleting post');
            }
        });
    });

    editPostButton.addEventListener('click', async function() {
        const postDetialData = await getPostDetailData(post.id, credentials);

        document.getElementById('title').value = postDetialData.title;
        document.getElementById('description').value = postDetialData.description;
        document.getElementById('content-type').value = postDetialData.contentType;
        document.getElementById('visibility').value = postDetialData.visibility;
    
        if (postDetialData.contentType === 'text/markdown' || postDetialData.contentType === 'text/plain') {
            document.getElementById('image').style.display = 'none';
            document.getElementById('image-title').style.display = 'none';
            document.getElementById('content-title').style.display = 'block';
            document.getElementById('content').style.display = 'block';
            document.getElementById('content').value = postDetialData.content;
        } else {
            document.getElementById('content').style.display = 'none';
            document.getElementById('content-title').style.display = 'none';
            document.getElementById('image-title').style.display = 'block';
            document.getElementById('image').style.display = 'block';
            document.getElementById('image').src = postDetialData.content;
        }
    
        const modal = document.getElementById("editPostModal");
        modal.classList.add("show");
    
        const span = document.getElementsByClassName("close")[0];

        span.onclick = function() {
            modal.classList.remove("show");
        };
    
        window.onclick = function(event) {
            if (event.target === modal)
                modal.classList.remove("show");
        };

        document.getElementById("content-type").addEventListener("change", function() {
            toggleInput();
        });
        
        const imageUpload = document.getElementById('image-upload');
        document.getElementById('image').addEventListener('click', function() {
            imageUpload.click();
        });

        let content64 = null;
        let fileType = null;

        const match = postDetialData.content.match(/^data:(image\/\w+);base64,/);
        if (match)
            fileType = match[1];
        if (postDetialData.contentType === "image/png;base64"
            || postDetialData.contentType === "image/jpeg;base64"
            || postDetialData.contentType === "application/base64")
            content64 = post.content;

        imageUpload.addEventListener('change', function() {
            const file = imageUpload.files[0];
            fileType = file.type;
            const reader = new FileReader();
            reader.onload = function(event) {
                content64 = event.target.result;
                document.getElementById('image').src = content64;
            }
            reader.readAsDataURL(file);
        });

        document.getElementById("edit-post-form").addEventListener("submit", function(event) {
            event.preventDefault();
            const contentType = document.getElementById("content-type").value;
            const visibility = document.getElementById("visibility").value;
            const title = document.getElementById('title').value;
            const description = document.getElementById('description').value;
            const editUrl = `/api/authors/${username}/posts/${postModelID}`;
            const content = document.getElementById('content').value;

            if (contentType === "text/markdown" || contentType === "text/plain") {
                update(modal, credentials, editUrl, title, description, content, contentType, visibility);
            }
            else {
                if (contentType === "image/png;base64") {
                    if (fileType === "image/png")
                        update(modal, credentials, editUrl, title, description, content64, contentType, visibility);
                    else
                        alert("Please upload a PNG image");
                }
                else if (contentType === "image/jpeg;base64") {
                    if (fileType === "image/jpeg")
                        update(modal, credentials, editUrl, title, description, content64, contentType, visibility);
                    else
                        alert("Please upload a JPEG image");
                }
                else if (contentType === "application/base64") {
                    if (fileType.startsWith("image/") && fileType !== "image/png" && fileType !== "image/jpeg")
                        update(modal, credentials, editUrl, title, description, content64, contentType, visibility);
                    else
                        alert("Please upload a valid image");
                }
            }
        });
    });
    
    const shareButton = document.createElement('img');
    shareButton.classList.add('interaction');
    shareButton.src = staticUrls.dataset.shareImg;
    shareButton.width = 30;
    shareButton.height = 30;
    shareButton.id = 'share-button';

    setHoverEffect(shareButton, staticUrls.dataset.shareImg, staticUrls.dataset.sharedImg);

    if (post.visibility === "FRIENDS")
        shareButton.style.display = "none";

    shareButton.addEventListener('click', function() {
        shareUrl = `${hostname}/posts/${encodeURIComponent(post.id)}`;
        navigator.clipboard.writeText(shareUrl);
        alert(`${shareUrl}\nPost URL copied to clipboard`);
    });

    likesCommentsContainer.appendChild(shareButton);

    postsContainer.appendChild(postDiv);
}

function update(modal, credentials, editUrl, title, description, content, contentType, visibility) {
    fetch(editUrl, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + credentials,
            'X-Original-Host': window.location.protocol + "//" + window.location.host + "/api/"
        },
        body: JSON.stringify({
            "title": title,
            "description": description,
            "contentType": contentType,
            "content": content,
            "visibility": visibility
        })
    })
    .then(response =>{
        if(response.ok) {
            return response.json();
        } else if (response.status === 400) {
            alert('Error updating post');
        }
    })
    .then(data => {
        modal.classList.remove("show");
        location.reload();
    })
    .catch(error => console.error('Error:', error));
}

async function renderPosts() {
    const credentials = Cookies.get('credentials');
    const urlUsername = decodeURIComponent(window.location.href.split('/').pop()).split('/').pop();
    const postsUrl = `/api/authors/${urlUsername}/posts/`;

    try {
        const response = await fetch(postsUrl, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Basic ' + credentials,
                'X-Original-Host': window.location.protocol + "//" + window.location.host + "/api/"
            },
        });
        const data = await response.json();
        data.forEach(post => {
            postDataLength += 1;
            createPostElement(post, postDataLength);
        });
    } catch (error) {
        console.error('Error fetching posts:', error);
    }
}

function setHoverEffect(element, defaultSrc, hoverSrc) {
    element.addEventListener('mouseover', () => {
        element.src = hoverSrc;
    });
    element.addEventListener('mouseout', () => {
        element.src = defaultSrc;
    });
}

async function getPostDetailData(postID, credentials) {
    const url = `/api/posts/${postID}`;
    try {
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Basic ' + credentials,
                'X-Original-Host': window.location.protocol + "//" + window.location.host + "/api/"
            },
        });
        if (!response.ok)
            throw new Error('Error fetching post details');
        const postDetailData = await response.json();
        return postDetailData;
    } catch (error) {
        console.error('Error in getPostDetailData:', error);
        return null;
    }
}

function credsAuth() {
    const credentials = Cookies.get('credentials');
    const username = credentials ? atob(credentials).split(':')[0] : null;

    if (credentials === null || credentials === undefined) {
        window.location.href = '/login';
        return;
    }

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
        if (response.ok)
            return response.json();
        else
            window.location.href = '/login';
    })
    .catch(error => {
        console.error('Error during authentication:', error);
        Cookies.remove('credentials');
        window.location.href = '/login';
    });
}

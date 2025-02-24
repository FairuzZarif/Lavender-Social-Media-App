let streamLength = 0;
let postsPerPage = 5;
let isFetching = false;
let currentPage = 1;

document.addEventListener("DOMContentLoaded", function () {
    main();
});

/**
 * @function toggleInput
 * @description Toggles the input field between text and image upload,
 * hides the textarea and shows the image upload field when the content type is an image.
 */
function toggleInput() {
    const contentType = document.getElementById("content-type").value;
    const textarea = document.getElementById('edit-post-textarea');
    const imageUpload = document.getElementById('image-upload');

    if (contentType === "image/png;base64" || contentType === "image/jpeg;base64" || contentType === "application/base64") {
        textarea.style.display = "none";
        imageUpload.style.display = "block";
    } else {
        textarea.style.display = "block";
        imageUpload.style.display = "none";
    }
}

/**
 * @function main
 * @description Main function that handles the logic for the main page.
 * @param {*} postButton - The button that toggles hide and show new post container.
 * @param {*} stream - The stream of posts that are displayed on the main page.
 */
async function main() {
    credsAuth();

    const credentials = Cookies.get('credentials');
    const username = atob(credentials).split(':')[0];
    const userID = window.location.protocol + "//" + window.location.host + "/api/authors/" + username;
    const id = Cookies.get('id');
    const url = `/api/authors/${username}/posts/`; 

    const editPostContainer = document.getElementById('edit-post-textarea-container');
    const postButton = document.getElementById("post-button");

    const streamLengthUrl = `/api/stream/${id}/length`;
    await fetch(streamLengthUrl, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + credentials,
            'X-Original-Host': window.location.protocol + "//" + window.location.host + "/api/"
        },
    })
    .then(response => response.json())
    .then(data => {
        streamLength = data.stream_length;
        if (streamLength < postsPerPage)
            postsPerPage = streamLength;
        createSpinnerElementsOnStream(0,postsPerPage);
    });

    document.getElementById("content-type").value = "text/plain";
    document.getElementById("visibility-options").value = "PUBLIC";

    document.getElementById("content-type").addEventListener("change", function() {
        toggleInput();
    });


    editPostContainer.style.display = 'none';

    document.addEventListener("keydown", function(event) {
        if (event.key === "Enter")
            postButton.click();
    });

    postButton.addEventListener("click", function () {
        
        const errorMessages = document.getElementById('post-error-messages');
        if (errorMessages !== null)
            errorMessages.remove();

        postButton.disabled = true;
        postButton.style.display = 'none';
        const postButtonSpinner = document.createElement('div');
        postButtonSpinner.classList.add('spinner');
        postButtonSpinner.id = 'post-button-spinner';
        postButtonSpinner.style.margin = 'auto';
        editPostContainer.appendChild(postButtonSpinner);

        const title = document.getElementById("title").value;
        const description = document.getElementById("description").value;
        const content = document.getElementById("edit-post-textarea").value;
        const visibility = document.getElementById("visibility-options").value;
        const contentType = document.getElementById("content-type").value;

        function disableLoadingWithError() {
            const postButtonSpinner = document.getElementById('post-button-spinner');
            postButtonSpinner.remove();
            const errorMessages = document.createElement('p');
            errorMessages.textContent = "Illegal post content detected. Please try again.";
            errorMessages.id = "post-error-messages";
            editPostContainer.appendChild(errorMessages);
            const postButton = document.getElementById("post-button");
            postButton.disabled = false;
            postButton.style.display = 'block';
        }

        if (contentType === "text/markdown" || contentType === "text/plain") {
            upload(credentials, url, title, description, content, visibility, contentType);
        }
        else {
            const image = document.getElementById("image-upload").files[0];
            if (image === undefined) {
                disableLoadingWithError();
                return;
            }
            let fileType = image.type;
            const reader = new FileReader();
            reader.onload = function(event) {
                const imageBase64 = event.target.result;
                if (contentType === "image/png;base64") {
                    if (fileType === "image/png")
                        upload(credentials, url, title, description, imageBase64, visibility, contentType);
                    else
                        disableLoadingWithError();
                }
                else if (contentType === "image/jpeg;base64") {
                    if (fileType === "image/jpeg")
                        upload(credentials, url, title, description, imageBase64, visibility, contentType);
                    else
                        disableLoadingWithError();
                }
                else if (contentType === "application/base64") {
                    if (fileType.startsWith("image/") && fileType !== "image/png" && fileType !== "image/jpeg")
                        upload(credentials, url, title, description, imageBase64, visibility, contentType);
                    else
                        disableLoadingWithError();
                }
            }
            reader.readAsDataURL(image);
        }

    });

    handleSearch();

    document.getElementById('refresh-button').addEventListener('click', function() {
        location.reload();
    });

    document.getElementById("backtotop-button").addEventListener("click", function() {
        window.scrollTo({top: 0, behavior: "smooth"});
    });

    document.getElementById('edit-button').addEventListener('click', function() {
        const errorMessages = document.getElementById('post-error-messages');
        if (errorMessages !== null)
            errorMessages.remove();
        if (editPostContainer.style.display === 'none') {
            window.scrollTo({
                top: 0,
                behavior: "smooth"
            });
            editPostContainer.style.display = 'block';
        } else {
            editPostContainer.style.display = 'none';
        }
    });

    await fetchAndCreatePostsOnStream(0, postsPerPage);
    
    handleInbox(username, credentials);
    setInterval(() => handleInbox(username, credentials), 5000);

    window.addEventListener('scroll', async function () {
        const scrollTop = window.scrollY;
        const viewportHeight = window.innerHeight;
        const documentHeight = document.documentElement.scrollHeight;
    
        if (!isFetching && scrollTop + viewportHeight >= documentHeight - 200) {
            isFetching = true;
    
            const min = currentPage * postsPerPage;
            const max = Math.min(min + postsPerPage, streamLength);
    
            if (min >= streamLength) {
                isFetching = false;
                return;
            }
            createSpinnerElementsOnStream(min, max);
    
            try {
                await fetchAndCreatePostsOnStream(min, max);
            } catch (error) {
                console.error('Error fetching and creating posts:', error);
            } finally {
                isFetching = false;
                currentPage++;
            }
        }
    });
}

function upload(credentials, url, title, description, content, visibility, contentType) {
    const editPostContainer = document.getElementById('edit-post-textarea-container');
    const requestData = {
        "title": title,
        "description": description,
        "contentType": contentType,
        "content": content,
        "visibility": visibility,
    };

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + credentials,
            'X-Original-Host': window.location.protocol + "//" + window.location.host + "/api/"
        },
        body: JSON.stringify(requestData),
    })
    .then(response => {
        if (response.status === 201) {
            document.getElementById("title").value = "";
            document.getElementById("description").value = "";
            document.getElementById("edit-post-textarea").value = "";
            const postButtonSpinner = document.getElementById('post-button-spinner');
            postButtonSpinner.remove();
            const postButton = document.getElementById("post-button");
            postButton.disabled = false;
            postButton.style.display = 'block';
            editPostContainer.style.display = 'none';
            location.reload();
        } else {
            const postButtonSpinner = document.getElementById('post-button-spinner');
            postButtonSpinner.remove();
            const errorMessages = document.createElement('p');
            errorMessages.textContent = "Illegal post content detected. Please try again.";
            errorMessages.id = "post-error-messages";
            editPostContainer.appendChild(errorMessages);
            const postButton = document.getElementById("post-button");
            postButton.disabled = false;
            postButton.style.display = 'block';
        }
    });
}

async function fetchAndCreatePostsOnStream(min, max) {
    const credentials = Cookies.get('credentials');
    const id = Cookies.get('id');

    for (let i = min; i < max; i++) {
        const streamUrl = `/api/stream/${id}/posts/${i + 1}`;

        fetch(streamUrl, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Basic ' + credentials,
                'X-Original-Host': window.location.protocol + "//" + window.location.host + "/api/"
            },
        })
        .then(response => response.json())
        .then(data => {
            createPublicPostElementByIndex(data, i);
        });
    }
}

function renderMarkdown(content) {
    const htmlContent = marked.parse(content);
    const sanitizedContent = DOMPurify.sanitize(htmlContent);
    return sanitizedContent;
}

function createSpinnerElementsOnStream(min, max) {
    const postsContainer = document.getElementById('posts-container');
    for (let i = min; i < max; i++) {
        const spinnerContainer = document.createElement('div');
        spinnerContainer.classList.add('loading-container');
        spinnerContainer.id = `spinner-${i}`;
        const spinner = document.createElement('div');
        spinner.classList.add('spinner');
        spinnerContainer.appendChild(spinner);
        postsContainer.appendChild(spinnerContainer);
    }
}


function hideSpinnerElement(i) {
    const spinnerElement = document.getElementById(`spinner-${i}`);
    spinnerElement.style.display = 'none';
}

async function createPublicPostElementByIndex(post, i) {
    let isLiked = false;
    const staticUrls = document.getElementById('static-urls');
    const credentials = Cookies.get('credentials');
    const username = atob(credentials).split(':')[0];
    const spinnerElement = document.getElementById(`spinner-${i}`);
    const postContainer = document.createElement('div');
    spinnerElement.replaceWith(postContainer);
    postContainer.classList.add('post-container');

    const postSection = document.createElement('div');
    postSection.classList.add('post');

    const userInfo = document.createElement('div');
    userInfo.classList.add('user-info');

    const userImg = document.createElement('img');
    userImg.src = post.author.profileImage || staticUrls.dataset.userProfileImg;
    userImg.width = 50;
    userImg.height = 50;
    userImg.style.borderRadius = '50%';
    userImg.onerror = function () {
        userImg.src = staticUrls.dataset.userProfileImg;
    };

    const userName = document.createElement('p');
    
    const url = post.author;
    const match = url.match(/\/authors\/([^\/]+)/);
    const authorName = match ? match[1] : null;

    userName.textContent = authorName || "Unknown User";

    userInfo.appendChild(userImg);
    userInfo.appendChild(userName);

    const postContentDiv = document.createElement('div');
    postContentDiv.classList.add('post-content');
    postContentDiv.classList.add("post-img");

    const postContent = document.createElement('p');
    postContent.id = "post-content";
    postContent.style.whiteSpace = 'pre-wrap';
    postContent.style.overflowWrap = 'break-word';
    postContentDiv.appendChild(postContent);

    const postImg = document.createElement('img');
    postImg.style.width = "50%";
    postImg.style.height = "50%";
    postImg.classList.add('thumbnail');
    postImg.loading = "lazy";
    postContentDiv.appendChild(postImg);

    const wordlimit = 250;
    if (post.contentType === "text/markdown") {
        postContent.innerHTML = renderMarkdown(post.content);
        postContentDiv.classList.add('markdown-content');
    } else if (post.contentType === "image/png;base64" || post.contentType === "image/jpeg;base64" || post.contentType === "application/base64") {
        postImg.src = post.content;
    } else {
        postContent.textContent = post.content;
        const words = postContent.textContent.split(' ');
        if (words.length > wordlimit)
            postContent.textContent = words.slice(0, wordlimit).join(' ') + '...';
    }

    const title = document.createElement('h1');
    title.classList.add("post-title");
    title.textContent = "Title: " + post.title;

    const description = document.createElement('h4');
    description.classList.add("post-description");
    description.textContent = "Description: " + post.description;

    const actionButtonsContainer = document.createElement('p');
    actionButtonsContainer.classList.add('like-button-container');

    const likeImg = document.createElement('img');
    likeImg.src = staticUrls.dataset.likeImg;
    likeImg.width = 30;
    likeImg.height = 30;
    likeImg.classList.add('like-pointer');
    let liked = false;
    likeImg.addEventListener('mouseover', ()=> {
        likeImg.src = staticUrls.dataset.likedImg;
    });
    likeImg.addEventListener('mouseout', handleMouseOut);

    function handleMouseOut() {
        likeImg.src = staticUrls.dataset.likeImg;
    }

    const repostImg = document.createElement('img');
    repostImg.src = staticUrls.dataset.repostImg;
    repostImg.width = 30;
    repostImg.height = 30;
    repostImg.addEventListener('mouseover', ()=> {
        repostImg.src = staticUrls.dataset.repostedImg;
    });
    repostImg.addEventListener('mouseout', ()=> {
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

    let dateStr = post.published;
    let dateObj = new Date(dateStr);
    let options = { year: 'numeric', month: 'long', day: 'numeric', hour: 'numeric', minute: 'numeric', timeZone: 'UTC'};
    let postDateStr = new Intl.DateTimeFormat('en-US', options).format(dateObj);

    const publishedDate = document.createElement('span');
    publishedDate.classList.add('published-date');
    publishedDate.textContent = postDateStr;

    actionButtonsContainer.appendChild(likeImg);
    actionButtonsContainer.appendChild(repostImg);
    actionButtonsContainer.appendChild(publishedDate);

    postSection.appendChild(userInfo);
    postSection.appendChild(title);
    postSection.appendChild(description);
    postSection.appendChild(postContentDiv);
    postContainer.appendChild(postSection);
    postContainer.appendChild(actionButtonsContainer);

    postSection.addEventListener("click", function (event) {
        event.preventDefault();
        window.location.href = `/posts/${encodeURIComponent(post.id)}`;
    });

    likeImg.addEventListener('click', function() {
        const likeUrl = `/api/authors/${username}/liked/send/`;
        likeImg.src = staticUrls.dataset.likedImg;
        isLiked = true;
        likeImg.removeEventListener('mouseout', handleMouseOut);

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
                return response.json();
            } else if (response.status === 409) {
                console.error(`User ${username} already liked this post`);
            } else if (response.status === 400 || response.status === 403 || response.status === 404) {
                console.error(`User ${username} failed to like this post`);
                likeImg.src = staticUrls.dataset.likedImg;
                isLiked = false;
            }
        });
    });

    const postLiked = post.isLiked;
    if (postLiked === true || isLiked === true) {
        likeImg.src = staticUrls.dataset.likedImg;
        isLiked = true;
        likeImg.removeEventListener('mouseout', handleMouseOut);
    }
}

async function handleSearch() {
    const loggedUserID = Cookies.get('id');
    const searchModal = document.getElementById("follow-modal");
    const openSearchModal = document.getElementById("follow-button");
    const submitButton = document.getElementById("id-submit-button");
    const searchError = document.getElementById("follow-error");
    const protocolType = document.getElementById("protocol-type");
    const hostInput = document.getElementById("host-input");
    const usernameInput = document.getElementById("username-input");
    const closeBtn = document.getElementById("close-follow-modal");
    const regex = /^[^%]*$/;

    openSearchModal.onclick = function() {
        searchModal.style.display = "flex";
    };

    closeBtn.onclick = function() {
        searchModal.style.display = "none";
    };

    window.addEventListener("click", function(event) {
        if (event.target === searchModal) {
            searchModal.style.display = "none";
        }
    });

    submitButton.onclick = function() {
        const isValid = regex.test(hostInput.value) && regex.test(usernameInput.value);
        const credentials = Cookies.get('credentials');
        const objectID = `${protocolType.value}://${hostInput.value}/api/authors/${usernameInput.value}`;
        if (!isValid) {
            searchError.textContent = "Invalid input";
            return;
        }
        url = `/api/authors/${loggedUserID.split('/').pop()}/frae/` + objectID;
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Basic ' + credentials,
                'X-Original-Host': window.location.protocol + "//" + window.location.host + "/api/"
            }
        })
        .then(response => {
            if (response.status === 201) {
                searchModal.style.display = "none";
            } else if (response.status === 400) {
                searchError.textContent = "Failed to follow user";
                throw new Error("Failed to follow local user");
            }
        });
    };
}

function credsAuth() {
    const staticUrls = document.getElementById('static-urls');
    const credentials = Cookies.get('credentials');
    
    if (credentials === null || credentials === undefined) {
        console.log(credentials)
        console.log("Hit the first login statement in CredsAuth")
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
        if (response.ok)
            return response.json();
        else
        console.log("Hit the second login statement in CredsAuth")
        Cookies.remove('credentials');
        window.location.href = '/login';
    })
    .catch(error => {
        console.error('Error during authentication:', error);
        Cookies.remove('credentials');
        console.log("Hit the third login statement in CredsAuth")
        window.location.href = '/login';
    });
}
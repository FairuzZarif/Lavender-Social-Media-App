/**
 * @function handleInbox
 * @description Opens the inbox modal for the current user, displaying all the follower requests.
 * @param {string} username - The current user's username, parsed from the credentials.
 * listen to the follower requests API, send GET request every 1 second.
 * @param {string} credentials - The current user's credentials, get from the cookies.
 */
function handleInbox(username, credentials) {
    const staticUrls = document.getElementById('static-urls');
    const modal = document.getElementById("inboxModal");
    const inboxButton = document.getElementById("inbox-button");
    const closeBtn = document.getElementById("close-inbox-modal");

    let inboxMessagesList = [];

    if (closeBtn) {
        closeBtn.onclick = function() {
            modal.style.display = "none";
        };
    }

    window.onclick = function(event) {
        if (event.target === modal)
            modal.style.display = "none";
    };

    const getFollowerRequestsUrl = `/api/authors/${username}/froe/`;
    fetch (getFollowerRequestsUrl, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + credentials,
            'X-Original-Host': window.location.protocol + "//" + window.location.host + "/api/"
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.data_displayed.length === 0) {
            const inboxTitle = document.getElementById("inbox-title");
            if (inboxTitle) {
                inboxTitle.textContent = "There are no new follower requests yet.";
            }
        }
        else {
            inboxButton.src = staticUrls.dataset.inboxImgNew;
            const inboxTitle = document.getElementById("inbox-title");
            if (inboxTitle) {
                inboxTitle.textContent = "";
            }

            data.data_displayed.forEach(request => {
                inboxMessagesList.push([request.id, request.profileImage]);
            });
        }
    });

    inboxButton.onclick = function() {
        console.log(document.getElementById("inboxModal"));
        modal.style.display = "flex";
        modal.classList.add("show");
        console.log(window.getComputedStyle(modal).display);
        const inboxList = document.getElementById("inbox-list");
        inboxList.classList.add("inbox-message-container");
        inboxList.innerHTML = "";

        inboxMessagesList.forEach(messageObject => {
            createMessageElement(messageObject[0], messageObject[1], inboxList);
        });
    };
}

function createMessageElement(id, profileImage, inboxList) {
    const staticUrls = document.getElementById('static-urls');
    const credentials = Cookies.get('credentials');
    const username = atob(credentials).split(':')[0];

    const listitemContainer = document.createElement("div");
    listitemContainer.classList.add("list-item-container");
    const inboxMessage = document.createElement("p");
    
    const acceptButton = document.createElement("button");
    acceptButton.classList.add("inbox-message-buttons");

    const deleteButton = document.createElement("button");
    deleteButton.classList.add("inbox-message-buttons", "delete");

    acceptButton.textContent = "Accept";
    deleteButton.textContent = "Delete";

    acceptButton.addEventListener("click", function() {
        acceptFollowerRequest(username, id, credentials);
    });

    deleteButton.addEventListener("click", function() {
        deleteFollowerRequest(username, id, credentials);
    });

    const userImg = document.createElement('img');
    userImg.src = profileImage || staticUrls.dataset.userProfileImg;
    userImg.onerror = function() {
        userImg.src = staticUrls.dataset.userProfileImg;
    }
    userImg.width = 40;
    userImg.height = 40;
    userImg.style.borderRadius = '50%';

    listitemContainer.appendChild(userImg);
    listitemContainer.appendChild(inboxMessage);
    listitemContainer.appendChild(acceptButton);
    listitemContainer.appendChild(deleteButton);

    inboxMessage.textContent = `${id} wants to follow you.`;

    inboxList.appendChild(listitemContainer);
}

function acceptFollowerRequest(username, id, credentials) {
    const deleteUrl = `/api/authors/${username}/froe/${id}`;

    fetch(deleteUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + credentials,
            'X-Original-Host': window.location.protocol + "//" + window.location.host + "/api/"
        },
    })
    .then(response => {
        if (response.ok) {
            location.reload();
            return response.json();
        } else {
            console.error(`Failed to delete follower request from ${id}`);
        }
    });
}

async function deleteFollowerRequest(username, id, credentials) {
    const deleteFollowerRequestUrl = `/api/authors/${username}/froe/${id}`;

    fetch(deleteFollowerRequestUrl, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + credentials,
            'X-Original-Host': window.location.protocol + "//" + window.location.host + "/api/"
        },
    })
    .then(response => {
        if (response.ok) {
            location.reload();
            return response.json();
        } else {
            console.error(`Failed to delete follower request from ${id}`);
        }
    });
}

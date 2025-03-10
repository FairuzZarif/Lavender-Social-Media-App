document.addEventListener('DOMContentLoaded', async function() {
    credsAuth();

    const credentials = Cookies.get('credentials');
    const username = atob(credentials).split(':')[0];
    handleInbox(username, credentials);
    setInterval(() => handleInbox(username, credentials), 5000);
    
    const userID = Cookies.get('id');
    const urlID = decodeURIComponent(window.location.pathname.split("/authors/")[1].split("/following")[0]);
    const urlPathname = decodeURIComponent(window.location.pathname);
    const match = urlPathname.match(/\/authors\/https?:\/\/[^/]+\/api\/authors\/([^/]+)/);
    const urlUsername = match ? match[1] : null;
    document.getElementById('profile').addEventListener('click', function(){
        window.location.href = `/authors/${encodeURIComponent(Cookies.get('id'))}`;
    });
    document.getElementById('following').addEventListener('click', function(){
        window.location.href = `/authors/${encodeURIComponent(urlID)}/following`;
    });
    document.getElementById('edit-profile').addEventListener('click', function(){
        window.location.href = `/authors/${encodeURIComponent(urlID)}/followers`;
    });
    
    await renderNameAvatar(urlID, userID, credentials);

    const followersData = await getFollowersData(urlUsername, credentials);
    const myFollowersData = await getFollowersData(username, credentials);
    const followerCountText = document.getElementById('follower-count');
    followerCountText.textContent = `${followersData.followers.length} Followers`;
    followerCountText.onclick = function() {
        window.location.href = `/authors/${encodeURIComponent(urlID)}/followers`;
    }

    const followingData = await getFollowingData(urlUsername, credentials);
    const myFollowingData = await getFollowingData(username, credentials);
    const followingCountText = document.getElementById('following-count');
    followingCountText.textContent = `${followingData.following.length} Following`;
    followingCountText.onclick = function() {
        window.location.href = `/authors/${encodeURIComponent(urlID)}/following`;
    }

    renderFollowing(myFollowingData, followingData, username, userID, credentials);

    const nofollowerReminder = document.getElementById('no-following-reminder');
    nofollowerReminder.textContent = "You haven't follow anyone yet.";
});

function renderFollowing(myFollowingData, followingData, myUsername, userID, credentials) {
    const staticUrls = document.getElementById('static-urls');
    let followingLength = 0;
    followingData.following.forEach(following => {
        followingLength = +1;
        const noFollowingReminder = document.getElementById('no-following-reminder');
        if (followingLength > 0) {
            noFollowingReminder.style.display = 'none';
        }

        const followingContainer = document.getElementById('posts-container');
        const followingDiv = document.createElement('div');
        followingDiv.classList.add('follower-container');

        const wordContainer = document.createElement('div');
        wordContainer.classList.add('word-container');

        const userAvatar = document.createElement('img');
        userAvatar.classList.add('followers-avatar');
        userAvatar.src = following.object.profileImage;
        userAvatar.onerror = function () {
            userAvatar.src = staticUrls.dataset.userProfileImg;
        };

        const username = document.createElement('h3');
        username.className = 'username';
        username.textContent = following.object.displayName;

        const followButton = document.createElement('button');
        followButton.className = 'follow-button';
        if (following.object.id === userID) {
            followButton.style.display = 'none';
        } else {
            handlefollowButton(followButton, following, myFollowingData, myUsername, credentials);
        }

        wordContainer.appendChild(username);
        wordContainer.appendChild(followButton);

        followingDiv.appendChild(userAvatar);
        followingDiv.appendChild(wordContainer);

        followingDiv.addEventListener('click', function(event) {
            event.preventDefault();
            window.location.href = `/authors/${encodeURIComponent(following.object.id)}`;
        });

        followingContainer.appendChild(followingDiv);
    });
}

function handlefollowButton(followButton, following, myFollowingData, username, credentials) {
    const isFollowing = myFollowingData.following.some(followingItem => followingItem.object.id === following.object.id);

    if (isFollowing) {
        followButton.textContent = 'Unfollow';
        followButton.onclick = function(event) {
            event.stopPropagation();
            unfollowUser(username, following.object.id, credentials);
        };
    } else {
        followButton.textContent = 'Follow';
        followButton.onclick = function(event) {
            event.stopPropagation();
            followUser(username, following.object.id, credentials);
        };
    }
}

async function unfollowUser(username, followingID, credentials) {
    const url = `/api/authors/${username}/frae/${followingID}`;
    try {
        const response = await fetch(url, {
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
}

async function followUser(username, followingID, credentials) {
    const url = `/api/authors/${username}/frae/${followingID}`;
    try {
        const response = await fetch(url, {
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
}

async function getFollowersData(urlUsername, credentials) {
    const url = `/api/authors/${urlUsername}/followers`;
    let followersData = null;
    try {
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Basic ' + credentials,
                'X-Original-Host': window.location.protocol + "//" + window.location.host + "/api/"
            },
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        followersData = data;
    } catch (error) {
        console.error('Error:', error);
    }
    return followersData;
}


async function getFollowingData(urlUsername, credentials) {
    const url = `/api/authors/${urlUsername}/following`; 
    let followingData = null;
    try {
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Basic ' + credentials,
                'X-Original-Host': window.location.protocol + "//" + window.location.host + "/api/"
            },
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        followingData = data;
    } catch (error) {
        console.error('Error:', error);
    }
    return followingData;
}

async function renderNameAvatar(urlID, userID, credentials) {
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

    const staticUrls = document.getElementById('static-urls');
    const usernameView = document.getElementById("username");
    usernameView.textContent = postOwnerData.displayName || "Unknown User";
    usernameView.classList.add('username');
    usernameView.onclick = function() {
        window.location.href = `/authors/${encodeURIComponent(postOwnerData.id)}`;
    }
    const profileAvatar = document.getElementById("profile-avatar");
    profileAvatar.src = postOwnerData.profileImage;
    profileAvatar.onerror = function () {
        profileAvatar.src = staticUrls.dataset.userProfileImg;
    };
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
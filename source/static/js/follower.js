document.addEventListener('DOMContentLoaded', async function() {
    credsAuth();

    const credentials = Cookies.get('credentials');
    const username = atob(credentials).split(':')[0];
    handleInbox(username, credentials);
    setInterval(() => handleInbox(username, credentials), 5000);
    
    const userID = Cookies.get('id');
    const urlID = decodeURIComponent(window.location.pathname.split("/authors/")[1].split("/followers")[0]);
    const urlPathname = decodeURIComponent(window.location.pathname);
    const match = urlPathname.match(/\/authors\/https?:\/\/[^/]+\/api\/authors\/([^/]+)/);
    const urlUsername = match ? match[1] : null;

    document.getElementById('profile').addEventListener('click', function(){
        window.location.href = `/authors/${encodeURIComponent(Cookies.get('id'))}`;
    });
    document.getElementById('following').addEventListener('click', function(){
        window.location.href = `/authors/${encodeURIComponent(urlID)}/following`;
    });

    await renderNameAvatar(urlID, userID, credentials);

    const followersData = await getFollowersData(urlUsername, credentials);
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

    renderFollowers(followersData, myFollowingData, username, userID, credentials);

    const nofollowerReminder = document.getElementById('no-follower-reminder');
    nofollowerReminder.textContent = 'You have no follower right now.';
});

function renderFollowers(followersData, myFollowingData, myUsername, userID, credentials) {
    const staticUrls = document.getElementById('static-urls');
    let followersLength = 0;
    followersData.followers.forEach(follower => {
        followersLength = +1;
        const noFollowerReminder = document.getElementById('no-follower-reminder');
        if (followersLength > 0) {
            noFollowerReminder.style.display = 'none';
        }

        const followerContainer = document.getElementById('posts-container');
        const followerDiv = document.createElement('div');
        followerDiv.classList.add('follower-container');

        const wordContainer = document.createElement('div');
        wordContainer.classList.add('word-container');

        const userAvatar = document.createElement('img');
        userAvatar.classList.add('followers-avatar');
        userAvatar.src = follower.profileImage;
        userAvatar.onerror = function () {
            userAvatar.src = staticUrls.dataset.userProfileImg;
        };

        const username = document.createElement('h3');
        username.className = 'username';
        username.textContent = follower.displayName;

        const followButton = document.createElement('button');
        followButton.className = 'follow-button';
        if (follower.id === userID) {
            followButton.style.display = 'none';
        }
        else {
            handlefollowButton(followButton, follower, myFollowingData, myUsername, credentials);
        }

        wordContainer.appendChild(username);
        wordContainer.appendChild(followButton);

        followerDiv.appendChild(userAvatar);
        followerDiv.appendChild(wordContainer);

        followerDiv.addEventListener('click', function(event) {
            event.preventDefault();
            window.location.href = `/authors/${encodeURIComponent(follower.id)}`;
        });
        
        followerContainer.appendChild(followerDiv);
    });
}

function handlefollowButton(followButton, follower, followingData, username, credentials) {
    let isFollowing = false;

    if (followingData.following.length === 0) {
        followButton.textContent = 'Follow';
        followButton.onclick = function(event) {
            event.stopPropagation();
            followUser(username, follower.id, credentials);
        };
    } else {
        followingData.following.forEach(following => {
            if (follower.id === following.object.id) {
                isFollowing = true;
                followButton.textContent = 'Unfollow';
                followButton.onclick = function(event) {
                    event.stopPropagation();
                    unfollowUser(username, follower.id, credentials);
                };
            }
        });

        if (!isFollowing) {
            followButton.textContent = 'Follow';
            followButton.onclick = function(event) {
                event.stopPropagation();
                followUser(username, follower.id, credentials);
            };
        }
    }
}


async function unfollowUser(username, followerID, credentials) {
    const url = `/api/authors/${username}/frae/${followerID}`;
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

async function followUser(username, followerID, credentials) {
    const url = `/api/authors/${username}/frae/${followerID}`;
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
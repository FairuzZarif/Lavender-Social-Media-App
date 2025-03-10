document.addEventListener("DOMContentLoaded", function () {
    const hostname = window.location.hostname;
    try {
        const credentials = Cookies.get('credentials');
        const username = atob(credentials).split(':')[0];
    }
    catch (error) {
        window.location.href = `/login`;
    }

    const credentials = Cookies.get('credentials');
    const username = atob(credentials).split(':')[0];
    handleInbox(username, credentials);
    setInterval(() => handleInbox(username, credentials), 5000);
    
    const userID = Cookies.get('id');

    const editButton = document.getElementById("update-username");
    const cancelButton = document.getElementById("cancel-username");
    const usernameErrorMessages = document.getElementById("username-error");
    const githubErrorMessages = document.getElementById("github-error");


    const websiteTitle = document.getElementById('website-title');
    const urlUsername = userID.split('/').pop();
    const url = `/api/authors/${urlUsername}`;

    const usernameInput = document.getElementById("app-username");
    const githubUsername = document.getElementById("app-github");
    const avatarPreview = document.getElementById("avatar-preview");

    let profileImgFile = null;

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
        const displayName = data.displayName;
        const staticUrls = document.getElementById('static-urls');
        usernameInput.value = displayName;
        avatarPreview.src = data.profileImage;
        avatarPreview.onerror = function () {
            avatarPreview.src = staticUrls.dataset.userProfileImg;
        };
        githubUsername.value = data.github.split('/').pop();
    })
    .catch(error => {
        console.error('Error getting display name:', error);
    });

    editButton.addEventListener("click", function (event) {
        event.preventDefault();
        update(usernameInput.value, username, githubUsername.value, credentials);
    });

    cancelButton.addEventListener("click", function (event) {
        event.preventDefault();
        location.href = `/authors/${userID}`;
    });

    const uploadButton = document.getElementById("upload-button");
    const avatarUpload = document.getElementById("avatar-upload");
    uploadButton.addEventListener("click", function (event) {
        event.preventDefault();
        avatarUpload.click();
    });

    avatarUpload.addEventListener("change", function (event) {
        profileImgFile = event.target.files[0];
        if (profileImgFile) {
            const validImageTypes = ["image/jpeg", "image/png", "image/gif", "image/webp"];
            if (validImageTypes.includes(profileImgFile.type)) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    const avatarPreview = document.getElementById("avatar-preview");
                    if (avatarPreview)
                        avatarPreview.src = e.target.result;
                };
                reader.readAsDataURL(profileImgFile);
            } else {
                avatarUpload.value = "";
            }
        }
    });
    
    function update(newUsername, oldUsername, githubUsername, credentials) {
        const usernameRegex = /^[^'"\\:]{1,20}$/;
        const githubUsernameRegex = /^[a-zA-Z0-9]+(?:-[a-zA-Z0-9]+)*$/;
    
        if (newUsername === "") {
            usernameErrorMessages.textContent = "Display name cannot be empty";
        } else if (!usernameRegex.test(newUsername)) {
            usernameErrorMessages.textContent = "Display name is invalid";
        } else if (!githubUsernameRegex.test(githubUsername)) {
            githubErrorMessages.textContent = "Github username is invalid";
        } else {
            usernameErrorMessages.textContent = "";
            const url = `/api/authors/${oldUsername}`;
            const formData = new FormData();
            formData.append("displayName", newUsername);
            if (profileImgFile)
                formData.append("profileImage", profileImgFile);
            formData.append("github", 'https://github.com/' + githubUsername);
            
            fetch(url, {
                method: "PUT",
                headers: {
                    'Authorization': 'Basic ' + credentials,
                    'X-Original-Host': window.location.protocol + "//" + window.location.host + "/api/"
                },
                body: formData,
            })
            .then(response => {
                if (response.ok) {
                    return response.json();
                } else if (response.status === 404) {
                    usernameErrorMessages.textContent = "Invalid username";
                    throw new Error("Invalid username");
                } else {
                    throw new Error("Failed to update");
                }
            })
            .then(data => {
                location.href = `/authors/${userID}`;
            })
            .catch(error => {
                console.error("Update Error", error);
                usernameErrorMessages.textContent = "Username already exists";
            });
        }
    }

    document.getElementById('profile').addEventListener('click', function(){
        window.location.href = `/authors/${encodeURIComponent(Cookies.get('id'))}`;
    });

    document.getElementById('following').addEventListener('click', function(){
        window.location.href = `/authors/${encodeURIComponent(Cookies.get('id'))}/following`;
    });
});

function credsAuth(credentials, username) {
    const hostname = window.location.hostname;
    if (credentials === null || credentials === undefined) {
        window.location.href = `/login`;
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
            window.location.href = `/login`;
    })
    .catch(error => {
        console.error('Error during authentication:', error);
    });
}

function preventOutsider(userID) {
    const urlID = window.location.pathname;
    const match = urlID.match(/(http:\/\/[^\/]+\/api\/authors\/[^\/]+)/);
    if (match === null || match[1] !== userID)
        window.location.href = `/authors/${userID}`;
}

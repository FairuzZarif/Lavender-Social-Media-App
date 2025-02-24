/**
 * Global variables
 * @param {string} mode - login or signup 
 * @param {string} credentials - base64 encoded username and password
 * @param {File} profileImgFile - profile image file
 */
let mode = "login";
let credentials = null;
let profileImgFile = null;

document.addEventListener("DOMContentLoaded", function () {
    main();
});

/**
 * @function main
 * @description main function to initialize the page and handle listeners
 * @returns {void}
 * */
function main() {
    initialize();
    handleUserLogged();
    handleListeners();
}

/**
 * @function initialize
 * @description Initial state of the page
 * */
function initialize() {
    const confirmPasswordInput = document.getElementById("confirm-password");
    const avatarContainer = document.getElementById("image-container");
    const usernameBox = document.getElementById("app-username");
    const passwordBox = document.getElementById("app-password");
    const staticUrls = document.getElementById("static-urls");
    const defaultImgUrl = staticUrls.dataset.userProfileImg;

    confirmPasswordInput.style.display = "none";
    avatarContainer.style.display = "none";
    usernameBox.value = "";
    passwordBox.value = "";
    mode = "login";

    loadDefaultImage(defaultImgUrl);
}

/**
 * @function handleListeners
 * @description Handle listeners for the page
 */
function handleListeners() {
    const reader = new FileReader();
    const staticUrls = document.getElementById('static-urls');
    const signInButton = document.getElementById("sign-in-button");
    const toggleLink = document.getElementById("toggle-link");
    const uploadIcon = document.getElementById("upload-icon");
    const previewAvatar = document.getElementById("avatar-edit");
    const upload = document.getElementById("image-upload");
    const password = document.getElementById("app-password");
    const username = document.getElementById("app-username");

    if (password === null && username === null) {
        signInButton.disabled = true;
    } else {
        signInButton.disabled = false;
        window.addEventListener("keyup", function (event) {
            if (event.key === "Enter")
                signInButton.click();
        });
    }

    signInButton.addEventListener("click", function (event) {
        event.preventDefault();
        const username = document.getElementById("app-username").value;
        const password = document.getElementById("app-password").value;

        if (mode === "login")
            login(username, password);
        else if (mode === "signup")
            signup(username, password);
    });

    toggleLink.addEventListener("click", function (event) {
        event.preventDefault();
        toggleMode();
    });

    uploadIcon.addEventListener("click", function() {
        upload.click();
    });

    upload.addEventListener("change", function(event) {
        profileImgFile = event.target.files[0];
        if (profileImgFile) {
            const validImageTypes = ["image/jpeg", "image/png", "image/gif", "image/webp"];
            if (validImageTypes.includes(profileImgFile.type)) {
                reader.onload = function (e) {
                    if(previewAvatar)
                        previewAvatar.src = e.target.result;
                };
                reader.readAsDataURL(profileImgFile);
            }
            else {
                alert("Invalid file type. Please upload an image (JPEG, PNG, GIF, or WebP).");
                upload.value = "";
            }
        }
    });
}

/**
 * @function handleUserLogged
 * @description Handle if user is already logged in,
 * redirect the user to home page if logged
 */
function handleUserLogged(){
    let credentials = Cookies.get('credentials');
    if (credentials !== undefined) {
        const username = atob(credentials).split(':')[0];
        console.log(username)
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
                Cookies.remove('credentials');
                window.location.href = '/login';
        })
        .then(data => {
            window.location.href = `/home`;
        });
    }
}

/**
 * @description Toggle between login and signup mode,
 * adjust the UI elements based on the mode
 */
function toggleMode() {
    const confirmPasswordInput = document.getElementById("confirm-password");
    const signInButton = document.getElementById("sign-in-button");
    const toggleText = document.getElementById("toggle-text");
    const toggleLink = document.getElementById("toggle-link");
    const errorMessage = document.getElementById("username-error");
    const avatarContainer = document.getElementById("image-container");

    if (mode === "login") {
        avatarContainer.style.display = "flex";
        avatarContainer.style.justifyContent = "center";
        confirmPasswordInput.style.display = "inline-block";
        toggleText.textContent = "Already have an account?";
        toggleLink.textContent = "Log in";
        signInButton.textContent = "Sign up";
        mode = "signup";
    } else {
        avatarContainer.style.display = "none";
        confirmPasswordInput.style.display = "none";
        toggleText.textContent = "Don't have an account?";
        toggleLink.textContent = "Sign up";
        signInButton.textContent = "Sign in";
        mode = "login";
    }
    errorMessage.textContent = "";
}
/**
 * @function login
 * @param {string} username - username user input
 * @param {string} password - password user input
 */
function login(username, password) {
    const errorMessage = document.getElementById("username-error");
    username = username.toLowerCase();
    credentials = btoa(`${username}:${password}`);
    if (username === "") {
        errorMessage.textContent = "Username Cannot Be Empty";
    } else if (password === "") {
        errorMessage.textContent = "Password Cannot Be Empty";
    } else {
        errorMessage.textContent = "";
        const url = `/api/authors/${username}`;
    
        const requestData = {
            "username": username,
            "password": password,
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
            if (response.ok) {
                return response.json();
            } else if (response.status === 401 || response.status === 403) {
                errorMessage.textContent = "Incorrect Password";
                throw new Error('Invalid password');
            } else if (response.status === 404) {
                errorMessage.textContent = "You haven't been signed up/verified yet";
                throw new Error('Invalid username or not verified');
            }
        })
        .then(data => {
            errorMessage.textContent = "";
            Cookies.set('credentials', credentials);
            Cookies.set('id', data.id);
            location.href = `/`;
        })
    }
}

/**
 * @function signup
 * @param {string} username - username user input
 * @param {string} password - password user input
 */
async function signup(username, password) {
    const errorMessage = document.getElementById("username-error");
    const usernameRegex = /^[a-zA-Z0-9]+$/;
    const passwordRegex = /^[a-zA-Z0-9!@#$%^&*()_+={}\[\]:;"'<>,.?/\\|`~\-]+$/;

    username = username.toLowerCase();
    credentials = btoa(`${username}:${password}`);
    const confirmPassword = document.getElementById("confirm-password").value;
     
    if ( username === "" || password === "" || confirmPassword === "") {
        errorMessage.textContent = "Please Fill in The Form";
    } else if (password !== confirmPassword) {
        errorMessage.textContent = "Passwords Do not Match";
    } else if (password.length < 8) {
        errorMessage.textContent = "Password Must Be at Least 8 Characters";
    } else if (!usernameRegex.test(username) || !passwordRegex.test(password)) {
        console.log(username)
        errorMessage.textContent = "Username is invalid";
    } else if(!profileImgFile) {
        errorMessage.textContent = "Please upload a profile image";
    } else{
        errorMessage.textContent = "";
        
        const url = "/api/authors/";
        const formData = new FormData();
        formData.append("displayName", username);
        formData.append("username", username);
        formData.append("password", password);
        formData.append("profileImage", profileImgFile);

        fetch(url, {
            method: "POST",
            body: formData
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                errorMessage.textContent = "Username Already Exists/Something went Wrong";
                throw new Error('Username already Exists');
            }
        })
        .then(data => {
            location.reload();
            document.getElementById("app-username").value = username;
        })
    }
}

/** 
 * @function loadDefaultImage
 * @description Load the default image from the server
 * @param {string} defaultImgUrl - default image url
 */
async function loadDefaultImage(defaultImgUrl) {
    try {
        const response = await fetch(defaultImgUrl);
        if (!response.ok)
            throw new Error("Failed to fetch the default image.");
        const blob = await response.blob();
        const reader = new FileReader();
        reader.onload = function (e) {
            profileImgFile = blob;
        };
        reader.readAsDataURL(blob);
    } catch (error) {
        console.error("Error loading default image:", error);
    }
}

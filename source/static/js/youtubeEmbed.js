// youtubeEmbed.js

/**
 * Extracts the YouTube video ID from a given content string.
 * @param {string} content - The content to search for a YouTube link.
 * @returns {string|null} - The extracted YouTube video ID or null if not found.
 */
function extractYouTubeVideoId(content) {
    const regex = /(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|embed|shorts)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})/;
    const match = content.match(regex);
    return match ? match[1] : null;
}

/**
 * Creates an iframe element for embedding a YouTube video.
 * @param {string} videoId - The YouTube video ID.
 * @returns {HTMLIFrameElement} - The iframe element.
 */
function createYouTubeEmbed(videoId) {
    const iframe = document.createElement('iframe');
    iframe.src = `https://www.youtube.com/embed/${videoId}`;
    iframe.width = "560";
    iframe.height = "315";
    iframe.frameBorder = "0";
    iframe.allowFullscreen = true;
    return iframe;
}

/**
 * Handles the embedding of YouTube videos in a post's content.
 * @param {Object} post - The post object.
 * @param {HTMLElement} postContent - The post content element.
 */
function handleYoutubeEmbed(post, postContent) {
    const videoId = extractYouTubeVideoId(post.content);
    if (videoId) {
        const youtubeEmbed = createYouTubeEmbed(videoId);
        postContent.appendChild(youtubeEmbed);
    } else {
        postContent.textContent = post.content;
    } 
}
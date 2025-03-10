/**
 * Extracts the Spotify embed URL from a given Spotify link.
 * @param {string} content - The Spotify URL to process.
 * @returns {string|null} - The converted Spotify embed URL or null if invalid.
 */
function extractSpotifyEmbedUrl(content) {
    if (!content.includes('open.spotify.com')) {
        return null;
    }
    return content.replace('open.spotify.com', 'open.spotify.com/embed').split('?')[0];
}

/**
 * Creates an iframe element for embedding a Spotify player.
 * @param {string} embedUrl - The Spotify embed URL.
 * @param {number} width - The width of the player (default: 300).
 * @param {number} height - The height of the player (default: 380).
 * @returns {HTMLIFrameElement} - The iframe element.
 */
function createSpotifyEmbed(embedUrl, width = 300, height = 380) {
    const iframe = document.createElement('iframe');
    iframe.src = embedUrl;
    iframe.width = width.toString();
    iframe.height = height.toString();
    iframe.allow = "autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture";
    iframe.frameBorder = "0";
    iframe.style.borderRadius = "12px";
    return iframe;
}

function handleSpotifyEmbed(post, postContent) {
    const embedUrl = extractSpotifyEmbedUrl(post.content);
    if (embedUrl) {
        const spotifyEmbed = createSpotifyEmbed(embedUrl);
        postContent.appendChild(spotifyEmbed);
    } else {
        postContent.textContent = post.content;
    }
}

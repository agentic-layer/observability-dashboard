export const getWebSocketUrl = () => {
    // In production, use the environment variable or construct from window location
    if (import.meta.env.PROD) {
        // Check for environment variable first
        if (import.meta.env.VITE_WS_URL) {
            return import.meta.env.VITE_WS_URL;
        }
        
        // Otherwise, construct from current location
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        return `${protocol}//${host}/ws`;
    }
    
    // In development, use localhost
    return 'ws://localhost:10005/ws';
};
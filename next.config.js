/** @type {import('next').NextConfig} */
const nextConfig = {
    // Enable React strict mode for better development experience
    reactStrictMode: true,

    // Ignore the _streamlit_backup folder during build
    eslint: {
        ignoreDuringBuilds: false,
    },

    // Image optimization config
    images: {
        domains: [],
    },
}

module.exports = nextConfig

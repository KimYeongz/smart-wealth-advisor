import type { Config } from "tailwindcss";

const config: Config = {
    darkMode: "class",
    content: [
        "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
        "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
        "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    ],
    theme: {
        extend: {
            colors: {
                // Custom colors for financial app
                primary: {
                    DEFAULT: "#00D26A",  // Green accent
                    50: "#E6FFF2",
                    100: "#B3FFD9",
                    200: "#80FFC0",
                    300: "#4DFFA7",
                    400: "#1AFF8E",
                    500: "#00D26A",
                    600: "#00A654",
                    700: "#007A3E",
                    800: "#004D28",
                    900: "#002112",
                },
                gold: {
                    DEFAULT: "#FFD700",
                    500: "#FFD700",
                },
                dark: {
                    DEFAULT: "#0F1117",
                    50: "#1E222A",
                    100: "#1A1D24",
                    200: "#151820",
                    300: "#0F1117",
                },
            },
            fontFamily: {
                sans: ["Noto Sans Thai", "Inter", "sans-serif"],
            },
            backgroundImage: {
                "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
                "gradient-primary": "linear-gradient(135deg, #00D26A 0%, #FFD700 100%)",
            },
        },
    },
    plugins: [],
};

export default config;

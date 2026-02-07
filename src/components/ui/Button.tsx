import { cn } from "@/lib/utils";
import { ButtonHTMLAttributes, forwardRef } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: "primary" | "secondary" | "outline" | "ghost" | "danger";
    size?: "sm" | "md" | "lg";
    isLoading?: boolean;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
    ({ className, variant = "primary", size = "md", isLoading, children, disabled, ...props }, ref) => {
        return (
            <button
                ref={ref}
                disabled={disabled || isLoading}
                className={cn(
                    "inline-flex items-center justify-center font-semibold rounded-xl transition-all duration-200",
                    "focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-dark-300",
                    "disabled:opacity-50 disabled:cursor-not-allowed",
                    // Variants
                    variant === "primary" &&
                    "bg-primary hover:bg-primary-600 text-white focus:ring-primary/50 hover:shadow-lg hover:shadow-primary/20",
                    variant === "secondary" &&
                    "bg-dark-50 hover:bg-dark-100 text-white border border-gray-700 focus:ring-gray-500",
                    variant === "outline" &&
                    "bg-transparent border-2 border-primary text-primary hover:bg-primary/10 focus:ring-primary/50",
                    variant === "ghost" &&
                    "bg-transparent text-gray-400 hover:text-white hover:bg-dark-50 focus:ring-gray-500",
                    variant === "danger" &&
                    "bg-red-500 hover:bg-red-600 text-white focus:ring-red-500/50",
                    // Sizes
                    size === "sm" && "px-4 py-2 text-sm",
                    size === "md" && "px-6 py-3 text-base",
                    size === "lg" && "px-8 py-4 text-lg",
                    className
                )}
                {...props}
            >
                {isLoading ? (
                    <svg className="animate-spin h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path
                            className="opacity-75"
                            fill="currentColor"
                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                        />
                    </svg>
                ) : null}
                {children}
            </button>
        );
    }
);

Button.displayName = "Button";

export { Button };

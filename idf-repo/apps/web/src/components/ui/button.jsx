import React from "react";
import { cn } from "../../lib/utils";

const variants = {
  primary:
    "bg-[hsl(220,90%,56%)] text-white hover:bg-[hsl(220,90%,48%)] shadow-sm shadow-blue-500/20",
  secondary:
    "bg-white text-[hsl(220,14%,20%)] border border-[hsl(220,13%,88%)] hover:bg-[hsl(220,14%,97%)] shadow-sm",
  ghost:
    "text-[hsl(220,8%,46%)] hover:text-[hsl(220,14%,20%)] hover:bg-[hsl(220,14%,95%)]",
  danger:
    "bg-red-50 text-red-600 border border-red-200 hover:bg-red-100",
};

const sizes = {
  sm: "h-7 px-2.5 text-xs gap-1",
  md: "h-8 px-3 text-sm gap-1.5",
  lg: "h-9 px-4 text-sm gap-2",
};

export function Button({
  className,
  variant = "primary",
  size = "md",
  ...props
}) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center rounded-lg font-medium",
        "transition-all duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-400/40 focus-visible:ring-offset-1",
        "disabled:opacity-40 disabled:pointer-events-none",
        "active:scale-[0.97]",
        variants[variant] || variants.primary,
        sizes[size] || sizes.md,
        className
      )}
      {...props}
    />
  );
}

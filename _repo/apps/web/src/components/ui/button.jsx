import React from "react";
import { cn } from "../../lib/utils";

export function Button({ className, ...props }) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center rounded-md text-sm font-medium",
        "h-9 px-4 py-2 bg-black text-white hover:bg-black/85",
        "transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 ring-neutral-400",
        className
      )}
      {...props}
    />
  );
}

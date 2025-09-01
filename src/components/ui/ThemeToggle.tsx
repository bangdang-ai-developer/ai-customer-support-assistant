'use client';

import React, { useContext } from 'react';
import { useTheme } from '@/contexts/ThemeContext';

export function ThemeToggle() {
  try {
    const { theme, toggleTheme } = useTheme();
    
    // If we get here, the context is available
    return <ThemeToggleComponent theme={theme} toggleTheme={toggleTheme} />;
  } catch (error) {
    // Fallback if ThemeProvider is not available
    return null;
  }
}

function ThemeToggleComponent({ theme, toggleTheme }: { theme: string; toggleTheme: () => void }) {

  return (
    <button
      onClick={toggleTheme}
      className="relative p-2 rounded-xl bg-gradient-to-r from-purple-500/10 to-pink-500/10 
                 dark:from-purple-400/20 dark:to-pink-400/20
                 hover:from-purple-500/20 hover:to-pink-500/20
                 transition-all duration-300 hover:scale-105 active:scale-95"
      aria-label="Toggle theme"
    >
      <div className="relative w-6 h-6">
        <svg
          className={`absolute inset-0 w-6 h-6 text-yellow-500 transition-all duration-300 ${
            theme === 'light' ? 'opacity-100 rotate-0' : 'opacity-0 rotate-90'
          }`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
          />
        </svg>

        <svg
          className={`absolute inset-0 w-6 h-6 text-purple-400 transition-all duration-300 ${
            theme === 'dark' ? 'opacity-100 rotate-0' : 'opacity-0 -rotate-90'
          }`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
          />
        </svg>
      </div>
    </button>
  );
}
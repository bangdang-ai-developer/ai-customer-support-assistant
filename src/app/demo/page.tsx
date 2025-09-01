'use client';

import React from 'react';
import { ThemeToggle } from '@/components/ui/ThemeToggle';

export default function DemoPage() {
  return (
    <div className="min-h-screen enhanced-chat-container">
      <div className="container mx-auto p-6">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold gradient-text">Enhanced UI Demo</h1>
          <ThemeToggle />
        </div>

        <div className="max-w-3xl mx-auto glass rounded-3xl p-6 custom-scrollbar">
          <h2 className="text-xl font-semibold mb-6 text-center">Dark Mode & Enhanced Styles</h2>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <button className="quick-action">Quick Action 1</button>
            <button className="quick-action">Quick Action 2</button>
            <button className="quick-action">Quick Action 3</button>
            <button className="quick-action">Quick Action 4</button>
          </div>

          <div className="space-y-4 mb-6">
            <div className="card-lift bg-white dark:bg-gray-800 p-4 rounded-2xl border border-gray-200 dark:border-gray-700">
              <h3 className="font-semibold mb-2">Card with Lift Effect</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">Hover over this card to see the lift animation!</p>
            </div>

            <div className="btn-glow bg-gradient-to-r from-purple-500 to-pink-500 text-white p-4 rounded-2xl">
              <h3 className="font-semibold mb-2">Glow Button Effect</h3>
              <p className="text-sm opacity-90">Hover to see the glow effect!</p>
            </div>
          </div>

          <div className="space-y-3">
            <h3 className="font-semibold">UI Features Demonstrated:</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span>Dark Mode Toggle</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                <span>Glass Morphism Effects</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
                <span>Gradient Text & Backgrounds</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-pink-500 rounded-full"></div>
                <span>Hover Animations</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
                <span>Custom Scrollbars</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-cyan-500 rounded-full"></div>
                <span>Smooth Transitions</span>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-8 text-center">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Try switching between light and dark modes using the toggle above!
          </p>
        </div>
      </div>
    </div>
  );
}
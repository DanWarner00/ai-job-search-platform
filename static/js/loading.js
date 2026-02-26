/**
 * Loading Overlay System
 * Better loading states than basic text
 */

class LoadingOverlay {
    constructor() {
        this.overlay = null;
    }

    show(message = 'Loading...') {
        // Remove existing if any
        this.hide();

        this.overlay = document.createElement('div');
        this.overlay.id = 'loading-overlay';
        this.overlay.className = 'fixed inset-0 bg-black bg-opacity-75 z-[60] flex items-center justify-center';
        this.overlay.innerHTML = `
            <div class="bg-gray-800 rounded-xl shadow-2xl p-8 flex flex-col items-center gap-4 border border-gray-700">
                <div class="relative w-16 h-16">
                    <div class="absolute inset-0 border-4 border-gray-600 rounded-full"></div>
                    <div class="absolute inset-0 border-4 border-blue-500 rounded-full border-t-transparent animate-spin"></div>
                </div>
                <div class="text-gray-200 font-medium text-lg">${message}</div>
            </div>
        `;
        
        document.body.appendChild(this.overlay);
        return this.overlay;
    }

    hide() {
        const existing = document.getElementById('loading-overlay');
        if (existing) {
            existing.remove();
        }
        this.overlay = null;
    }

    update(message) {
        if (this.overlay) {
            const messageEl = this.overlay.querySelector('.text-gray-200');
            if (messageEl) {
                messageEl.textContent = message;
            }
        }
    }
}

// Global instance
window.loading = new LoadingOverlay();

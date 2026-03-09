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
        this.overlay.setAttribute('style', 'position:fixed;inset:0;background:rgba(26,24,20,0.50);z-index:60;display:flex;align-items:center;justify-content:center;');
        this.overlay.innerHTML = `
            <div style="background:#ede8df;border:1px solid #ddd8d0;border-radius:8px;padding:32px;display:flex;flex-direction:column;align-items:center;gap:16px;box-shadow:0 12px 40px rgba(26,24,20,0.12);">
                <div style="position:relative;width:48px;height:48px;">
                    <div style="position:absolute;inset:0;border:3px solid #ddd8d0;border-radius:50%;"></div>
                    <div style="position:absolute;inset:0;border:3px solid #c84b2f;border-radius:50%;border-top-color:transparent;animation:spin 0.8s linear infinite;"></div>
                </div>
                <div style="font-family:'DM Mono',monospace;font-size:12px;letter-spacing:0.06em;color:#6b6560;text-transform:uppercase;">${message}</div>
            </div>
            <style>@keyframes spin{to{transform:rotate(360deg)}}</style>
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

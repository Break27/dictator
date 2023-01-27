export default class DisplayMode {
    Modes = ['light', 'dark', 'default'];

    constructor() {
        this.apply();
    }

    currentMode() {
        return localStorage.theme ?? 'default';
    }

    toggle() {
        const index = this.Modes.indexOf(this.currentMode());
        const next = this.Modes[index < 2 ? index + 1 : 0];

        if (next === 'default') localStorage.removeItem('theme');
        else localStorage.theme = next;
        this.apply();
        return next;
    }

    apply() {
        if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
    }
}
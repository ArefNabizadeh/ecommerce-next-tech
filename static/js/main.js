// ========================================
// CURSOR CONTROLLER - NEXT TECH
// ========================================

document.addEventListener('DOMContentLoaded', () => {

    const cursor = {
        dot: document.querySelector('.cursor-dot'),
        ring: document.querySelector('.cursor-ring'),
        progress: document.querySelector('.scroll-progress'),
        x: 0,
        y: 0,
        ringX: 0,
        ringY: 0,
        isHovering: false,
        isClicking: false,

        init() {
            if (window.innerWidth < 1024) {
                this.hide();
                return;
            }
            this.bindEvents();
            this.animate();
        },

        bindEvents() {
            document.addEventListener('mousemove', (e) => {
                this.x = e.clientX;
                this.y = e.clientY;
                this.dot.style.transform = `translate(${this.x - 3}px, ${this.y - 3}px)`;
            });

            // ===== تشخیص المنت‌های قابل کلیک و لینک‌ها =====
            const interactiveElements = document.querySelectorAll(
                'a, button, input, select, textarea, ' +
                '[role="button"], [role="link"], ' +
                '.cursor-pointer, .hoverable, ' +
                '.btn, .button, [onclick]'
            );

            interactiveElements.forEach(el => {
                el.addEventListener('mouseenter', () => {
                    this.ring.classList.add('hover');
                    this.isHovering = true;
                });
                el.addEventListener('mouseleave', () => {
                    this.ring.classList.remove('hover');
                    this.isHovering = false;
                });
            });

            // ===== تشخیص المنت‌های متنی (برای حالت text) =====
            document.querySelectorAll('p, span, h1, h2, h3, h4, h5, h6, label, .text').forEach(el => {
                el.addEventListener('mouseenter', () => {
                    if (!this.isHovering) {
                        this.ring.classList.add('text');
                    }
                });
                el.addEventListener('mouseleave', () => {
                    this.ring.classList.remove('text');
                });
            });

            // ===== کلیک =====
            document.addEventListener('mousedown', () => {
                this.ring.classList.add('click');
                this.isClicking = true;
            });
            document.addEventListener('mouseup', () => {
                this.ring.classList.remove('click');
                this.isClicking = false;
            });

            // ===== خروج از صفحه =====
            document.addEventListener('mouseleave', () => {
                this.hide();
            });
            document.addEventListener('mouseenter', () => {
                this.show();
            });

            // ===== اسکرول پیشرفت =====
            window.addEventListener('scroll', () => {
                const scrollTop = window.scrollY;
                const docHeight = document.documentElement.scrollHeight - window.innerHeight;
                const progress = (scrollTop / docHeight) * 100;
                this.progress.style.width = progress + '%';
            });

            // ===== تغییر سایز پنجره =====
            window.addEventListener('resize', () => {
                if (window.innerWidth < 1024) {
                    this.hide();
                    document.body.style.cursor = 'auto';
                } else {
                    this.show();
                    document.body.style.cursor = 'none';
                }
            });
        },

        animate() {
            this.ringX += (this.x - this.ringX) * 0.15;
            this.ringY += (this.y - this.ringY) * 0.15;
            this.ring.style.transform = `translate(${this.ringX - 18}px, ${this.ringY - 18}px)`;
            requestAnimationFrame(() => this.animate());
        },

        hide() {
            if (this.dot) this.dot.classList.add('hidden');
            if (this.ring) this.ring.classList.add('hidden');
            document.body.style.cursor = 'auto';
        },

        show() {
            if (this.dot) this.dot.classList.remove('hidden');
            if (this.ring) this.ring.classList.remove('hidden');
            document.body.style.cursor = 'none';
        }
    };

    cursor.init();
});
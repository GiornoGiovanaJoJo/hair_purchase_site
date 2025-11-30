// ===== НАВИГАЦИЯ ПО СЕКЦИЯМ =====
document.addEventListener('DOMContentLoaded', function() {
    // Получаем все кнопки навигации
    const navButtons = document.querySelectorAll('.nav-btn, .dot');
    const sections = document.querySelectorAll('.section');

    // Функция переключения секций
    function switchSection(sectionId) {
        // Убираем активный класс со всех секций
        sections.forEach(section => {
            section.classList.remove('active');
        });

        // Убираем активный класс со всех кнопок
        document.querySelectorAll('.nav-btn, .dot').forEach(btn => {
            btn.classList.remove('active');
        });

        // Добавляем активный класс к выбранной секции
        const targetSection = document.getElementById(sectionId);
        if (targetSection) {
            targetSection.classList.add('active');
        }

        // Добавляем активный класс к соответствующим кнопкам
        document.querySelectorAll(`[data-section="${sectionId}"]`).forEach(btn => {
            btn.classList.add('active');
        });

        // Плавная прокрутка наверх
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    // Обработчики для всех кнопок навигации
    navButtons.forEach(button => {
        button.addEventListener('click', function() {
            const sectionId = this.getAttribute('data-section');
            if (sectionId) {
                switchSection(sectionId);
            }
        });
    });

    // Глобальная функция для прокрутки к секции
    window.scrollToSection = function(sectionId) {
        switchSection(sectionId);
    };
});

// ===== ПЛАВНОЕ ПОЯВЛЕНИЕ ЭЛЕМЕНТОВ ===== 
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Наблюдаем за карточками
document.querySelectorAll('.feature-card').forEach((card, index) => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(30px)';
    card.style.transition = `all 0.6s ease ${index * 0.1}s`;
    observer.observe(card);
});

// ===== АНИМАЦИЯ HERO ИЗОБРАЖЕНИЯ =====
const heroImage = document.getElementById('heroImage');
if (heroImage) {
    // Эффект параллакса при прокрутке
    window.addEventListener('scroll', function() {
        const scrolled = window.pageYOffset;
        if (heroImage.style) {
            heroImage.style.transform = `translateY(${scrolled * 0.5}px) scale(1.1)`;
        }
    });

    // Устанавливаем placeholder если нет изображения
    heroImage.onerror = function() {
        this.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080"%3E%3Cdefs%3E%3ClinearGradient id="grad" x1="0%25" y1="0%25" x2="100%25" y2="100%25"%3E%3Cstop offset="0%25" style="stop-color:%23e74c3c;stop-opacity:1" /%3E%3Cstop offset="100%25" style="stop-color:%23c0392b;stop-opacity:1" /%3E%3C/linearGradient%3E%3C/defs%3E%3Crect width="1920" height="1080" fill="url(%23grad)" /%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" font-family="Arial" font-size="48" fill="white" font-weight="bold"%3EСкупка натуральных волос%3C/text%3E%3C/svg%3E';
    };
}

// ===== КЛАВИАТУРНАЯ НАВИГАЦИЯ =====
document.addEventListener('keydown', function(e) {
    const sections = ['home', 'calculator', 'application'];
    const currentSection = document.querySelector('.section.active');
    const currentId = currentSection ? currentSection.id : 'home';
    const currentIndex = sections.indexOf(currentId);

    // Стрелка вправо или вниз - следующая секция
    if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
        e.preventDefault();
        const nextIndex = (currentIndex + 1) % sections.length;
        window.scrollToSection(sections[nextIndex]);
    }

    // Стрелка влево или вверх - предыдущая секция
    if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
        e.preventDefault();
        const prevIndex = (currentIndex - 1 + sections.length) % sections.length;
        window.scrollToSection(sections[prevIndex]);
    }
});

// ===== CONSOLE LOG =====
console.log('%c🧑‍🦰 Сайт скупки волос загружен!', 'color: #e74c3c; font-size: 20px; font-weight: bold;');
console.log('%cРазработано с ❤️ для вас', 'color: #95a5a6; font-size: 12px;');

// ===== API ИНТЕГРАЦИЯ (для будущего расширения) =====
// Калькулятор и форма будут добавлены позже
// API эндпоинты: /api/calculator/ и /api/applications/
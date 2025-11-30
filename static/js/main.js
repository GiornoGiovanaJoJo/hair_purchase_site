// ===== CSRF TOKEN =====
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

// ===== НАВИГАЦИЯ ПО СЕКЦИЯМ =====
document.addEventListener('DOMContentLoaded', function() {
    const navButtons = document.querySelectorAll('.nav-btn, .dot');
    const sections = document.querySelectorAll('.section');

    function switchSection(sectionId) {
        sections.forEach(section => {
            section.classList.remove('active');
        });

        document.querySelectorAll('.nav-btn, .dot').forEach(btn => {
            btn.classList.remove('active');
        });

        const targetSection = document.getElementById(sectionId);
        if (targetSection) {
            targetSection.classList.add('active');
        }

        document.querySelectorAll(`[data-section="${sectionId}"]`).forEach(btn => {
            btn.classList.add('active');
        });

        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    navButtons.forEach(button => {
        button.addEventListener('click', function() {
            const sectionId = this.getAttribute('data-section');
            if (sectionId) {
                switchSection(sectionId);
            }
        });
    });

    window.scrollToSection = function(sectionId) {
        switchSection(sectionId);
    };
});

// ===== КАЛЬКУЛЯТОР СТОИМОСТИ =====
const calculatorForm = document.getElementById('calculatorForm');
const priceResult = document.getElementById('priceResult');
const estimatedPriceElement = document.getElementById('estimatedPrice');

if (calculatorForm) {
    calculatorForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        const formData = new FormData(this);
        const data = {
            length: formData.get('length'),
            color: formData.get('color'),
            structure: formData.get('structure'),
            condition: formData.get('condition')
        };

        const submitButton = this.querySelector('button[type="submit"]');
        const btnText = submitButton.querySelector('.btn-text');
        const btnLoader = submitButton.querySelector('.btn-loader');
        
        btnText.classList.add('hidden');
        btnLoader.classList.remove('hidden');
        submitButton.disabled = true;

        try {
            const response = await fetch('/api/calculator/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                },
                credentials: 'same-origin',
                body: JSON.stringify(data)
            });

            if (response.ok) {
                const result = await response.json();
                estimatedPriceElement.textContent = `${result.estimated_price.toLocaleString('ru-RU')} ₽`;
                priceResult.classList.remove('hidden');
                
                setTimeout(() => {
                    priceResult.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                }, 300);
            } else {
                const error = await response.json();
                console.error('API Error:', error);
                alert('Ошибка при расчете стоимости. Попробуйте снова.');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Произошла ошибка. Проверьте подключение к интернету.');
        } finally {
            btnText.classList.remove('hidden');
            btnLoader.classList.add('hidden');
            submitButton.disabled = false;
        }
    });
}

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

document.querySelectorAll('.feature-card').forEach((card, index) => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(30px)';
    card.style.transition = `all 0.6s ease ${index * 0.1}s`;
    observer.observe(card);
});

// ===== АНИМАЦИЯ HERO ИЗОБРАЖЕНИЯ =====
const heroImage = document.getElementById('heroImage');
if (heroImage) {
    window.addEventListener('scroll', function() {
        const scrolled = window.pageYOffset;
        if (heroImage.style) {
            heroImage.style.transform = `translateY(${scrolled * 0.5}px) scale(1.1)`;
        }
    });

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

    if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
        e.preventDefault();
        const nextIndex = (currentIndex + 1) % sections.length;
        window.scrollToSection(sections[nextIndex]);
    }

    if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
        e.preventDefault();
        const prevIndex = (currentIndex - 1 + sections.length) % sections.length;
        window.scrollToSection(sections[prevIndex]);
    }
});

// ===== CONSOLE LOG =====
console.log('%c🧑‍🦰 Сайт скупки волос загружен!', 'color: #e74c3c; font-size: 20px; font-weight: bold;');
console.log('%cРазработано с ❤️ для вас', 'color: #95a5a6; font-size: 12px;');
console.log('%c🔧 API: /api/calculator/ и /api/applications/', 'color: #3498db; font-size: 14px;');
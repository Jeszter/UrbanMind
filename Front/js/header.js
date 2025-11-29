// Функция для определения активной страницы
function highlightCurrentPage() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-menu a');

    console.log("Current path:", currentPath);

    // Убираем активный класс у всех ссылок
    navLinks.forEach(link => {
        link.classList.remove('active');
    });

    // Определяем текущую страницу
    let activePage = '';

    // Главная страница
    if (currentPath === '/' || currentPath === '' || currentPath === '/home') {
        activePage = 'home';
    }
    // Work & Education pages
    else if (currentPath === '/neurohr' || currentPath.includes('neurohr')) {
        activePage = 'neurohr';
    }
    else if (currentPath === '/jobs' || currentPath.includes('jobs')) {
        activePage = 'jobs';
    }
    else if (currentPath === '/career' || currentPath.includes('career')) {
        activePage = 'career';
    }
    else if (currentPath === '/courses' || currentPath.includes('courses')) {
        activePage = 'courses';
    }
    else if (currentPath === '/certification' || currentPath.includes('certification')) {
        activePage = 'certification';
    }
    else if (currentPath === '/language-learning' || currentPath.includes('language-learning')) {
        activePage = 'language-learning';
    }
    // Documents pages
    else if (currentPath === '/visa' || currentPath.includes('visa')) {
        activePage = 'visa';
    }
    else if (currentPath === '/registration' || currentPath.includes('registration')) {
        activePage = 'registration';
    }
    else if (currentPath === '/banking' || currentPath.includes('banking')) {
        activePage = 'banking';
    }
    else if (currentPath === '/legal' || currentPath.includes('legal')) {
        activePage = 'legal';
    }
    // Language & Social pages
    else if (currentPath === '/translation' || currentPath.includes('translation')) {
        activePage = 'translation';
    }
    else if (currentPath === '/cultural-guide' || currentPath.includes('cultural-guide')) {
        activePage = 'cultural-guide';
    }
    else if (currentPath === '/social-events' || currentPath.includes('social-events')) {
        activePage = 'social-events';
    }
    else if (currentPath === '/community' || currentPath.includes('community')) {
        activePage = 'community';
    }
    // Housing
    else if (currentPath === '/housing' || currentPath.includes('housing')) {
        activePage = 'housing';
    }

    console.log("Active page detected:", activePage);

    // Находим и активируем соответствующую ссылку
    const activeLink = document.querySelector(`.nav-menu a[data-page="${activePage}"]`);
    if (activeLink) {
        console.log("Found active link:", activeLink);
        activeLink.classList.add('active');

        // Активируем родительский пункт для вложенных страниц
        const parentPages = {
            'neurohr': 'work',
            'jobs': 'work',
            'career': 'work',
            'courses': 'work',
            'certification': 'work',
            'language-learning': 'work',
            'visa': 'docs',
            'registration': 'docs',
            'banking': 'docs',
            'legal': 'docs',
            'translation': 'lang',
            'cultural-guide': 'lang',
            'social-events': 'lang',
            'community': 'lang'
        };

        if (parentPages[activePage]) {
            const parentLink = document.querySelector(`.nav-menu a[data-page="${parentPages[activePage]}"]`);
            if (parentLink) {
                console.log("Found parent link:", parentLink);
                parentLink.classList.add('active');
            }
        }
    } else {
        console.log("No active link found for page:", activePage);
    }
}

// Обработчик мобильного меню
function initMobileMenu() {
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navMenu = document.querySelector('.nav-menu');

    if (mobileMenuBtn && navMenu) {
        mobileMenuBtn.addEventListener('click', function() {
            navMenu.classList.toggle('active');

            // Смена иконки меню
            const icon = this.querySelector('i');
            if (navMenu.classList.contains('active')) {
                icon.classList.remove('fa-bars');
                icon.classList.add('fa-times');
            } else {
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            }
        });
    }

    // Закрытие меню при клике на ссылку (для мобильных)
    const navLinks = document.querySelectorAll('.nav-menu a');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            if (window.innerWidth <= 850 && navMenu) {
                navMenu.classList.remove('active');
                const icon = mobileMenuBtn.querySelector('i');
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            }
        });
    });
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM loaded, initializing header...");
    highlightCurrentPage();
    initMobileMenu();
});

// Если хедер загружается динамически, вызываем функцию после загрузки
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', highlightCurrentPage);
} else {
    highlightCurrentPage();
}
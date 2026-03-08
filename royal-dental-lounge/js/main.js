// Royal Dental Lounge — Global JavaScript

document.addEventListener('DOMContentLoaded', () => {
    // 1. Navigation Scroll Effect
    const nav = document.querySelector('.nav');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            nav.classList.add('scrolled');
        } else {
            nav.classList.remove('scrolled');
        }
    });

    // 2. Mobile Menu Toggle
    const hamburgerBtn = document.getElementById('hamburger-btn');
    const mobileCloseBtn = document.getElementById('mobile-close-btn');
    const mobileMenu = document.getElementById('mobile-menu');

    if (hamburgerBtn && mobileMenu && mobileCloseBtn) {
        hamburgerBtn.addEventListener('click', () => {
            mobileMenu.classList.add('active');
            document.body.style.overflow = 'hidden'; // prevent scrolling
        });

        mobileCloseBtn.addEventListener('click', () => {
            mobileMenu.classList.remove('active');
            document.body.style.overflow = '';
        });

        // Close when clicking a link inside mobile menu
        const mobileLinks = mobileMenu.querySelectorAll('a');
        mobileLinks.forEach(link => {
            link.addEventListener('click', () => {
                mobileMenu.classList.remove('active');
                document.body.style.overflow = '';
            });
        });
    }

    // 3. Scroll Animations (Intersection Observer)
    const animateElements = document.querySelectorAll('.animate-on-scroll');

    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.15
    };

    const scrollObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                observer.unobserve(entry.target); // Animate only once
            }
        });
    }, observerOptions);

    animateElements.forEach(el => {
        scrollObserver.observe(el);
    });

    // 4. FAQ Accordion
    const faqItems = document.querySelectorAll('.faq-item');
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        const answer = item.querySelector('.faq-answer');

        question.addEventListener('click', () => {
            const isActive = item.classList.contains('active');

            // Close all other FAQs
            faqItems.forEach(otherItem => {
                otherItem.classList.remove('active');
                otherItem.querySelector('.faq-answer').style.maxHeight = null;
            });

            // Toggle current FAQ
            if (!isActive) {
                item.classList.add('active');
                answer.style.maxHeight = answer.scrollHeight + "px";
            }
        });
    });

    // 5. Appointment Form Submission 
    const contactForm = document.getElementById('appointment-form');
    if (contactForm) {
        contactForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const name = document.getElementById('name').value;

            // Show toast notification
            showToast(`✅ Thank you, ${name}! We'll confirm your appointment shortly.`);
            contactForm.reset();
        });
    }

    // 6. Number Counter Animation (for hero stats)
    const stats = document.querySelectorAll('.hero-stat-number[data-target]');
    let hasCounted = false;

    const startCounters = () => {
        stats.forEach(stat => {
            const target = +stat.getAttribute('data-target');
            const duration = 2000; // ms
            const increment = target / (duration / 16); // 60fps
            let current = 0;

            const updateCounter = () => {
                current += increment;
                if (current < target) {
                    stat.innerText = Math.ceil(current) + '+';
                    requestAnimationFrame(updateCounter);
                } else {
                    stat.innerText = target + '+';
                }
            };
            updateCounter();
        });
    };

    // Trigger counter when hero stats are in view
    const statsContainer = document.querySelector('.hero-stats');
    if (statsContainer && stats.length > 0) {
        const statsObserver = new IntersectionObserver((entries) => {
            if (entries[0].isIntersecting && !hasCounted) {
                startCounters();
                hasCounted = true;
            }
        }, { threshold: 0.5 });

        statsObserver.observe(statsContainer);
    }
});

// Toast Notification Function
function showToast(message) {
    let toast = document.getElementById('app-toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'app-toast';
        toast.className = 'toast';
        document.body.appendChild(toast);
    }

    toast.innerHTML = message;
    toast.classList.add('show');

    setTimeout(() => {
        toast.classList.remove('show');
    }, 4000);
}

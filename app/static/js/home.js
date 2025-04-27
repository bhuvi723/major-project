// Home Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize animations
    initScrollAnimations();
    initParticles();
    createFloatingElements();
    initCounters();
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 70,
                    behavior: 'smooth'
                });
            }
        });
    });
});

// Initialize scroll animations
function initScrollAnimations() {
    const animatedElements = document.querySelectorAll('.fade-in-up, .fade-in-left, .fade-in-right, .zoom-in');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
            }
        });
    }, {
        threshold: 0.1
    });
    
    animatedElements.forEach(element => {
        observer.observe(element);
    });
}

// Initialize particle background
function initParticles() {
    if (typeof particlesJS !== 'undefined' && document.getElementById('particles-js')) {
        particlesJS('particles-js', {
            particles: {
                number: {
                    value: 80,
                    density: {
                        enable: true,
                        value_area: 800
                    }
                },
                color: {
                    value: '#ffffff'
                },
                shape: {
                    type: 'circle',
                    stroke: {
                        width: 0,
                        color: '#000000'
                    },
                    polygon: {
                        nb_sides: 5
                    }
                },
                opacity: {
                    value: 0.5,
                    random: false,
                    anim: {
                        enable: false,
                        speed: 1,
                        opacity_min: 0.1,
                        sync: false
                    }
                },
                size: {
                    value: 3,
                    random: true,
                    anim: {
                        enable: false,
                        speed: 40,
                        size_min: 0.1,
                        sync: false
                    }
                },
                line_linked: {
                    enable: true,
                    distance: 150,
                    color: '#ffffff',
                    opacity: 0.4,
                    width: 1
                },
                move: {
                    enable: true,
                    speed: 2,
                    direction: 'none',
                    random: false,
                    straight: false,
                    out_mode: 'out',
                    bounce: false,
                    attract: {
                        enable: false,
                        rotateX: 600,
                        rotateY: 1200
                    }
                }
            },
            interactivity: {
                detect_on: 'canvas',
                events: {
                    onhover: {
                        enable: true,
                        mode: 'grab'
                    },
                    onclick: {
                        enable: true,
                        mode: 'push'
                    },
                    resize: true
                },
                modes: {
                    grab: {
                        distance: 140,
                        line_linked: {
                            opacity: 1
                        }
                    },
                    bubble: {
                        distance: 400,
                        size: 40,
                        duration: 2,
                        opacity: 8,
                        speed: 3
                    },
                    repulse: {
                        distance: 200,
                        duration: 0.4
                    },
                    push: {
                        particles_nb: 4
                    },
                    remove: {
                        particles_nb: 2
                    }
                }
            },
            retina_detect: true
        });
    }
}

// Create floating elements
function createFloatingElements() {
    const container = document.querySelector('.stats-section');
    if (!container) return;
    
    const numElements = 15;
    
    for (let i = 0; i < numElements; i++) {
        const element = document.createElement('div');
        element.classList.add('floating-element');
        
        // Random size between 20px and 100px
        const size = Math.random() * 80 + 20;
        element.style.width = `${size}px`;
        element.style.height = `${size}px`;
        
        // Random position
        const posX = Math.random() * 100;
        const posY = Math.random() * 100;
        element.style.left = `${posX}%`;
        element.style.top = `${posY}%`;
        
        // Random animation duration between 10s and 30s
        const duration = Math.random() * 20 + 10;
        element.style.animation = `float ${duration}s infinite ease-in-out`;
        
        // Random delay
        const delay = Math.random() * 5;
        element.style.animationDelay = `${delay}s`;
        
        // Random opacity
        const opacity = Math.random() * 0.1 + 0.05;
        element.style.opacity = opacity;
        
        container.appendChild(element);
    }
}

// Initialize counters
function initCounters() {
    const counters = document.querySelectorAll('.stat-value');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = entry.target;
                const targetValue = parseInt(target.getAttribute('data-target'));
                const duration = 2000; // 2 seconds
                const step = targetValue / (duration / 16); // 60fps
                
                let current = 0;
                const timer = setInterval(() => {
                    current += step;
                    if (current >= targetValue) {
                        target.textContent = targetValue.toLocaleString();
                        clearInterval(timer);
                    } else {
                        target.textContent = Math.floor(current).toLocaleString();
                    }
                }, 16);
            }
        });
    }, {
        threshold: 0.5
    });
    
    counters.forEach(counter => {
        observer.observe(counter);
    });
}

// Add keyframe animation for floating elements
document.addEventListener('DOMContentLoaded', function() {
    const style = document.createElement('style');
    style.textContent = `
        @keyframes float {
            0% {
                transform: translateY(0) translateX(0) rotate(0);
            }
            25% {
                transform: translateY(-20px) translateX(10px) rotate(5deg);
            }
            50% {
                transform: translateY(0) translateX(20px) rotate(0);
            }
            75% {
                transform: translateY(20px) translateX(10px) rotate(-5deg);
            }
            100% {
                transform: translateY(0) translateX(0) rotate(0);
            }
        }
    `;
    document.head.appendChild(style);
});

// Ticker animation for stock prices
function updateTicker() {
    const tickerContent = document.querySelector('.ticker-content');
    if (!tickerContent) return;
    
    // Clone the first ticker item and append it to the end
    const firstItem = tickerContent.querySelector('.ticker-item');
    if (firstItem) {
        const clone = firstItem.cloneNode(true);
        tickerContent.appendChild(clone);
        
        // Remove the first item after animation
        setTimeout(() => {
            tickerContent.removeChild(firstItem);
        }, 1000);
    }
}

// Update ticker every 3 seconds
setInterval(updateTicker, 3000);

// Video background autoplay fix for mobile
document.addEventListener('DOMContentLoaded', function() {
    const video = document.querySelector('.video-background');
    if (video) {
        // Play video when it's loaded
        video.addEventListener('loadeddata', function() {
            video.play();
        });
        
        // Try to play video immediately
        video.play().catch(error => {
            console.log('Autoplay prevented:', error);
            
            // Add play button for mobile
            const playButton = document.createElement('button');
            playButton.classList.add('video-play-button');
            playButton.innerHTML = '<i class="fas fa-play"></i>';
            playButton.style.position = 'absolute';
            playButton.style.top = '50%';
            playButton.style.left = '50%';
            playButton.style.transform = 'translate(-50%, -50%)';
            playButton.style.zIndex = '2';
            playButton.style.background = 'rgba(0, 0, 0, 0.5)';
            playButton.style.color = 'white';
            playButton.style.border = 'none';
            playButton.style.borderRadius = '50%';
            playButton.style.width = '80px';
            playButton.style.height = '80px';
            playButton.style.fontSize = '2rem';
            playButton.style.cursor = 'pointer';
            
            const videoContainer = document.querySelector('.video-background-container');
            if (videoContainer) {
                videoContainer.appendChild(playButton);
                
                playButton.addEventListener('click', function() {
                    video.play();
                    playButton.style.display = 'none';
                });
            }
        });
    }
});

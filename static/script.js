// script.js

// Menu Toggle for Mobile
document.addEventListener('DOMContentLoaded', () => {
    const menuToggle = document.getElementById('menuToggle');
    const mainNav = document.querySelector('.main-nav');

    if (menuToggle && mainNav) {
        menuToggle.addEventListener('click', () => {
            mainNav.classList.toggle('active');
        });
    }

    // Hero Slider Functionality (index.html)
    const slider = document.querySelector('.hero-slider');
    if (slider) {
        const slides = document.querySelectorAll('.slide');
        const dots = document.querySelectorAll('.slider-dots .dot');
        const prevArrow = document.querySelector('.prev-arrow');
        const nextArrow = document.querySelector('.next-arrow');
        let currentSlide = 0;

        function updateSlide(index) {
            slides.forEach((slide, i) => {
                slide.classList.toggle('active', i === index);
            });
            dots.forEach((dot, i) => {
                dot.classList.toggle('active', i === index);
            });
        }

        nextArrow.addEventListener('click', () => {
            currentSlide = (currentSlide + 1) % slides.length;
            updateSlide(currentSlide);
        });

        prevArrow.addEventListener('click', () => {
            currentSlide = (currentSlide - 1 + slides.length) % slides.length;
            updateSlide(currentSlide);
        });

        dots.forEach((dot, index) => {
            dot.addEventListener('click', () => {
                currentSlide = index;
                updateSlide(currentSlide);
            });
        });

        // Auto-slide every 5 seconds
        setInterval(() => {
            currentSlide = (currentSlide + 1) % slides.length;
            updateSlide(currentSlide);
        }, 5000);
    }

    // Registration Form Tabs (register.html)
    document.addEventListener('DOMContentLoaded', () => {
        const menuToggle = document.getElementById('menuToggle');
        const mainNav = document.querySelector('.main-nav');
        if (menuToggle && mainNav) {
            menuToggle.addEventListener('click', () => {
                mainNav.classList.toggle('active');
            });
        }
    
        // Registration Form Tabs
        const optionTabs = document.querySelectorAll('.option-tab');
        const registerForms = document.querySelectorAll('.register-forms form');
        if (optionTabs.length && registerForms.length) {
            optionTabs.forEach(tab => {
                tab.addEventListener('click', () => {
                    optionTabs.forEach(t => t.classList.remove('active'));
                    registerForms.forEach(f => f.classList.remove('active'));
                    tab.classList.add('active');
                    document.getElementById(`${tab.dataset.type}-form`).classList.add('active');
                });
            });
        }
    });

    // Dynamic Product Loading Placeholder (index.html & products.html)
    const productGrids = document.querySelectorAll('.product-grid, .products-grid');
    productGrids.forEach(grid => {
        // Simulated product data (replace with actual API call)
        const products = [
            { name: 'Fresh Tomatoes', price: '₹40/kg', image: 'static/tomato.jpg' },
            { name: 'Organic Rice', price: '₹80/kg', image: 'static/rice.jpg' },
            { name: 'Farm Milk', price: '₹50/ltr', image: 'static/milk.jpg' },
        ];

        products.forEach(product => {
            const productCard = document.createElement('div');
            productCard.classList.add('product-card');
            productCard.innerHTML = `
                <img src="${product.image}" alt="${product.name}">
                <h3>${product.name}</h3>
                <p>${product.price}</p>
                <button class="btn primary-btn">Add to Cart</button>
            `;
            grid.appendChild(productCard);
        });
    });

    // Dynamic Farmer Loading Placeholder (index.html)
    const farmerGrid = document.querySelector('.farmer-grid');
    if (farmerGrid) {
        const farmers = [
            { name: 'Ramesh Patel', location: 'Gujarat', image: '/api/placeholder/200/200' },
            { name: 'Sita Devi', location: 'Punjab', image: '/api/placeholder/200/200' },
        ];

        farmers.forEach(farmer => {
            const farmerCard = document.createElement('div');
            farmerCard.classList.add('farmer-card');
            farmerCard.innerHTML = `
                <img src="${farmer.image}" alt="${farmer.name}">
                <h3>${farmer.name}</h3>
                <p>${farmer.location}</p>
                <a href="farmers.html" class="btn secondary-btn">View Products</a>
            `;
            farmerGrid.appendChild(farmerCard);
        });
    }

    // Price Range Slider (products.html)
    const priceRange = document.getElementById('priceRange');
    const priceValue = document.getElementById('priceValue');
    if (priceRange && priceValue) {
        priceRange.addEventListener('input', () => {
            priceValue.textContent = `₹${priceRange.value}+`;
        });
    }

    // Filter Application Placeholder (products.html)
    const applyFiltersBtn = document.getElementById('apply-filters');
    const clearFiltersBtn = document.getElementById('clear-filters');
    if (applyFiltersBtn && clearFiltersBtn) {
        applyFiltersBtn.addEventListener('click', () => {
            console.log('Filters applied'); // Replace with actual filter logic
        });

        clearFiltersBtn.addEventListener('click', () => {
            document.querySelectorAll('.checkbox-group input').forEach(input => input.checked = false);
            document.getElementById('location-filter').value = '';
            document.getElementById('sort-products').value = 'relevance';
            priceRange.value = 5000;
            priceValue.textContent = '₹5000+';
            console.log('Filters cleared'); // Replace with actual reset logic
        });
    }

    // Pagination Placeholder (products.html)
    const paginationBtns = document.querySelectorAll('.pagination-btn');
    paginationBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            paginationBtns.forEach(b => b.classList.remove('active'));
            if (!btn.querySelector('i')) { // Ignore arrow buttons
                btn.classList.add('active');
                console.log(`Page ${btn.textContent} selected`); // Replace with actual page logic
            }
        });
    });
});
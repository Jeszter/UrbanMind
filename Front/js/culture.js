const cityCoordinates = {
    kosice: { lat: 48.7164, lng: 21.2611 },
    bratislava: { lat: 48.1486, lng: 17.1077 },
    prague: { lat: 50.0755, lng: 14.4378 },
    budapest: { lat: 47.4979, lng: 19.0402 },
    warsaw: { lat: 52.2297, lng: 21.0122 },
    vienna: { lat: 48.2082, lng: 16.3738 },
    berlin: { lat: 52.52, lng: 13.405 },
    paris: { lat: 48.8566, lng: 2.3522 },
    london: { lat: 51.5074, lng: -0.1278 },
    rome: { lat: 41.9028, lng: 12.4964 }
};

const locationStatus = document.querySelector('.location-status');
const citySelect = document.getElementById('city-select');
const updateLocationBtn = document.getElementById('update-location');
const categoryFilters = document.querySelectorAll('.category-filter');
const distanceTabs = document.querySelectorAll('.distance-tab');
const chatContainer = document.getElementById('chat-container');
const chatInput = document.getElementById('chat-input');
const chatSend = document.getElementById('chat-send');

let currentFilter = 'all';
let currentDistance = 'all';
let currentCity = '';
let currentLat = null;
let currentLng = null;

function updateDistanceSection(distanceKey, sites) {
    const section = document.getElementById(`sites-${distanceKey}`);
    if (!section) return;
    if (!sites || sites.length === 0) {
        section.innerHTML = '<p style="text-align: center; padding: 40px; color: var(--color-light-text);">No cultural sites in this distance range.</p>';
        return;
    }
    section.innerHTML = '';
    sites.forEach(site => {
        const card = document.createElement('div');
        card.className = 'cultural-site-card fade-in';
        const distanceLabel = typeof site.distance_km === 'number' ? site.distance_km.toFixed(1) : site.distance_km;
        card.innerHTML = `
            <div class="cultural-site-image">
                <img src="${site.image}" alt="${site.name}">
                <div class="cultural-site-type">${site.type}</div>
                <div class="cultural-site-distance">${distanceLabel} km</div>
            </div>
            <div class="cultural-site-content">
                <div class="cultural-site-header">
                    <h3>${site.name}</h3>
                    <p>${site.description}</p>
                </div>
                <div class="cultural-site-info">
                    <div class="cultural-site-location">
                        <i class="fas fa-map-marker-alt"></i>
                        <span>${site.address || ''}</span>
                    </div>
                    <div class="cultural-site-rating">
                        <i class="fas fa-star"></i> ${site.rating || ''}
                    </div>
                </div>
                <a href="#" class="cultural-site-link">Learn More</a>
            </div>
        `;
        section.appendChild(card);
    });
}

function updateDistanceVisibility() {
    const sections = document.querySelectorAll('.distance-section');
    sections.forEach(section => {
        const distance = section.id.replace('distance-', '');
        if (currentDistance === 'all' || currentDistance === distance) {
            section.style.display = 'block';
        } else {
            section.style.display = 'none';
        }
    });
}

async function loadSitesForLocation(lat, lng) {
    currentLat = lat;
    currentLng = lng;
    try {
        locationStatus.className = 'location-status detecting';
        locationStatus.innerHTML = '<i class="fas fa-map-marker-alt"></i><span>Loading nearby cultural sites...</span>';
        const resp = await fetch('/api/culture/nearby', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                lat: lat,
                lng: lng,
                category: currentFilter === 'all' ? null : currentFilter
            })
        });
        if (!resp.ok) {
            locationStatus.className = 'location-status error';
            locationStatus.innerHTML = '<i class="fas fa-exclamation-triangle"></i><span>Server error while loading sites.</span>';
            return;
        }
        const data = await resp.json();
        if (!data || data.status !== 'success') {
            locationStatus.className = 'location-status error';
            locationStatus.innerHTML = '<i class="fas fa-exclamation-triangle"></i><span>Failed to load cultural sites.</span>';
            return;
        }
        const payload = data.data || {};
        const groups = payload.groups || {};
        const label = payload.region_label || 'your area';
        currentCity = payload.city_code || '';
        locationStatus.className = 'location-status detected';
        locationStatus.innerHTML = `<i class="fas fa-check-circle"></i><span>Showing cultural sites near: <span class="detected-location">${label}</span></span>`;
        updateDistanceSection('0-2', groups['0-2'] || []);
        updateDistanceSection('2-5', groups['2-5'] || []);
        updateDistanceSection('5-10', groups['5-10'] || []);
        updateDistanceVisibility();
    } catch (e) {
        locationStatus.className = 'location-status error';
        locationStatus.innerHTML = '<i class="fas fa-exclamation-triangle"></i><span>Connection error while loading sites.</span>';
    }
}

function detectLocation() {
    if (!navigator.geolocation) {
        locationStatus.className = 'location-status error';
        locationStatus.innerHTML = '<i class="fas fa-exclamation-triangle"></i><span>Geolocation is not supported. Please select your city manually.</span>';
        return;
    }
    navigator.geolocation.getCurrentPosition(
        pos => {
            const lat = pos.coords.latitude;
            const lng = pos.coords.longitude;
            loadSitesForLocation(lat, lng);
        },
        () => {
            locationStatus.className = 'location-status error';
            locationStatus.innerHTML = '<i class="fas fa-exclamation-triangle"></i><span>Could not detect your location. Please select your city manually.</span>';
        }
    );
}

function addMessage(message, isUser) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${isUser ? 'user' : 'bot'}`;
    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = 'message-bubble';
    bubbleDiv.textContent = message;
    messageDiv.appendChild(bubbleDiv);
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

async function handleChatInput() {
    const message = chatInput.value.trim();
    if (message === '') return;
    addMessage(message, true);
    chatInput.value = '';
    try {
        const resp = await fetch('/api/culture/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                city_code: currentCity || null,
                lat: currentLat,
                lng: currentLng
            })
        });
        if (!resp.ok) {
            addMessage("Server error while answering your question.", false);
            return;
        }
        const data = await resp.json();
        if (data && data.status === 'success' && data.reply) {
            addMessage(data.reply, false);
        } else {
            addMessage("I had trouble generating an answer. Please try again.", false);
        }
    } catch (e) {
        addMessage("Connection error while asking about city history.", false);
    }
}

updateLocationBtn.addEventListener('click', () => {
    const selectedCity = citySelect.value;
    if (!selectedCity) {
        alert('Please select a city first.');
        return;
    }
    const coords = cityCoordinates[selectedCity];
    if (!coords) {
        alert('Coordinates for this city are not available.');
        return;
    }
    currentCity = selectedCity;
    loadSitesForLocation(coords.lat, coords.lng);
});

categoryFilters.forEach(filter => {
    filter.addEventListener('click', () => {
        categoryFilters.forEach(f => f.classList.remove('active'));
        filter.classList.add('active');
        currentFilter = filter.getAttribute('data-category');
        if (currentLat != null && currentLng != null) {
            loadSitesForLocation(currentLat, currentLng);
        }
    });
});

distanceTabs.forEach(tab => {
    tab.addEventListener('click', () => {
        distanceTabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        currentDistance = tab.getAttribute('data-distance');
        updateDistanceVisibility();
    });
});

chatSend.addEventListener('click', () => {
    handleChatInput();
});

chatInput.addEventListener('keypress', e => {
    if (e.key === 'Enter') {
        handleChatInput();
    }
});

detectLocation();

const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
const navMenu = document.querySelector('.nav-menu');

if (mobileMenuBtn && navMenu) {
    mobileMenuBtn.addEventListener('click', () => {
        navMenu.classList.toggle('active');
        mobileMenuBtn.innerHTML = navMenu.classList.contains('active')
            ? '<i class="fas fa-times"></i>'
            : '<i class="fas fa-bars"></i>';
    });
}

fetch('/header.html')
    .then(response => {
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return response.text();
    })
    .then(html => {
        document.getElementById('header-container').innerHTML = html;
    })
    .catch(error => {
        document.getElementById('header-container').innerHTML =
            `<div style="color: red;">Error loading header: ${error.message}</div>`;
    });

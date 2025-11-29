const jobSitesByCountry = {
    'sk': [
        { name: 'Profesia.sk', url: 'https://www.profesia.sk', description: 'The largest job portal in Slovakia with thousands of job offers.' },
        { name: 'Praca.sme.sk', url: 'https://praca.sme.sk', description: 'Job portal from a major Slovak media company.' },
        { name: 'Kariera.zoznam.sk', url: 'https://kariera.zoznam.sk', description: 'Popular platform with diverse opportunities.' },
        { name: 'Jobs.sk', url: 'https://www.jobs.sk', description: 'Comprehensive job board for many industries.' }
    ],
    'cz': [
        { name: 'Jobs.cz', url: 'https://www.jobs.cz', description: 'The most visited job portal in the Czech Republic.' },
        { name: 'Prace.cz', url: 'https://www.prace.cz', description: 'Huge database of offers across sectors.' },
        { name: 'LMC.cz', url: 'https://www.lmc.cz', description: 'Leading recruitment agency with their own portal.' },
        { name: 'Careerjet.cz', url: 'https://www.careerjet.cz', description: 'Aggregates offers from multiple sources.' }
    ],
    'pl': [
        { name: 'Pracuj.pl', url: 'https://www.pracuj.pl', description: 'Poland’s most popular job search website.' },
        { name: 'OLX Praca', url: 'https://www.olx.pl/praca', description: 'Job offers from the classifieds platform.' },
        { name: 'Indeed Poland', url: 'https://pl.indeed.com', description: 'Global job engine with rich Polish listings.' },
        { name: 'Gowork.pl', url: 'https://www.gowork.pl', description: 'Job portal with company reviews.' }
    ],
    'hu': [
        { name: 'Profession.hu', url: 'https://www.profession.hu', description: 'Leading Hungarian job portal.' },
        { name: 'Jobline.hu', url: 'https://www.jobline.hu', description: 'Comprehensive search platform.' },
        { name: 'CVO Hungary', url: 'https://www.cvonline.hu', description: 'Popular recruitment website.' },
        { name: 'Allasok.hu', url: 'https://www.allasok.hu', description: 'Large database of Hungarian offers.' }
    ],
    'at': [
        { name: 'Karriere.at', url: 'https://www.karriere.at', description: 'Austria’s top job platform.' },
        { name: 'StepStone Austria', url: 'https://www.stepstone.at', description: 'International job portal with Austrian listings.' },
        { name: 'Monster Austria', url: 'https://www.monster.at', description: 'Global career platform for Austria.' },
        { name: 'AMS', url: 'https://www.ams.at', description: 'Official Austrian employment service.' }
    ],
    'de': [
        { name: 'StepStone Germany', url: 'https://www.stepstone.de', description: 'One of Germanys largest portals.' },
        { name: 'Indeed Germany', url: 'https://de.indeed.com', description: 'Global engine with German listings.' },
        { name: 'Monster Germany', url: 'https://www.monster.de', description: 'International job platform.' },
        { name: 'XING', url: 'https://www.xing.com', description: 'Professional network with job listings.' }
    ],
    'fr': [
        { name: 'Indeed France', url: 'https://fr.indeed.com', description: 'Popular search engine.' },
        { name: 'Monster France', url: 'https://www.monster.fr', description: 'International job platform.' },
        { name: 'APEC', url: 'https://www.apec.fr', description: 'Executive employment association.' },
        { name: 'Pôle Emploi', url: 'https://www.pole-emploi.fr', description: 'National employment agency.' }
    ],
    'uk': [
        { name: 'Indeed UK', url: 'https://www.indeed.co.uk', description: 'Most visited UK job site.' },
        { name: 'Reed.co.uk', url: 'https://www.reed.co.uk', description: 'Long-standing UK job board.' },
        { name: 'Totaljobs', url: 'https://www.totaljobs.com', description: 'Leading UK job board.' },
        { name: 'CV-Library', url: 'https://www.cv-library.co.uk', description: 'Popular site with many listings.' }
    ],
    'us': [
        { name: 'Indeed', url: 'https://www.indeed.com', description: 'World’s #1 job site.' },
        { name: 'LinkedIn Jobs', url: 'https://www.linkedin.com/jobs', description: 'Professional job marketplace.' },
        { name: 'Monster', url: 'https://www.monster.com', description: 'Global pioneer in job listings.' },
        { name: 'CareerBuilder', url: 'https://www.careerbuilder.com', description: 'Advanced job board.' }
    ],
    'ca': [
        { name: 'Indeed Canada', url: 'https://ca.indeed.com', description: 'Top engine for Canada.' },
        { name: 'Workopolis', url: 'https://www.workopolis.com', description: 'Popular Canadian job board.' },
        { name: 'Monster Canada', url: 'https://www.monster.ca', description: 'International platform.' },
        { name: 'Eluta.ca', url: 'https://www.eluta.ca', description: 'Job search with employer reviews.' }
    ]
};

const countryNames = {
    'sk': 'Slovakia',
    'cz': 'Czech Republic',
    'pl': 'Poland',
    'hu': 'Hungary',
    'at': 'Austria',
    'de': 'Germany',
    'fr': 'France',
    'uk': 'United Kingdom',
    'us': 'United States',
    'ca': 'Canada'
};

const locationStatus = document.querySelector('.location-status');
const countrySelect = document.getElementById('country-select');
const updateLocationBtn = document.getElementById('update-location');
const jobSitesGrid = document.querySelector('.job-sites-grid');

function localCacheLoad() {
    try {
        return JSON.parse(localStorage.getItem('job_cache') || '{}');
    } catch {
        return {};
    }
}

function localCacheSave(key, data) {
    const cache = localCacheLoad();
    cache[key] = data;
    localStorage.setItem('job_cache', JSON.stringify(cache));
}

function pushHistory(entry) {
    let log = [];
    try {
        log = JSON.parse(localStorage.getItem('job_history') || '[]');
    } catch {
        log = [];
    }
    log.push(entry);
    if (log.length > 10) log.shift();
    localStorage.setItem('job_history', JSON.stringify(log));
}

function setStatusDetecting() {
    locationStatus.className = 'location-status detecting';
    locationStatus.innerHTML = `
        <i class="fas fa-map-marker-alt"></i>
        <span>Detecting your location...</span>
    `;
}

function setStatusForCountry(code, nameText) {
    locationStatus.className = 'location-status detected';
    locationStatus.innerHTML = `
        <i class="fas fa-check-circle"></i>
        <span>Showing job sites for: <span class="detected-location">${nameText}</span></span>
    `;
}

function setStatusManualNeeded() {
    locationStatus.className = 'location-status manual';
    locationStatus.innerHTML = `
        <i class="fas fa-map-marker-alt"></i>
        <span>Location unavailable. Please select your country manually.</span>
    `;
}

function renderJobSites(sites, countryCode) {
    jobSitesGrid.innerHTML = '';
    if (!sites || sites.length === 0) {
        jobSitesGrid.innerHTML = '<p>No job sites available for this country.</p>';
        return;
    }
    const countryName = countryNames[countryCode] || 'Selected country';
    setStatusForCountry(countryCode, countryName);
    sites.forEach(site => {
        const jobSiteCard = document.createElement('div');
        jobSiteCard.className = 'job-site-card fade-in';
        jobSiteCard.innerHTML = `
            <div class="job-site-logo"><i class="fas fa-briefcase"></i></div>
            <h3>${site.name}</h3>
            <p>${site.description || ''}</p>
            <a href="${site.url}" target="_blank" class="job-site-link">Visit Site <i class="fas fa-external-link-alt"></i></a>
        `;
        jobSitesGrid.appendChild(jobSiteCard);
    });
}

async function fetchFreshData(payload, cacheKey) {
    try {
        const resp = await fetch('/api/get_job_sites', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!resp.ok) return null;
        const data = await resp.json();
        if (!data || !Array.isArray(data.sites)) return null;
        localCacheSave(cacheKey, data);
        pushHistory({ when: new Date().toISOString(), location: cacheKey, sites: data.sites.map(s => s.name) });
        return data;
    } catch {
        return null;
    }
}

async function requestJobSites(payload) {
    const cacheKey = payload.country_code
        ? payload.country_code.toLowerCase()
        : payload.latitude + ',' + payload.longitude;

    const cache = localCacheLoad();
    const cached = cache[cacheKey];

    if (cached) {
        renderJobSites(cached.sites, cached.country_code);
        fetchFreshData(payload, cacheKey).then(newData => {
            if (newData && JSON.stringify(newData.sites) !== JSON.stringify(cached.sites)) {
                renderJobSites(newData.sites, newData.country_code);
            }
        });
        return;
    }

    const fresh = await fetchFreshData(payload, cacheKey);
    if (fresh) {
        renderJobSites(fresh.sites, fresh.country_code);
        return;
    }

    if (payload.country_code) {
        const fallback = jobSitesByCountry[payload.country_code] || [];
        renderJobSites(fallback, payload.country_code);
        return;
    }

    setStatusManualNeeded();
}

function detectLocation() {
    setStatusDetecting();
    if (!navigator.geolocation) {
        setStatusManualNeeded();
        return;
    }
    navigator.geolocation.getCurrentPosition(
        pos => {
            const payload = {
                latitude: pos.coords.latitude,
                longitude: pos.coords.longitude
            };
            requestJobSites(payload);
        },
        () => setStatusManualNeeded()
    );
}

updateLocationBtn.addEventListener('click', () => {
    const selectedCountry = countrySelect.value;
    if (selectedCountry) {
        requestJobSites({ country_code: selectedCountry });
    } else {
        alert('Please select a country first.');
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

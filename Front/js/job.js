const jobSitesByCountry = {
    'sk': [
        { name: 'Profesia.sk', url: 'https://www.profesia.sk', description: 'The largest job portal in Slovakia with thousands of job offers.' },
        { name: 'Praca.sme.sk', url: 'https://praca.sme.sk', description: 'Job portal from one of the largest Slovak media companies.' },
        { name: 'Kariera.zoznam.sk', url: 'https://kariera.zoznam.sk', description: 'Popular job search platform with diverse opportunities.' },
        { name: 'Jobs.sk', url: 'https://www.jobs.sk', description: 'Comprehensive job board for various industries in Slovakia.' }
    ],
    'cz': [
        { name: 'Jobs.cz', url: 'https://www.jobs.cz', description: 'The most visited job portal in the Czech Republic.' },
        { name: 'Prace.cz', url: 'https://www.prace.cz', description: 'Extensive database of job offers across all sectors.' },
        { name: 'LMC.cz', url: 'https://www.lmc.cz', description: 'Leading recruitment agency with their own job portal.' },
        { name: 'Careerjet.cz', url: 'https://www.careerjet.cz', description: 'Job search engine aggregating offers from multiple sources.' }
    ],
    'pl': [
        { name: 'Pracuj.pl', url: 'https://www.pracuj.pl', description: 'Poland\'s most popular job search website.' },
        { name: 'OLX Praca', url: 'https://www.olx.pl/praca', description: 'Job offers on the popular classifieds platform.' },
        { name: 'Indeed Poland', url: 'https://pl.indeed.com', description: 'Global job search engine with extensive Polish listings.' },
        { name: 'Gowork.pl', url: 'https://www.gowork.pl', description: 'Job portal with company reviews from employees.' }
    ],
    'hu': [
        { name: 'Profession.hu', url: 'https://www.profession.hu', description: 'Leading Hungarian job portal with diverse opportunities.' },
        { name: 'Jobline.hu', url: 'https://www.jobline.hu', description: 'Comprehensive job search platform in Hungary.' },
        { name: 'CVO Hungary', url: 'https://www.cvonline.hu', description: 'Popular recruitment website with various job categories.' },
        { name: 'Allasok.hu', url: 'https://www.allasok.hu', description: 'Extensive database of job offers across Hungary.' }
    ],
    'at': [
        { name: 'Karriere.at', url: 'https://www.karriere.at', description: 'Austria\'s leading job platform with thousands of offers.' },
        { name: 'StepStone Austria', url: 'https://www.stepstone.at', description: 'International job portal with strong Austrian presence.' },
        { name: 'Monster Austria', url: 'https://www.monster.at', description: 'Global career platform with Austrian job listings.' },
        { name: 'AMS', url: 'https://www.ams.at', description: 'Austrian Public Employment Service official job portal.' }
    ],
    'de': [
        { name: 'StepStone Germany', url: 'https://www.stepstone.de', description: 'One of Germany\'s largest job portals.' },
        { name: 'Indeed Germany', url: 'https://de.indeed.com', description: 'Global job search engine with extensive German listings.' },
        { name: 'Monster Germany', url: 'https://www.monster.de', description: 'International career platform popular in Germany.' },
        { name: 'XING', url: 'https://www.xing.com', description: 'Professional network with job opportunities in German-speaking countries.' }
    ],
    'fr': [
        { name: 'Indeed France', url: 'https://fr.indeed.com', description: 'Popular job search engine with French listings.' },
        { name: 'Monster France', url: 'https://www.monster.fr', description: 'International career platform with French job offers.' },
        { name: 'APEC', url: 'https://www.apec.fr', description: 'French association for executives employment.' },
        { name: 'Pôle Emploi', url: 'https://www.pole-emploi.fr', description: 'French government employment agency.' }
    ],
    'uk': [
        { name: 'Indeed UK', url: 'https://www.indeed.co.uk', description: 'Most visited job site in the United Kingdom.' },
        { name: 'Reed.co.uk', url: 'https://www.reed.co.uk', description: 'Long-standing UK job board with diverse opportunities.' },
        { name: 'Totaljobs', url: 'https://www.totaljobs.com', description: 'One of the UK\'s leading job boards.' },
        { name: 'CV-Library', url: 'https://www.cv-library.co.uk', description: 'Popular UK job site with extensive listings.' }
    ],
    'us': [
        { name: 'Indeed', url: 'https://www.indeed.com', description: 'World\'s #1 job site with millions of listings.' },
        { name: 'LinkedIn Jobs', url: 'https://www.linkedin.com/jobs', description: 'Professional network with extensive job opportunities.' },
        { name: 'Monster', url: 'https://www.monster.com', description: 'Pioneer in online career services with global reach.' },
        { name: 'CareerBuilder', url: 'https://www.careerbuilder.com', description: 'Leading job board with advanced search features.' }
    ],
    'ca': [
        { name: 'Indeed Canada', url: 'https://ca.indeed.com', description: 'Most popular job search engine in Canada.' },
        { name: 'Workopolis', url: 'https://www.workopolis.com', description: 'Leading Canadian job board with diverse opportunities.' },
        { name: 'Monster Canada', url: 'https://www.monster.ca', description: 'International career platform with Canadian focus.' },
        { name: 'Eluta.ca', url: 'https://www.eluta.ca', description: 'Canadian job search engine with employer reviews.' }
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
        jobSitesGrid.innerHTML = '<p>No job sites available for this country. Please try another country.</p>';
        return;
    }

    const countryName = countryNames[countryCode] || 'Selected country';
    setStatusForCountry(countryCode, countryName);

    sites.forEach(site => {
        const jobSiteCard = document.createElement('div');
        jobSiteCard.className = 'job-site-card fade-in';
        jobSiteCard.innerHTML = `
            <div class="job-site-logo">
                <i class="fas fa-briefcase"></i>
            </div>
            <h3>${site.name}</h3>
            <p>${site.description || ''}</p>
            <a href="${site.url}" target="_blank" class="job-site-link">Visit Site <i class="fas fa-external-link-alt"></i></a>
        `;
        jobSitesGrid.appendChild(jobSiteCard);
    });
}

async function fetchFromBackend(payload) {
    try {
        const resp = await fetch('/api/get_job_sites', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!resp.ok) throw new Error('Bad response');
        const data = await resp.json();
        if (data && Array.isArray(data.sites) && data.sites.length > 0) {
            const code = (data.country_code || '').toLowerCase();
            if (code && countrySelect) countrySelect.value = code;
            setStatusForCountry(code || 'unknown', data.country_name || 'Your region');
            jobSitesGrid.innerHTML = '';
            data.sites.forEach(site => {
                const jobSiteCard = document.createElement('div');
                jobSiteCard.className = 'job-site-card fade-in';
                jobSiteCard.innerHTML = `
                    <div class="job-site-logo">
                        <i class="fas fa-briefcase"></i>
                    </div>
                    <h3>${site.name}</h3>
                    <p>${site.description || ''}</p>
                    <a href="${site.url}" target="_blank" class="job-site-link">Visit Site <i class="fas fa-external-link-alt"></i></a>
                `;
                jobSitesGrid.appendChild(jobSiteCard);
            });
            return true;
        }
        return false;
    } catch (e) {
        return false;
    }
}

async function updateJobSites(countryCode) {
    if (!countryCode) return;

    const backendOk = await fetchFromBackend({ country_code: countryCode });
    if (backendOk) return;

    const jobSites = jobSitesByCountry[countryCode] || [];
    renderJobSites(jobSites, countryCode);
}

function detectLocation() {
    setStatusDetecting();

    if (!navigator.geolocation) {
        setStatusManualNeeded();
        return;
    }

    navigator.geolocation.getCurrentPosition(
        async position => {
            const payload = {
                latitude: position.coords.latitude,
                longitude: position.coords.longitude
            };
            const ok = await fetchFromBackend(payload);
            if (!ok) setStatusManualNeeded();
        },
        () => {
            setStatusManualNeeded();
        }
    );
}

updateLocationBtn.addEventListener('click', () => {
    const selectedCountry = countrySelect.value;
    if (selectedCountry) {
        updateJobSites(selectedCountry);
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

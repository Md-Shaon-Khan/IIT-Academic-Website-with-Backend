const API_BASE = "http://127.0.0.1:8000";

document.addEventListener("DOMContentLoaded", () => {
    fetch('navbar.html')
        .then(res => res.text())
        .then(data => {
            document.getElementById('navbar-placeholder').innerHTML = data;

            const searchInput = document.getElementById('globalSearchInput');
            if (searchInput) {
                searchInput.addEventListener('keypress', function (e) {
                    if (e.key === 'Enter') performGlobalSearch();
                });
            }
        });

    fetch('footer.html')
        .then(res => res.text())
        .then(data => document.getElementById('footer-placeholder').innerHTML = data);

    document.getElementById('batch-label').innerText = "All Batches";
    loadAllProjects();
});

async function loadAllProjects() {
    const container = document.getElementById("projects-container");
    container.innerHTML = `<div class="text-center py-5"><div class="spinner-border" style="color: #11446c;"></div></div>`;

    try {
        const res = await fetch(`${API_BASE}/get-all-projects/`);
        const projects = await res.json();

        if (!projects || projects.length === 0) {
            container.innerHTML = `<div class="col-12 text-center py-5"><h3 style="color: #11446c;">No projects found.</h3></div>`;
            return;
        }

        // Group projects by batch
        const grouped = {};
        projects.forEach(p => {
            if (!grouped[p.batch]) grouped[p.batch] = [];
            grouped[p.batch].push(p);
        });

        // Sort batches in descending order (latest first)
        const sortedBatches = Object.keys(grouped).sort((a, b) => b - a);

        container.innerHTML = "";

        sortedBatches.forEach(batch => {
            // Batch heading
            container.innerHTML += `
                <div class="col-12 mt-4 mb-2">
                    <h4 style="color: #11446c; font-weight: 700; border-left: 4px solid #11446c; padding-left: 12px;">
                        Batch ${batch}
                        <span class="badge ms-2" style="background:#11446c; font-size:13px;">${grouped[batch].length} project${grouped[batch].length > 1 ? 's' : ''}</span>
                    </h4>
                    <hr style="border-color: rgba(17,68,108,0.2);">
                </div>`;

            // Projects under this batch
            grouped[batch].forEach(p => {
                const imgPath = p.image_path.replace(/\\/g, '/');
                container.innerHTML += `
                    <div class="col-md-6 mb-4" id="project-card-${p.id}">
                        <div class="card h-100 shadow-sm border-0 project-card" style="border-radius: 15px; overflow: hidden;">
                            <div class="row g-0 h-100">
                                <div class="col-7 p-4 d-flex flex-column">
                                    <h5 class="fw-bold" style="color: #11446c !important;">${p.project_name}</h5>
                                    <p class="text-muted small mb-1"><strong>Batch:</strong> ${p.batch}</p>
                                    <p class="text-muted small mb-3">${p.introduction.substring(0, 100)}...</p>
                                    <div class="mt-auto">
                                        <p class="small mb-1 text-secondary"><strong>Supervisor:</strong> ${p.supervisor}</p>
                                        <div class="d-flex gap-2 mt-2">
                                            <a href="project_details.html?id=${p.id}" class="btn btn-primary btn-sm px-4" style="border-radius: 20px; background-color: #11446c; border: none;">Details</a>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-5">
                                    <img src="${API_BASE}/${imgPath}" class="img-fluid h-100 w-100" style="object-fit: cover; min-height: 220px;">
                                </div>
                            </div>
                        </div>
                    </div>`;
            });
        });

    } catch (e) {
        console.error(e);
        container.innerHTML = `<div class="alert alert-danger text-center">Failed to load projects.</div>`;
    }
}

async function performGlobalSearch() {
    const query = document.getElementById('globalSearchInput').value;
    if (!query.trim()) return;

    const container = document.getElementById("projects-container");
    const label = document.getElementById('batch-label');

    label.innerText = `Search Results for: "${query}"`;
    container.innerHTML = `<div class="text-center py-5"><div class="spinner-border" style="color: #11446c;"></div></div>`;

    try {
        const res = await fetch(`${API_BASE}/search-projects/?query=${encodeURIComponent(query)}`);
        const projects = await res.json();

        if (!projects || projects.length === 0) {
            container.innerHTML = `<div class="col-12 text-center py-5"><h3 style="color: #11446c;">No projects found.</h3></div>`;
            return;
        }

        container.innerHTML = "";
        projects.forEach(p => {
            const imgPath = p.image_path.replace(/\\/g, '/');
            container.innerHTML += `
                <div class="col-md-6 mb-4">
                    <div class="card h-100 shadow-sm border-0 project-card" style="border-radius: 15px; overflow: hidden;">
                        <div class="row g-0 h-100">
                            <div class="col-7 p-4 d-flex flex-column">
                                <h5 class="fw-bold" style="color: #11446c !important;">${p.project_name}</h5>
                                <p class="text-muted small mb-1"><strong>Batch:</strong> ${p.batch}</p>
                                <p class="text-muted small mb-3">${p.introduction.substring(0, 100)}...</p>
                                <div class="mt-auto">
                                    <p class="small mb-1 text-secondary"><strong>Supervisor:</strong> ${p.supervisor}</p>
                                    <div class="d-flex gap-2 mt-2">
                                        <a href="project_details.html?id=${p.id}" class="btn btn-primary btn-sm px-4" style="border-radius: 20px; background-color: #11446c; border: none;">Details</a>
                                    </div>
                                </div>
                            </div>
                            <div class="col-5">
                                <img src="${API_BASE}/${imgPath}" class="img-fluid h-100 w-100" style="object-fit: cover; min-height: 220px;">
                            </div>
                        </div>
                    </div>
                </div>`;
        });

    } catch (error) {
        console.error("Search Error:", error);
    }
}
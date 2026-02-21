document.addEventListener("DOMContentLoaded", () => {
    fetch('navbar.html').then(res => res.text()).then(data => document.getElementById('navbar-placeholder').innerHTML = data);
    fetch('footer.html').then(res => res.text()).then(data => document.getElementById('footer-placeholder').innerHTML = data);

    const urlParams = new URLSearchParams(window.location.search);
    let batchId = urlParams.get('batch');

    if (!batchId) {
        document.getElementById('projects-container').innerHTML = `<div class="col-12 text-center py-5"><h3>Please select a batch from the menu above.</h3></div>`;
        document.getElementById('batch-label').innerText = "Select Batch";
        return;
    }

    document.getElementById('batch-label').innerText = `Batch-${batchId}`;
    loadProjects(batchId);
});

async function loadProjects(batch) {
    const API_BASE = "http://127.0.0.1:8000";
    const container = document.getElementById("projects-container");
    
    try {
        const res = await fetch(`${API_BASE}/get-projects/${batch}`);
        const projects = await res.json();
        container.innerHTML = "";

        projects.forEach(p => {
            const imgPath = p.image_path.replace(/\\/g, '/');
            container.innerHTML += `
                <div class="col-md-6">
                    <div class="card h-100 shadow-sm border-0">
                        <div class="row g-0 h-100">
                            <div class="col-7 p-4">
                                <h5 class="fw-bold">${p.project_name}</h5>
                                <p class="text-muted small">${p.introduction}</p>
                                <a href="project_details.html?id=${p.id}" class="btn btn-primary btn-sm mt-3">View Full Details</a>
                            </div>
                            <div class="col-5">
                                <img src="${API_BASE}/${imgPath}" class="img-fluid h-100" style="object-fit: cover;">
                            </div>
                        </div>
                    </div>
                </div>`;
        });
    } catch (e) { console.error(e); }
}
document.addEventListener("DOMContentLoaded", () => {
    // ১. Navbar এবং Footer লোড করা
    fetch('navbar.html')
        .then(res => res.text())
        .then(data => {
            document.getElementById('navbar-placeholder').innerHTML = data;
            
            const searchInput = document.getElementById('globalSearchInput');
            if (searchInput) {
                searchInput.addEventListener('keypress', function (e) {
                    if (e.key === 'Enter') {
                        performGlobalSearch();
                    }
                });
            }
        });

    fetch('footer.html')
        .then(res => res.text())
        .then(data => document.getElementById('footer-placeholder').innerHTML = data);

    const urlParams = new URLSearchParams(window.location.search);
    let batchId = urlParams.get('batch');

    if (!batchId) {
        document.getElementById('projects-container').innerHTML = `
            <div class="col-12 text-center py-5">
                <h3>Please select a batch or use the search bar to find projects.</h3>
            </div>`;
        document.getElementById('batch-label').innerText = "Select Batch";
        return;
    }

    document.getElementById('batch-label').innerText = `Batch-${batchId}`;
    loadProjects(batchId);
});

async function loadProjects(batch) {
    const API_BASE = "http://127.0.0.1:8000";
    const container = document.getElementById("projects-container");
    container.innerHTML = `<div class="text-center py-5"><div class="spinner-border text-primary"></div></div>`;
    
    try {
        const res = await fetch(`${API_BASE}/get-projects/${batch}`);
        const projects = await res.json();
        displayProjects(projects);
    } catch (e) { 
        console.error(e);
        container.innerHTML = `<div class="alert alert-danger text-center">Failed to load projects.</div>`;
    }
}

async function performGlobalSearch() {
    const query = document.getElementById('globalSearchInput').value;
    if (!query.trim()) return;

    const API_BASE = "http://127.0.0.1:8000";
    const container = document.getElementById("projects-container");
    const label = document.getElementById('batch-label');

    label.innerText = `Search Results for: "${query}"`;
    container.innerHTML = `<div class="text-center py-5"><div class="spinner-border text-primary"></div></div>`;

    try {
        const res = await fetch(`${API_BASE}/search-projects/?query=${encodeURIComponent(query)}`);
        const projects = await res.json();
        displayProjects(projects);
    } catch (error) {
        console.error("Search Error:", error);
    }
}

// কার্ড রেন্ডার করার জন্য একটি মাত্র ফাংশন
function displayProjects(projects) {
    const container = document.getElementById("projects-container");
    const API_BASE = "http://127.0.0.1:8000";
    container.innerHTML = "";

    if (!projects || projects.length === 0) {
        container.innerHTML = `<div class="col-12 text-center py-5"><h3>No projects found.</h3></div>`;
        return;
    }

    projects.forEach(p => {
        const imgPath = p.image_path.replace(/\\/g, '/');
        
        container.innerHTML += `
            <div class="col-md-6 mb-4" id="project-card-${p.id}">
                <div class="card h-100 shadow-sm border-0 project-card" style="border-radius: 15px; overflow: hidden;">
                    <div class="row g-0 h-100">
                        <div class="col-7 p-4 d-flex flex-column">
                            <h5 class="fw-bold text-primary">${p.project_name}</h5>
                            <p class="text-muted small mb-1"><strong>Batch:</strong> ${p.batch}</p>
                            <p class="text-muted small mb-3">${p.introduction.substring(0, 100)}...</p>
                            
                            <div class="mt-auto">
                                <p class="small mb-1 text-secondary"><strong>Supervisor:</strong> ${p.supervisor}</p>
                                <div class="d-flex gap-2 mt-2">
                                    <a href="project_details.html?id=${p.id}" class="btn btn-primary btn-sm px-3" style="border-radius: 20px;">Details</a>
                                    <button onclick="confirmDelete(${p.id})" class="btn btn-outline-danger btn-sm px-3" style="border-radius: 20px;">
                                        <i class="fa fa-trash"></i> Delete
                                    </button>
                                </div>
                            </div>
                        </div>
                        <div class="col-5">
                            <img src="${API_BASE}/${imgPath}" class="img-fluid h-100 w-100" style="object-fit: cover; min-height: 200px;">
                        </div>
                    </div>
                </div>
            </div>`;
    });
}

async function confirmDelete(projectId) {
    const password = prompt("Admin access required. Enter Password to delete:");
    
    if (password === "iitju123") {
        if (confirm("Are you sure you want to delete this project?")) {
            const API_BASE = "http://127.0.0.1:8000";
            try {
                const res = await fetch(`${API_BASE}/delete-project/${projectId}`, { method: 'DELETE' });
                if (res.ok) {
                    alert("Project deleted successfully!");
                    document.getElementById(`project-card-${projectId}`).remove(); 
                } else {
                    alert("Failed to delete.");
                }
            } catch (e) {
                console.error("Delete Error:", e);
            }
        }
    } else if (password !== null) {
        alert("Incorrect Password!");
    }
}
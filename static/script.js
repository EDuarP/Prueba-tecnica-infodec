function showSectionFromPath() {
            const path = window.location.pathname.replace("/", "") || "subirarchivos";
            document.querySelectorAll("section").forEach(sec => sec.classList.remove("active"));
            const target = document.getElementById(path);
            if (target) target.classList.add("active");
        }

        // Ejecuta al cargar
        showSectionFromPath();

        // Captura clicks para evitar recargar el HTML
        document.querySelectorAll("a").forEach(a => {
            a.addEventListener("click", function(e) {
                e.preventDefault();
                const href = this.getAttribute("href");
                window.history.pushState({}, "", href);
                showSectionFromPath();
            });
        });

        // Cuando el usuario usa el botón "atrás/

function showSection(sectionName, el) {


    // Hide all sections
    const sections = document.querySelectorAll('.content-section');
    sections.forEach(section => {
        section.style.display = 'none';
    });
    
    // Show selected section
    document.getElementById(sectionName).style.display = 'block';
    
    // Show/hide sidebar based on section
    const sidebarContainer = document.getElementById('sidebar-container');
    const navegationBar = document.getElementById('navegation-bar')
    const mainContentContainer = document.getElementById('main-content-container');
    
    if (sectionName === 'home') {
        sidebarContainer.style.display = 'none';
        navegationBar.style.display = 'none'
    } else {
        sidebarContainer.style.display = 'block';
        navegationBar.style.display = 'block'
    }
    
    // Update sidebar active state
    const sidebarItems = document.querySelectorAll('.sidebar-item');
    sidebarItems.forEach(item => {
        item.classList.remove('active');
    }); 

    // Marcar el actual como activo
    if (sectionName != 'home') {
        el.classList.add('active')

    }
}

// Feature cards click handlers
document.addEventListener('DOMContentLoaded', function() {
    const cards = document.querySelectorAll('.feature-card');
    cards.forEach(card => {
        card.addEventListener('click', function() {
            const title = this.querySelector('.feature-title').textContent;
            if (title.includes('Ventas')) {
                window.history.pushState({}, "", "/subirarchivos");
                showSection('subirarchivos', document.querySelector('.boton_ventas'));
            } else if (title.includes('Vendedores')) {
                window.history.pushState({}, "", "/vendedores");
                showSection('vendedores', document.querySelector('.boton_vendedores'));
            } else if (title.includes('Datos')) {
                window.history.pushState({}, "", "/datos");
                showSection('datos', document.querySelector('.boton_datos'));
            } else if (title.includes('Dashboard')) {
                window.history.pushState({}, "", "/dashboard");
                showSection('dashboard', document.querySelector('.boton_dashboard'));
            }
        });
    });
    
    // Initialize home view (no sidebar)
    showSection('home', this);
    window.history.pushState({}, "", "/home");
});

// File upload
const uploadArea = document.querySelector('.upload-area');
const boton_ventas_csv = document.querySelector('.boton_ventas_csv')
const boton_devoluciones_csv = document.querySelector('.boton_devoluciones_csv')
var flag_file = 0
var file = ""

if (uploadArea) {
    uploadArea.addEventListener('click', function() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.csv';
        input.onchange = function(e) {
            file = e.target.files[0];
            if (file) {
                window.history.pushState({}, "", "/subirarchivos/cargado");
                uploadArea.innerHTML = `
                    <i class="fas fa-check-circle fa-3x text-success mb-3"></i>
                    <p class="mb-0 text-success">Archivo "${file.name}" cargado exitosamente</p>
                `;
                flag_file = 1;
                showSection("subirarchivos", document.querySelector(".boton_ventas"));
            }
        };
        input.click();
    });
}

boton_ventas_csv.addEventListener("click", async () => {
    if (flag_file != 1) {
        alert("Primero debes cargar un archivo");
        return;
    }

    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch("/upload_csv/", {
        method: "POST",
        body: formData
    });

    const data = await res.json();
    if (res.ok) {
        alert(data.message);
    } else {
        alert("Error: " + data.detail);
    }
});

boton_devoluciones_csv.addEventListener("click", async () => {
    if (flag_file != 1) {
        alert("Primero debes cargar un archivo");
        return;
    }

    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch("/upload_csv/", {
        method: "POST",
        body: formData
    });

    const data = await res.json();
    if (res.ok) {
        alert(data.message);
    } else {
        alert("Error: " + data.detail);
    }
});
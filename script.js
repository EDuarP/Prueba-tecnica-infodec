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
                showSection('subirarchivos', document.querySelector('.boton_ventas'));
            } else if (title.includes('Vendedores')) {
                showSection('vendedores', document.querySelector('.boton_vendedores'));
            } else if (title.includes('Datos')) {
                showSection('datos', document.querySelector('.boton_datos'));
            } else if (title.includes('Dashboard')) {
                showSection('dashboard', document.querySelector('.boton_dashboard'));
            }
        });
    });
    
    // Initialize home view (no sidebar)
    showSection('home', this);
});

// File upload simulation
const uploadArea = document.querySelector('.upload-area');
if (uploadArea) {
    uploadArea.addEventListener('click', function() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.csv';
        input.onchange = function(e) {
            const file = e.target.files[0];
            if (file) {
                uploadArea.innerHTML = `
                    <i class="fas fa-check-circle fa-3x text-success mb-3"></i>
                    <p class="mb-0 text-success">Archivo "${file.name}" cargado exitosamente</p>
                `;
            }
        };
        input.click();
    });
}
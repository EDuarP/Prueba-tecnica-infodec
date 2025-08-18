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

document.addEventListener("DOMContentLoaded", function () {
    fetch("/api/vendedores_nombre")
        .then(res => res.json())
        .then(data => {
            const select1 = document.getElementById("consulta_vendedores_select");
            const select2 = document.getElementById("vendedorSelect2");
            data.forEach(v => {
                const option1 = document.createElement("option");
                option1.value = v.id;
                option1.textContent = v.nombre;
                select1.appendChild(option1);

                const option2 = document.createElement("option");
                option2.value = v.id;
                option2.textContent = v.nombre;
                select2.appendChild(option2);
            });
        })
        .catch(error => console.error("Error cargando vendedores:", error));

    fetch("/api/meses")
        .then(res => res.json())
        .then(data => {
            data.forEach(m => {
                const option = document.createElement("option");
                option.value = m.mes;
                option.textContent = m.mes;
                document.getElementById("mesSelect").appendChild(option);
            });
        })
        .catch(err => console.error("Error cargando meses:", err));
    
    fetch("/api/referencias")
        .then(res => res.json())
        .then(data => {
            data.forEach(r => {
                const option = document.createElement("option");
                option.value = r.referencias;
                option.textContent = r.referencias;
                document.getElementById("ReferenciaSelect").appendChild(option);
            });
        })
        .catch(err => console.error("Error cargando referencias:", err));

    const vendedorId = document.getElementById("consulta_vendedores_select").value;
    const mes = document.getElementById("mesSelect").value;
    cargarEstadisticas(vendedorId, mes);
});

function cargarEstadisticas(vendedorId, mes) {
    const url = new URL("/api/estadisticas", window.location.origin);
    if (vendedorId) url.searchParams.append("vendedor_id", vendedorId);
    if (mes) url.searchParams.append("mes", mes);

    fetch(url)
        .then(res => res.json())
        .then(data => {
            document.getElementById("totalVentas").textContent = data.total_ventas.toLocaleString();
            document.getElementById("comisionCalculada").textContent = data.comision_calculada.toLocaleString();
            document.getElementById("Bono").textContent = data.bono.toLocaleString();
            document.getElementById("Penalizacion").textContent = data.penalizacion.toLocaleString();
            document.getElementById("comisionFinal").textContent = data.comision_final.toLocaleString();
        })
        .catch(err => console.error("Error cargando estadísticas:", err));
}

// Eventos de cambio
document.getElementById("consulta_vendedores_select").addEventListener("change", () => {
    const vendedorId = document.getElementById("consulta_vendedores_select").value;
    const mes = document.getElementById("mesSelect").value;
    cargarEstadisticas(vendedorId, mes);
});

document.getElementById("mesSelect").addEventListener("change", () => {
    const vendedorId = document.getElementById("consulta_vendedores_select").value;
    const mes = document.getElementById("mesSelect").value;
    cargarEstadisticas(vendedorId, mes);
});

document.getElementById("boton_pdf").addEventListener("click", () => {
    const vendedorId = document.getElementById("consulta_vendedores_select").value || null;
    const mes = document.getElementById("mesSelect").value || null;

    const datos = {
        "Total de ventas": parseInt(document.getElementById("totalVentas").textContent.replace(/\./g, "")),
        "Comisión calculada": parseInt(document.getElementById("comisionCalculada").textContent.replace(/\./g, "")),
        "Bono": parseInt(document.getElementById("Bono").textContent.replace(/\./g, "")),
        "Penalización": parseInt(document.getElementById("Penalizacion").textContent.replace(/\./g, "")),
        "Comisión final a pagar": parseInt(document.getElementById("comisionFinal").textContent.replace(/\./g, ""))
    };

    fetch("/api/generar_pdf", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ datos, vendedor: vendedorId, mes })
    })
    .then(response => response.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "reporte.pdf";
        document.body.appendChild(a);
        a.click();
        a.remove();
    });
});

document.getElementById("boton_guardar_datos").addEventListener("click", () => {
    const vendedorId = document.getElementById("vendedorSelect2").value || null;
    const Referencia = document.getElementById("ReferenciaSelect").value || null;
    const Cantidad = document.getElementById("cantidad_ingresada").value || null;
    const Operacion = document.getElementById("operacionSelect").value || null;
    const Motivo = document.getElementById("motivoInput").value || null;

    const campos = [
        { valor: vendedorId, mensaje: "Error: No se ha seleccionado un vendedor" },
        { valor: Referencia, mensaje: "Error: No se ha seleccionado una Referencia" },
        { valor: Cantidad, mensaje: "Error: No se ha seleccionado una Cantidad" }
    ];

    for (const campo of campos) {
        if (!campo.valor) {
            alert(campo.mensaje);
            return;
        }
    }

    const datos = {
        "vendedorId": vendedorId,
        "Referencia": Referencia,
        "Cantidad": Cantidad,
        "Operacion": Operacion,
        "Motivo": Motivo
    };

    fetch("/api/guardar_datos", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({datos})
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Error al guardar los datos");
        }
        return response.json();
    })
    .then(data => {
        alert("Datos guardados correctamente");

        // Limpia los campos después de guardar
        document.getElementById("vendedorSelect2").value = null;
        document.getElementById("ReferenciaSelect").value = null;
        document.getElementById("cantidad_ingresada").value = null;
        document.getElementById("operacionSelect").value = null;
        document.getElementById("motivoInput").value = null;
    })
    .catch(error => {
        console.error("Error:", error);
        alert("No se pudo guardar la información");
    });
});


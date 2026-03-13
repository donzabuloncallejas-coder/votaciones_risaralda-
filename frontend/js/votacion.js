const API_URL = 'http://localhost:5000/api';

// Variables globales
let votanteCedula = '';
let votanteNombre = '';
let candidatoSeleccionado = null;

// Verificar sesión al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    votanteCedula = sessionStorage.getItem('votanteCedula');
    votanteNombre = sessionStorage.getItem('votanteNombre');
    
    if (!votanteCedula) {
        // No hay sesión, redirigir al login
        window.location.href = '/';
        return;
    }
    
    // Mostrar información del votante
    document.getElementById('nombreVotante').textContent = votanteNombre;
    document.getElementById('cedulaVotante').textContent = votanteCedula;
    
    // Cargar municipios
    cargarMunicipios();
    
    // Configurar event listeners
    configurarEventListeners();
});

async function cargarMunicipios() {
    try {
        const response = await fetch(`${API_URL}/municipios`);
        const data = await response.json();
        
        if (data.success) {
            const selectMunicipio = document.getElementById('selectMunicipio');
            selectMunicipio.innerHTML = '<option value="">-- Seleccione un municipio --</option>';
            
            data.municipios.forEach(municipio => {
                const option = document.createElement('option');
                option.value = municipio;
                option.textContent = municipio;
                selectMunicipio.appendChild(option);
            });
        } else {
            mostrarError('Error al cargar los municipios');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarError('Error de conexión al cargar municipios');
    }
}

function configurarEventListeners() {
    // Cambiar municipio
    document.getElementById('selectMunicipio').addEventListener('change', function() {
        const btnVerCandidatos = document.getElementById('btnVerCandidatos');
        btnVerCandidatos.disabled = !this.value;
    });
    
    // Ver candidatos
    document.getElementById('btnVerCandidatos').addEventListener('click', cargarCandidatos);
    
    // Votar
    document.getElementById('btnVotar').addEventListener('click', registrarVoto);
}

async function cargarCandidatos() {
    const municipio = document.getElementById('selectMunicipio').value;
    
    if (!municipio) {
        mostrarError('Por favor seleccione un municipio');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/candidatos/${encodeURIComponent(municipio)}`);
        const data = await response.json();
        
        if (data.success) {
            mostrarCandidatos(data.candidatos, municipio);
        } else {
            mostrarError(data.error || 'Error al cargar candidatos');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarError('Error de conexión al cargar candidatos');
    }
}

function mostrarCandidatos(candidatos, municipio) {
    const pasoMunicipio = document.getElementById('pasoMunicipio');
    const pasoCandidatos = document.getElementById('pasoCandidatos');
    const listaCandidatos = document.getElementById('listaCandidatos');
    const municipioNombre = document.getElementById('municipioNombre');
    
    // Ocultar paso de municipio, mostrar candidatos
    pasoMunicipio.style.display = 'none';
    pasoCandidatos.style.display = 'block';
    
    municipioNombre.textContent = municipio;
    listaCandidatos.innerHTML = '';
    
    if (candidatos.length === 0) {
        listaCandidatos.innerHTML = '<p style="text-align: center; color: #666; padding: 20px;">No hay candidatos registrados para este municipio</p>';
        return;
    }
    
    candidatos.forEach(candidato => {
        const card = document.createElement('div');
        card.className = 'candidato-card';
        card.dataset.candidatoId = candidato.id;
        card.innerHTML = `
            <div class="candidato-radio"></div>
            <div class="candidato-info">
                <h3>${candidato.nombre}</h3>
                <p>Municipio: ${candidato.municipio}</p>
                <span class="discapacidad">${candidato.tipo_discapacidad}</span>
            </div>
        `;
        
        card.addEventListener('click', () => seleccionarCandidato(card, candidato));
        listaCandidatos.appendChild(card);
    });
}

function seleccionarCandidato(card, candidato) {
    // Remover selección anterior
    document.querySelectorAll('.candidato-card').forEach(c => {
        c.classList.remove('seleccionado');
    });
    
    // Seleccionar nuevo candidato
    card.classList.add('seleccionado');
    candidatoSeleccionado = candidato;
    
    // Habilitar botón de votar
    document.getElementById('btnVotar').disabled = false;
}

async function registrarVoto() {
    if (!candidatoSeleccionado) {
        mostrarError('Por favor seleccione un candidato');
        return;
    }
    
    // Confirmar voto
    const confirmar = confirm(
        `¿Está seguro de votar por:\n\n${candidatoSeleccionado.nombre}\n\nEsta acción no se puede deshacer.`
    );
    
    if (!confirmar) return;
    
    const btnVotar = document.getElementById('btnVotar');
    btnVotar.disabled = true;
    btnVotar.innerHTML = '<span class="loading"></span> Registrando voto...';
    
    try {
        const response = await fetch(`${API_URL}/votar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                cedula: votanteCedula,
                candidato_id: candidatoSeleccionado.id
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Voto registrado exitosamente
            mostrarConfirmacion();
        } else {
            mostrarError(data.error || 'Error al registrar el voto');
            btnVotar.disabled = false;
            btnVotar.textContent = '✓ VOTAR';
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarError('Error de conexión al registrar el voto');
        btnVotar.disabled = false;
        btnVotar.textContent = '✓ VOTAR';
    }
}

function mostrarConfirmacion() {
    // Ocultar pasos de votación
    document.getElementById('pasoMunicipio').style.display = 'none';
    document.getElementById('pasoCandidatos').style.display = 'none';
    
    // Mostrar mensaje de confirmación
    const mensajeConfirmacion = document.getElementById('mensajeConfirmacion');
    mensajeConfirmacion.style.display = 'block';
    
    // Limpiar sesión
    sessionStorage.removeItem('votanteCedula');
    sessionStorage.removeItem('votanteNombre');
    sessionStorage.removeItem('votanteMunicipio');
}

function mostrarError(mensaje) {
    const mensajeError = document.getElementById('mensajeError');
    mensajeError.textContent = '❌ ' + mensaje;
    mensajeError.style.display = 'block';
    
    // Ocultar mensaje después de 5 segundos
    setTimeout(() => {
        mensajeError.style.display = 'none';
    }, 5000);
}
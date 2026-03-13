const API_URL = '/api';

document.getElementById('loginForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const cedula = document.getElementById('cedula').value.trim();
    const mensajeError = document.getElementById('mensajeError');
    const btnSubmit = this.querySelector('button[type="submit"]');
    
    // Limpiar mensajes anteriores
    mensajeError.style.display = 'none';
    mensajeError.textContent = '';
    
    // Validar que la cédula no esté vacía
    if (!cedula) {
        mostrarError('Por favor ingrese su número de cédula');
        return;
    }
    
    // Deshabilitar botón mientras se procesa
    btnSubmit.disabled = true;
    btnSubmit.innerHTML = '<span class="loading"></span> Validando...';
    
    try {
        const response = await fetch(`${API_URL}/validar-votante`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ cedula })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Votante válido, redirigir a página de votación
            // Guardar información del votante en sessionStorage
            sessionStorage.setItem('votanteCedula', cedula);
            sessionStorage.setItem('votanteNombre', data.votante.nombre);
            sessionStorage.setItem('votanteMunicipio', data.votante.municipio);
            
            window.location.href = '/votacion.html';
        } else {
            // Error - votante no encontrado o ya votó
            mostrarError(data.error || 'Error al validar el votante');
        }
        
    } catch (error) {
        console.error('Error:', error);
        mostrarError('Error de conexión con el servidor. Intente nuevamente.');
    } finally {
        // Restaurar botón
        btnSubmit.disabled = false;
        btnSubmit.textContent = 'Continuar →';
    }
});

function mostrarError(mensaje) {
    const mensajeError = document.getElementById('mensajeError');
    mensajeError.textContent = '❌ ' + mensaje;
    mensajeError.style.display = 'block';
}
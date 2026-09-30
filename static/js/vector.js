// Archivo de Vector - JavaScript principal
console.log('⌛ Archivo de Vector · JS cargado');

// Función para alternar detalles de lección
function toggleLesson(el) {
    const details = el.querySelector('.lesson-details');
    if (details) {
        if (details.style.display === 'none') {
            details.style.display = 'block';
            el.style.borderColor = 'var(--violet)';
        } else {
            details.style.display = 'none';
            el.style.borderColor = 'var(--border-cyan)';
        }
    }
}

// Función para guardar progreso (vía AJAX)
function guardarProgreso(lessonId, score, completed) {
    const csrf = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    fetch('/api/guardar-progreso/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrf,
        },
        body: JSON.stringify({ lesson_id: lessonId, score: score, completed: completed })
    })
    .then(r => r.json())
    .then(data => {
        if (data.status === 'success') {
            console.log('✅ Progreso guardado:', data);
        }
    })
    .catch(e => console.error('❌ Error:', e));
}

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    console.log('📚 Archivo de Vector listo');
});

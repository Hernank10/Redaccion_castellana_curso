# API REST — El Archivo de Vector

Base URL: `http://127.0.0.1:8007/api/v1/`

## Autenticación

Todos los endpoints protegidos requieren el header:
```
Authorization: Token <tu_token>
```

### POST `/auth/register/`
Registrar usuario nuevo.
```json
{
  "username": "nuevo",
  "email": "nuevo@test.local",
  "password": "Test1234",
  "first_name": "Nuevo",
  "last_name": "User"
}
```
Devuelve: `{ token, user }`

### POST `/auth/login/`
```json
{ "username": "est_test_001", "password": "Test1234!" }
```
Devuelve: `{ token, user }`

### POST `/auth/logout/`
Borra el token. Requiere auth.

### GET `/auth/me/`
Datos del usuario + score + streak + counts. Requiere auth.

---

## Cursos

### GET `/courses/`
Lista paginada de cursos activos. Soporta `?search=` y `?ordering=`.

### GET `/courses/{slug}/`
Detalle del curso con lecciones embebidas.

### GET `/courses/{slug}/lessons/`
Lecciones del curso.

### GET `/courses/{slug}/ranking/`
Top 20 estudiantes del curso.

---

## Lecciones

### GET `/lessons/`
Lista paginada. Soporta `?search=`.

### GET `/lessons/{id}/`
Detalle de la lección.

### GET `/lessons/{id}/exercises/`
Ejercicios de la lección. `correct_answer` solo visible para staff.

---

## Progreso (requiere auth)

### GET `/progress/`
Progreso del usuario actual.

### POST `/progress/guardar/`
```json
{ "lesson_id": 1, "score": 85, "completed": true }
```

---

## Inscripciones (requiere auth)

### GET `/inscripciones/`
Cursos inscritos del usuario.

### POST `/inscripciones/inscribirse/`
```json
{ "curso_slug": "comunicacion-efectiva-12-248" }
```

---

## Certificados (requiere auth)

### GET `/certificados/`
Certificados del usuario.

---

## Logros (requiere auth)

### GET `/logros/`
Insignias/medallas/estrellas/libros.

---

## Notificaciones (requiere auth)

### GET `/notificaciones/`
Lista de notificaciones.

### POST `/notificaciones/{id}/leer/`
Marca una como leída.

### POST `/notificaciones/leer_todas/`
Marca todas como leídas.

---

## Ranking

### GET `/ranking/`
Top 50 global (público).

---

## Códigos de estado

| Código | Significado |
|--------|-------------|
| 200 | OK |
| 201 | Creado |
| 400 | Datos inválidos |
| 401 | Token inválido o ausente |
| 403 | Sin permisos |
| 404 | No encontrado |
| 500 | Error del servidor |
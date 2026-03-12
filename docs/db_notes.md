# DB Notes — Feria de Servicio Social Backend

## Resumen

Se configuró y validó la base de datos del proyecto **Feria de Servicio Social** usando **PostgreSQL en Docker**, con control de cambios mediante **Alembic** y acceso de inspección a través de **pgAdmin**.  
La estructura actual ya soporta el flujo base del sistema para usuarios administrativos, estudiantes, periodos, oportunidades e inscripciones.

---

## Stack utilizado

- **PostgreSQL 16**
- **Docker**
- **SQLAlchemy**
- **Alembic**
- **pgAdmin**

---

## Tablas principales creadas

### `users`
Tabla para usuarios administrativos del sistema.

Campos principales:
- `id` (PK)
- `email`
- `hashed_password`
- `role`
- `created_at`

Restricciones:
- `email` UNIQUE
- `role` definido mediante ENUM con valores:
  - `admin`
  - `intern`

---

### `students`
Tabla para estudiantes que se registran en el sistema.

Campos principales:
- `id` (PK)
- `matricula`
- `nombre`
- `apellido`
- `email`
- `hashed_password`
- `created_at`

Restricciones:
- `matricula` UNIQUE
- `email` UNIQUE

---

### `periods`
Tabla para periodos académicos o ciclos de servicio social.

Campos principales:
- `id` (PK)
- `name`
- `starts_at`
- `ends_at`
- `is_active`

Restricciones:
- `name` UNIQUE

---

### `opportunities`
Tabla para oportunidades o vacantes de servicio social.

Campos principales:
- `id` (PK)
- `period_id` (FK)
- `title`
- `description`
- `company`
- `location`
- `capacity`
- `is_active`

Relación:
- `period_id` → `periods.id`

---

### `enrollments`
Tabla de inscripciones de estudiantes a oportunidades.

Campos principales:
- `id` (PK)
- `student_id` (FK)
- `opportunity_id` (FK)
- `period_id` (FK)
- `status`
- `created_at`

Relaciones:
- `student_id` → `students.id`
- `opportunity_id` → `opportunities.id`
- `period_id` → `periods.id`

Restricciones clave:
- `UNIQUE(student_id, opportunity_id)`
- `UNIQUE(student_id, period_id)`

La restricción `UNIQUE(student_id, period_id)` implementa la regla de negocio principal:  
**un estudiante solo puede tener una inscripción por periodo**.

---

## Integridad referencial

Se validaron las llaves foráneas entre las tablas principales:

- `opportunities.period_id` referencia `periods.id`
- `enrollments.student_id` referencia `students.id`
- `enrollments.opportunity_id` referencia `opportunities.id`
- `enrollments.period_id` referencia `periods.id`

Esto garantiza consistencia entre periodos, oportunidades y registros de inscripción.

---

## Constraints verificados

### `users`
- Primary Key en `id`
- UNIQUE en `email`
- ENUM en `role`

### `students`
- Primary Key en `id`
- UNIQUE en `matricula`
- UNIQUE en `email`

### `periods`
- Primary Key en `id`
- UNIQUE en `name`

### `enrollments`
- Primary Key en `id`
- UNIQUE en `(student_id, opportunity_id)`
- UNIQUE en `(student_id, period_id)`

---

## Índices creados

Para optimizar consultas frecuentes, se añadieron índices en:

### `opportunities`
- índice por `period_id`
- índice compuesto por `(period_id, is_active)`

### `enrollments`
- índice por `student_id`
- índice por `opportunity_id`
- índice por `period_id`

Estos índices ayudan a mejorar el rendimiento en consultas como:
- filtrar oportunidades por periodo activo
- listar inscripciones por estudiante
- listar inscritos por oportunidad
- consultar inscripciones por periodo

---

## Seeds iniciales

Se crearon seeds para facilitar pruebas y desarrollo.

### Usuarios seed
- `admin@feria.mx`
- `intern@feria.mx`

### Periodo seed
- `2026_S1`

### Oportunidades seed
Se insertaron oportunidades de prueba asociadas al periodo activo.

---

## Scripts utilizados

### Migraciones
```bash
alembic upgrade head
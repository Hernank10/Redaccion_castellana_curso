# 🚀 Guía de Despliegue en Producción

Documentación completa del despliegue del **Archivo de Vector** en producción:
PostgreSQL + Gunicorn + Nginx + Storage externo + Railway.

---

## 📋 Índice

1. [Arquitectura](#arquitectura)
2. [Requisitos previos](#requisitos-previos)
3. [Configuración de settings](#configuración-de-settings)
4. [Variables de entorno](#variables-de-entorno)
5. [PostgreSQL](#postgresql)
6. [Gunicorn](#gunicorn)
7. [Nginx](#nginx)
8. [SSL con Let's Encrypt](#ssl-con-lets-encrypt)
9. [Storage externo para PDFs](#storage-externo-para-pdfs)
10. [Despliegue en Railway](#despliegue-en-railway)
11. [Scripts de despliegue](#scripts-de-despliegue)
12. [Docker (opcional)](#docker-opcional)
13. [Checklist pre-producción](#checklist-pre-producción)
14. [Troubleshooting](#troubleshooting)

---

## Arquitectura

```
┌──────────────┐
│   Cliente    │
└──────┬───────┘
       │ HTTPS (443)
       ▼
┌──────────────┐
│    Nginx     │  ← Reverse proxy + SSL + estáticos
└──────┬───────┘
       │ Unix socket
       ▼
┌──────────────┐
│   Gunicorn   │  ← WSGI, workers
└──────┬───────┘
       │
       ▼
┌──────────────┐      ┌─────────────────┐
│    Django    │─────▶│   PostgreSQL    │
└──────┬───────┘      └─────────────────┘
       │
       ▼
┌──────────────┐
│   Storage    │  ← S3 / Cloudflare R2 / local
│   (PDFs)     │
└──────────────┘
```

| Componente | Función |
|-----------|---------|
| **Nginx** | Reverse proxy, terminación SSL, sirve estáticos directamente |
| **Gunicorn** | Servidor WSGI multi-worker (reemplaza `runserver`) |
| **PostgreSQL** | Base de datos relacional en producción |
| **systemd** | Gestor de servicios (arranque automático + reinicio) |
| **WhiteNoise** | Sirve estáticos si no usas Nginx |
| **Storage externo** | PDFs/certificados en S3 o similar |

---

## Requisitos previos

### Servidor Linux (VPS)

- Ubuntu 22.04 LTS o Debian 12
- 2 GB RAM mínimo
- 20 GB SSD
- Python 3.12
- PostgreSQL 16
- Nginx 1.24+

### Alternativa PaaS (sin VPS)

- **Railway** (recomendado para empezar)
- **Render**
- **PythonAnywhere**
- **Fly.io**

---

## Configuración de settings

El proyecto usa **settings separados** por entorno:

```
lms_vector/settings/
├── __init__.py
├── base.py          # Común a todos los entornos
├── development.py   # SQLite local, DEBUG=True
└── production.py    # PostgreSQL, HTTPS, DEBUG=False
```

### `base.py` (común)

```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'dev-insecure-change-me')
DEBUG = os.environ.get('DJANGO_DEBUG', 'false').lower() == 'true'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# WhiteNoise para estáticos
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ← aquí
    # ... resto
]

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### `development.py`

```python
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

MIDDLEWARE = [m for m in MIDDLEWARE if 'whitenoise' not in m]
SECURE_SSL_REDIRECT = False
```

### `production.py`

```python
from .base import *
import dj_database_url

DEBUG = False
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'temp-key')
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '*').split(',')

# PostgreSQL (Railway/Render dan DATABASE_URL)
if os.environ.get('DATABASE_URL'):
    DATABASES = {'default': dj_database_url.config(conn_max_age=600, ssl_require=False)}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'vector_db'),
            'USER': os.environ.get('DB_USER', 'vector_user'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
            'CONN_MAX_AGE': 60,
        }
    }

# HTTPS obligatorio
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': str(BASE_DIR / 'logs' / 'django.log'),
        },
    },
    'loggers': {
        'django': {'handlers': ['file'], 'level': 'WARNING'},
    },
}
```

---

## Variables de entorno

### `.env` (producción VPS)

```ini
DJANGO_SETTINGS_MODULE=lms_vector.settings.production
DJANGO_SECRET_KEY=clave-de-50-caracteres-aleatoria
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=tudominio.com,www.tudominio.com
CSRF_TRUSTED_ORIGINS=https://tudominio.com,https://www.tudominio.com

DB_NAME=vector_db
DB_USER=vector_user
DB_PASSWORD=contraseña-muy-segura
DB_HOST=localhost
DB_PORT=5432

GUNICORN_WORKERS=3
GUNICORN_TIMEOUT=120

# Storage (opcional)
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_STORAGE_BUCKET_NAME=vector-media
AWS_S3_REGION_NAME=us-east-1
```

### `.gitignore`

```
.env
*.env
logs/
staticfiles/
media/
settings.py.old
```

**Regla**: `.env` NUNCA se sube a Git. Se usa para guardar secretos.

---

## PostgreSQL

### Instalación (Ubuntu)

```bash
sudo apt update
sudo apt install -y postgresql postgresql-contrib libpq-dev
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Crear base de datos y usuario

```bash
sudo -u postgres psql
```

Dentro de `psql`:

```sql
CREATE DATABASE vector_db;
CREATE USER vector_user WITH PASSWORD 'contraseña-segura';
ALTER ROLE vector_user SET client_encoding TO 'utf8';
ALTER ROLE vector_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE vector_user SET timezone TO 'America/Bogota';
GRANT ALL PRIVILEGES ON DATABASE vector_db TO vector_user;
ALTER DATABASE vector_db OWNER TO vector_user;
\q
```

### Ajustes en `postgresql.conf` (opcional, mejoras)

```conf
shared_buffers = 256MB
effective_cache_size = 768MB
maintenance_work_mem = 64MB
work_mem = 4MB
```

Reiniciar:

```bash
sudo systemctl restart postgresql
```

### Migración desde SQLite

```bash
# En desarrollo: exportar datos
python manage.py dumpdata --natural-foreign --natural-primary \
    --exclude=contenttypes --exclude=auth.Permission \
    --indent 2 > datos.json

# En producción: importar
python manage.py loaddata datos.json
```

### `psycopg2` en requirements

```txt
psycopg2-binary==2.9.10
```

> **Nota**: `-binary` trae binarios precompilados (rápido de instalar).
> Para producción crítica se prefiere `psycopg2` puro (compilado).

---

## Gunicorn

### Instalación

```txt
gunicorn==23.0.0
```

### `gunicorn.conf.py`

```python
import multiprocessing
import os

bind = 'unix:/run/gunicorn/vector.sock'
workers = int(os.environ.get('GUNICORN_WORKERS', 2 * multiprocessing.cpu_count() + 1))
worker_class = 'sync'
timeout = int(os.environ.get('GUNICORN_TIMEOUT', 120))
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
accesslog = '/var/log/gunicorn/access.log'
errorlog = '/var/log/gunicorn/error.log'
loglevel = 'info'
preload_app = True
```

> **Fórmula de workers**: `(2 × CPU cores) + 1`.
> Para un VPS de 2 vCPU → 5 workers.

### Probar en local (Windows)

```cmd
E:\PythonPortable_Django5\python.exe -m gunicorn lms_vector.wsgi:application --bind 127.0.0.1:8001
```

Abre `http://127.0.0.1:8001/es/`

### Servicio systemd

`/etc/systemd/system/gunicorn.service`:

```ini
[Unit]
Description=Gunicorn daemon for Archivo de Vector
After=network.target

[Service]
User=vector
Group=www-data
WorkingDirectory=/srv/vector/Redaccion_castellana_curso-main
EnvironmentFile=/srv/vector/Redaccion_castellana_curso-main/.env
ExecStart=/srv/vector/venv/bin/gunicorn \
    --config /srv/vector/Redaccion_castellana_curso-main/gunicorn.conf.py \
    lms_vector.wsgi:application
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### Comandos systemd

```bash
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl status gunicorn
sudo journalctl -u gunicorn -f      # ver logs en vivo
sudo systemctl restart gunicorn     # reiniciar
```

---

## Nginx

### Instalación

```bash
sudo apt install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### Configuración `/etc/nginx/sites-available/vector`

```nginx
upstream django {
    server unix:/run/gunicorn/vector.sock;
}

server {
    listen 80;
    server_name tudominio.com www.tudominio.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tudominio.com www.tudominio.com;

    ssl_certificate /etc/letsencrypt/live/tudominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tudominio.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;

    client_max_body_size 20M;

    # Estáticos
    location /static/ {
        alias /srv/vector/Redaccion_castellana_curso-main/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media (uploads)
    location /media/ {
        alias /srv/vector/Redaccion_castellana_curso-main/media/;
        expires 7d;
    }

    location = /favicon.ico {
        access_log off;
        log_not_found off;
    }

    # Proxy a Gunicorn
    location / {
        proxy_pass http://django;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_read_timeout 120s;
        proxy_connect_timeout 10s;
    }
}
```

### Activar

```bash
sudo ln -s /etc/nginx/sites-available/vector /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Comandos útiles

```bash
sudo nginx -t                 # test config
sudo systemctl reload nginx   # recargar sin cortar
sudo systemctl status nginx
sudo tail -f /var/log/nginx/error.log
```

---

## SSL con Let's Encrypt

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d tudominio.com -d www.tudominio.com
sudo systemctl enable certbot.timer
```

Certbot renueva automáticamente cada 60 días. Probar renovación:

```bash
sudo certbot renew --dry-run
```

---

## Storage externo para PDFs

### Problema

Los certificados PDF y los informes se guardan en `MEDIA_ROOT` local. En producción
con múltiples servidores o contenedores efímeros (Railway, Render, Heroku), ese
almacenamiento se pierde al reiniciar.

### Solución: `django-storages` + S3 (o compatible)

#### Opción A: AWS S3

```bash
pip install django-storages boto3
```

En `production.py`:

```python
if os.environ.get('AWS_ACCESS_KEY_ID'):
    AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
    AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']
    AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_DEFAULT_ACL = 'private'
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}

    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
```

#### Opción B: Cloudflare R2 (más barato)

```python
AWS_ACCESS_KEY_ID = os.environ['R2_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['R2_SECRET_ACCESS_KEY']
AWS_STORAGE_BUCKET_NAME = os.environ['R2_BUCKET_NAME']
AWS_S3_ENDPOINT_URL = f'https://{os.environ["R2_ACCOUNT_ID"]}.r2.cloudflarestorage.com'
AWS_S3_REGION_NAME = 'auto'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
```

#### Opción C: Backblaze B2

Similar a S3, más barato aún que R2 para grandes volúmenes.

### Uso en el código

Los certificados ya se generan en memoria y se devuelven como `HttpResponse`.
Para guardarlos como archivos, usar el storage de Django:

```python
from django.core.files.base import ContentFile

# Guardar PDF en el storage configurado
cert.archivo_pdf.save(
    f'certificado_{cert.codigo_verificacion}.pdf',
    ContentFile(pdf_bytes),
    save=True,
)
```

### Beneficios del storage externo

| Aspecto | Local | S3/R2/B2 |
|---------|-------|----------|
| Persistencia | ❌ Se borra al reiniciar | ✅ Permanente |
| Escalabilidad | ❌ Un solo servidor | ✅ Ilimitado |
| CDN | ❌ No | ✅ CloudFront/R2 CDN |
| Backup | Manual | Automático |
| Costo | Incluido en VPS | ~$0.015/GB/mes |

---

## Despliegue en Railway

Railway es la opción más sencilla si no tienes VPS.

### Archivos necesarios

**`Procfile`**:

```
web: gunicorn lms_vector.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120
```

**`runtime.txt`**:

```
python-3.12.4
```

### Pasos

1. Cuenta en **https://railway.app** (login con GitHub)
2. **New Project** → **Deploy from GitHub repo**
3. Elige `Hernank10/Redaccion_castellana_curso`
4. **+ Create** → **Database** → **PostgreSQL**
5. Railway añade `DATABASE_URL` automáticamente
6. Añade variables en el servicio web:
   - `DJANGO_SETTINGS_MODULE=lms_vector.settings.production`
   - `DJANGO_SECRET_KEY=<clave>`
   - `DJANGO_DEBUG=false`
   - `DJANGO_ALLOWED_HOSTS=*`
   - `CSRF_TRUSTED_ORIGINS=https://*.railway.app`
7. **Settings** → **Networking** → **Generate Domain**
8. **⋮** → **Run Command**:
   - `python manage.py migrate`
   - `python manage.py createsuperuser`

### Costes

| Plan | Crédito | RAM | Después |
|------|---------|-----|---------|
| **Trial** | $5 único | 1 GB | 30 días |
| **Free** | $1/mes | 0.5 GB | Permanente |
| **Hobby** | $5/mes | 8 GB | Producción real |

---

## Scripts de despliegue

### `deploy.sh` (VPS)

```bash
#!/bin/bash
set -e

PROJECT_DIR="/srv/vector/Redaccion_castellana_curso-main"
VENV="/srv/vector/venv"

cd "$PROJECT_DIR"

echo "→ Pulling latest changes..."
git pull origin main

echo "→ Activating venv..."
source "$VENV/bin/activate"

echo "→ Installing dependencies..."
pip install -r requirements.txt --quiet

echo "→ Running migrations..."
python manage.py migrate --noinput

echo "→ Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "→ Running deployment check..."
python manage.py check --deploy

echo "→ Restarting Gunicorn..."
sudo systemctl restart gunicorn

echo "✓ Deployment complete"
```

Uso:

```bash
chmod +x deploy.sh
./deploy.sh
```

### `.bat` (Windows, para Railway)

```cmd
:: railway-push.bat
git add .
git commit -m "Deploy %date%"
git push
```

---

## Docker (opcional)

Si tu sistema lo soporta (Windows 10 build 19044+, Linux, macOS):

**`Dockerfile`**:

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--config", "gunicorn.conf.py", "lms_vector.wsgi:application"]
```

**`docker-compose.yml`**:

```yaml
version: '3.9'

services:
  db:
    image: postgres:16-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    restart: always

  web:
    build: .
    env_file: .env
    depends_on:
      - db
    restart: always
    volumes:
      - static_volume:/app/staticfiles

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - static_volume:/static
    depends_on:
      - web
    restart: always

volumes:
  postgres_data:
  static_volume:
```

Comandos:

```bash
docker compose up -d --build
docker compose logs -f
docker compose down
docker compose exec web python manage.py migrate
```

---

## Checklist pre-producción

Ejecutar antes de cada deploy:

```bash
# 1. Django check de seguridad
python manage.py check --deploy

# 2. Verificar DEBUG=False
python manage.py shell -c "from django.conf import settings; print('DEBUG:', settings.DEBUG)"

# 3. Verificar conexión PostgreSQL
python manage.py dbshell -c "SELECT version();"

# 4. Verificar Gunicorn
sudo systemctl status gunicorn

# 5. Verificar Nginx
sudo nginx -t
sudo systemctl status nginx

# 6. Probar HTTPS
curl -I https://tudominio.com

# 7. Probar certbot
sudo certbot renew --dry-run
```

### Checklist de seguridad

| Item | Estado |
|------|--------|
| `DEBUG = False` | ⬜ |
| `SECRET_KEY` en `.env` | ⬜ |
| `ALLOWED_HOSTS` explícito | ⬜ |
| `SECURE_SSL_REDIRECT = True` | ⬜ |
| `SESSION_COOKIE_SECURE = True` | ⬜ |
| `CSRF_COOKIE_SECURE = True` | ⬜ |
| HSTS 1 año | ⬜ |
| `X_FRAME_OPTIONS = 'DENY'` | ⬜ |
| `.env` en `.gitignore` | ⬜ |
| `check --deploy` sin warnings | ⬜ |
| Backups automáticos PostgreSQL | ⬜ |
| Logs rotados | ⬜ |

### Backup PostgreSQL

```bash
# Backup diario
pg_dump -U vector_user -h localhost vector_db > /backups/vector_$(date +%Y%m%d).sql

# Cron
0 3 * * * pg_dump -U vector_user vector_db | gzip > /backups/vector_$(date +\%Y\%m\%d).sql.gz
```

### Restaurar

```bash
psql -U vector_user -h localhost vector_db < /backups/vector_20261001.sql
```

---

## Troubleshooting

### Error: `ModuleNotFoundError: lms_vector.settings.development`

**Causa**: la carpeta `settings/` no existe o falta `__init__.py`.

**Fix**:
```cmd
dir lms_vector\settings
```

### Error: `no such table: core_course`

**Causa**: `BASE_DIR` mal calculado. `settings/base.py` está 3 niveles abajo.

**Fix**:
```python
BASE_DIR = Path(__file__).resolve().parent.parent.parent
```

### Error: `DisallowedHost`

**Causa**: dominio no está en `ALLOWED_HOSTS`.

**Fix**:
```python
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '*').split(',')
```

### Error: `CSRF verification failed`

**Causa**: el dominio no está en `CSRF_TRUSTED_ORIGINS`.

**Fix**:
```python
CSRF_TRUSTED_ORIGINS = ['https://tudominio.com', 'https://*.railway.app']
```

### Error: `static files not found`

**Causa**: no se ejecutó `collectstatic`.

**Fix**:
```bash
python manage.py collectstatic --noinput
```

### Error: `Docker requires Windows 10 version 2004+`

**Causa**: Windows antiguo (build < 19044).

**Fix**: usar Railway, Render o PythonAnywhere en lugar de Docker.

### Error: `psycopg2 installation failed`

**Causa**: falta `libpq-dev` en el sistema.

**Fix**:
```bash
sudo apt install libpq-dev
```

O usa `psycopg2-binary` (no requiere compilación).

---

## Recursos

- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)
- [Gunicorn Docs](https://docs.gunicorn.org/)
- [Nginx Docs](https://nginx.org/en/docs/)
- [Railway Docs](https://docs.railway.app/)
- [Let's Encrypt](https://letsencrypt.org/)
- [django-storages](https://django-storages.readthedocs.io/)

---

**Última actualización**: 1 de octubre de 2026
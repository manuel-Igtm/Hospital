# 🐳 Docker Quick Start

Get the entire hospital backend running with one command!

## Prerequisites

- Docker Engine 20.10+
- Docker Compose V2
- 4GB+ free RAM
- 10GB+ free disk space

## Quick Start

```bash
# 1. Copy environment template
cd docker
cp .env.example .env

# 2. Generate a secure Django secret key
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
# Copy the output and paste it in .env as DJANGO_SECRET_KEY=<your-key>

# 3. Start all services
docker-compose up -d

# 4. Check logs
docker-compose logs -f web

# 5. Create superuser
docker-compose exec web python manage.py createsuperuser

# 6. Access services
# - Backend API: http://localhost:8000/api/v1/
# - API Docs: http://localhost:8000/api/v1/docs/
# - Admin Panel: http://localhost:8000/admin/
# - PgAdmin: http://localhost:5050/ (dev profile only)
```

## Services Overview

| Service | Port | Description |
|---------|------|-------------|
| **web** | 8000 | Django API (gunicorn) |
| **postgres** | 5432 | PostgreSQL 15 database |
| **redis** | 6379 | Cache & Celery broker |
| **celery_worker** | - | Background task processor |
| **celery_beat** | - | Scheduled task runner |
| **pgadmin** | 5050 | Database admin UI (dev only) |
| **nginx** | 80/443 | Reverse proxy (prod only) |

## Development Workflow

### Start with live reload
```bash
# Start all services in dev mode with PgAdmin
docker-compose --profile dev up

# In another terminal, watch logs
docker-compose logs -f web celery_worker
```

### Run migrations
```bash
docker-compose exec web python manage.py migrate
```

### Create demo data
```bash
docker-compose exec web python manage.py seed_data
```

### Run tests
```bash
# All tests
docker-compose exec web pytest

# With coverage
docker-compose exec web pytest --cov=apps --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Django shell
```bash
docker-compose exec web python manage.py shell_plus
```

### Database shell
```bash
# PostgreSQL CLI
docker-compose exec postgres psql -U hospital_user -d hospital_db

# Or use PgAdmin at http://localhost:5050
```

## Production Deployment

### With Nginx reverse proxy
```bash
# Start with production profile
docker-compose --profile prod up -d

# View logs
docker-compose logs -f web nginx

# Scale workers
docker-compose up -d --scale celery_worker=3
```

### Environment variables
Edit `.env` file for production:
```bash
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=<your-secure-50-char-key>
DJANGO_ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com
DATABASE_URL=postgresql://user:pass@host:5432/dbname
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

### SSL/TLS
Place your certificates in `docker/certs/`:
- `fullchain.pem` (certificate + chain)
- `privkey.pem` (private key)

Update `nginx.conf` to enable HTTPS.

## Maintenance

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web

# Last 100 lines
docker-compose logs --tail=100 web
```

### Restart services
```bash
# All services
docker-compose restart

# Specific service
docker-compose restart web
```

### Stop services
```bash
# Stop but keep data
docker-compose stop

# Stop and remove containers (data persists in volumes)
docker-compose down

# Remove everything including volumes (⚠️ DELETES DATA)
docker-compose down -v
```

### Database backup
```bash
# Backup
docker-compose exec postgres pg_dump -U hospital_user hospital_db > backup.sql

# Restore
cat backup.sql | docker-compose exec -T postgres psql -U hospital_user hospital_db
```

### Update images
```bash
# Rebuild after code changes
docker-compose build

# Pull latest base images
docker-compose pull

# Rebuild without cache
docker-compose build --no-cache
```

## Troubleshooting

### "Database unavailable" error
```bash
# Check postgres is running
docker-compose ps postgres

# Check postgres logs
docker-compose logs postgres

# Manually wait for database
docker-compose exec web python manage.py wait_for_db
```

### "Port already in use" error
```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill the process
kill -9 <PID>

# Or change port in docker-compose.yml
ports:
  - "8001:8000"  # Host:Container
```

### "Out of memory" error
```bash
# Increase Docker memory limit in Docker Desktop settings
# Minimum recommended: 4GB

# Or reduce worker count
docker-compose up -d --scale celery_worker=1
```

### Rebuild C modules
```bash
# Rebuild containers with no cache
docker-compose build --no-cache web celery_worker

# Or rebuild C modules inside container
docker-compose exec web sh -c "cd /build/native/build && make clean && cmake .. && make"
```

### Reset everything
```bash
# Nuclear option: delete all containers, volumes, images
docker-compose down -v --rmi all
docker-compose build
docker-compose up -d
```

## Performance Tuning

### Gunicorn workers
Edit `docker/Dockerfile` CMD:
```dockerfile
# CPU-bound: workers = (2 * CPU_cores) + 1
CMD ["gunicorn", "config.wsgi:application", \
     "--workers", "9", \  # For 4 cores
     "--worker-class", "gthread", \
     "--threads", "2"]
```

### Celery concurrency
Edit `docker-compose.yml`:
```yaml
celery_worker:
  command: celery -A config worker -l info --concurrency=4
```

### PostgreSQL tuning
Create `docker/postgres.conf`:
```ini
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
max_connections = 200
```

Mount in `docker-compose.yml`:
```yaml
postgres:
  volumes:
    - ./postgres.conf:/etc/postgresql/postgresql.conf
  command: postgres -c config_file=/etc/postgresql/postgresql.conf
```

## Security Checklist

- [ ] Change `DJANGO_SECRET_KEY` in `.env`
- [ ] Set `DJANGO_DEBUG=False` in production
- [ ] Configure `DJANGO_ALLOWED_HOSTS`
- [ ] Change database password (`POSTGRES_PASSWORD`)
- [ ] Enable HTTPS with valid SSL certificates
- [ ] Set up Sentry for error tracking
- [ ] Configure firewall to restrict port access
- [ ] Regularly update base images (`docker-compose pull`)
- [ ] Enable Docker security features (AppArmor, seccomp)
- [ ] Use Docker secrets for sensitive data in production

## Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/)
- [Gunicorn Configuration](https://docs.gunicorn.org/en/stable/configure.html)
- [PostgreSQL Docker Hub](https://hub.docker.com/_/postgres)
- [Redis Docker Hub](https://hub.docker.com/_/redis)

---

**Need help?** Open an issue on GitHub or check the main [README.md](../README.md)

# Hospital Backend - Quick Start Guide

Get up and running in 5 minutes! Choose your preferred method.

## 🐳 Option 1: Docker (Recommended for Quick Testing)

The fastest way to see the entire system running.

```bash
# 1. Clone and navigate
cd Hospital/docker

# 2. Copy environment file
cp .env.example .env

# 3. Generate secret key
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
# Copy output to .env as DJANGO_SECRET_KEY

# 4. Start all services
docker-compose up -d

# 5. Create superuser
docker-compose exec web python manage.py createsuperuser

# 6. Visit the API
# - API Docs: http://localhost:8000/api/v1/docs/
# - Admin: http://localhost:8000/admin/
# - PgAdmin: http://localhost:5050/
```

**See [docker/README.md](docker/README.md) for full Docker documentation.**

## 💻 Option 2: Local Development (Recommended for Development)

For active development with fast iteration.

### Prerequisites
```bash
# Check versions
python --version  # Need 3.12+
cmake --version   # Need 3.18+
gcc --version     # Or clang
```

### Setup

```bash
# 1. Install uv (fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Build C modules
cd native
mkdir build && cd build
cmake ..
make
ctest  # Run C tests
cd ../..

# 3. Install Python dependencies
cd backend
uv pip install -e ../native  # Install C extensions
uv pip install -r requirements/dev.txt

# 4. Set up environment
cp .env.example .env
# Edit .env and set DJANGO_SECRET_KEY

# 5. Set up database (PostgreSQL recommended)
# Option A: Use Docker for just PostgreSQL
docker run -d -p 5432:5432 \
  -e POSTGRES_DB=hospital_db \
  -e POSTGRES_USER=hospital_user \
  -e POSTGRES_PASSWORD=hospital_pass \
  postgres:15-alpine

# Option B: Use local PostgreSQL
createdb hospital_db

# 6. Run migrations
export DJANGO_SETTINGS_MODULE=config.settings.dev
python manage.py migrate

# 7. Create superuser
python manage.py createsuperuser

# 8. Start development server
python manage.py runserver

# 9. In another terminal, start Celery (optional)
celery -A config worker -l info
```

**See [backend/README.md](backend/README.md) for full development documentation.**

## 🚀 Option 3: Makefile Commands (Power User)

Automated commands for common tasks.

```bash
# Full setup (builds C, installs deps, runs migrations)
make setup

# Build C modules
make build

# Run all tests
make test

# Run linters
make lint

# Auto-format code
make format

# Start Django dev server
make run

# Start Celery worker
make celery

# Docker shortcuts
make docker-up     # Start all services
make docker-down   # Stop all services
make docker-logs   # View logs

# Cleaning
make clean         # Clean build artifacts
make clean-all     # Nuclear clean
```

**See [Makefile](Makefile) for all available commands.**

## 🧪 Verify Installation

```bash
# Test C modules
cd native/build && ctest -V

# Test Python imports
python -c "from apps.core.utils import generate_pii_token; print('✅ C modules loaded')"

# Test Django
python manage.py check

# Test API
curl http://localhost:8000/health/
# Should return: {"status": "ok", ...}
```

## 📚 What's Next?

1. **Read the docs**: [README.md](README.md) for architecture overview
2. **Explore the API**: http://localhost:8000/api/v1/docs/
3. **Check progress**: [docs/progress.md](docs/progress.md) for weekly goals
4. **Contribute**: [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines

## 🔧 Troubleshooting

### C modules won't compile
```bash
# Install dependencies (Ubuntu/Debian)
sudo apt-get install build-essential cmake libssl-dev libpq-dev

# Install dependencies (macOS)
brew install cmake openssl postgresql
```

### Python import errors
```bash
# Rebuild C extensions
cd native
pip install -e .

# Or use fallback Python implementations
export ENABLE_C_MODULES=False
```

### Database connection errors
```bash
# Check PostgreSQL is running
pg_isready

# Or use SQLite for testing (edit .env)
DATABASE_URL=sqlite:///db.sqlite3
```

### Port already in use
```bash
# Find process using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use different port
python manage.py runserver 8001
```

## 🎯 Choose Your Journey

| Goal | Recommended Path |
|------|------------------|
| **Quick demo** | Docker (Option 1) |
| **Active development** | Local setup (Option 2) |
| **Contributing** | Local + Makefile (Options 2 + 3) |
| **Production deployment** | Docker with prod profile |

## 🆘 Need Help?

- 📖 Full documentation: [README.md](README.md)
- 🐛 Found a bug? Open an issue on GitHub
- 💬 Questions? Check [CONTRIBUTING.md](CONTRIBUTING.md)
- 📧 Contact: Immanuel Njogu (immanuel@njogu.tech)

---

**Pro tip**: Start with Docker to see everything working, then switch to local development for faster iteration. 🚀

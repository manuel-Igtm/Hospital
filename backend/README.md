# Hospital Backend - Getting Started with uv

This project uses [uv](https://github.com/astral-sh/uv) for fast Python package management.

## Quick Setup (using uv)

### 1. Install uv

```bash
# macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv
```

### 2. Create virtual environment and install dependencies

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate  # Windows

# Install dependencies
uv pip install -e ".[dev]"

# Or install from requirements (legacy)
uv pip install -r requirements/dev.txt
```

### 3. Build C modules

```bash
cd ../native
mkdir build && cd build
cmake ..
make
cd ..

# Install Python extensions
uv pip install -e .
cd ../backend
```

### 4. Setup database

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load demo data
python scripts/seed_demo_data.py
```

### 5. Run development server

```bash
python manage.py runserver
```

Visit:
- API: http://localhost:8000/api/v1/
- Admin: http://localhost:8000/admin/
- API Docs: http://localhost:8000/api/v1/docs/

## Using uv Commands

```bash
# Add a new package
uv pip install <package-name>

# Add to dev dependencies
uv pip install --dev <package-name>

# Update all packages
uv pip install -U -r requirements/dev.txt

# Sync environment with pyproject.toml
uv pip sync

# Check for outdated packages
uv pip list --outdated
```

## Development Workflow

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=apps --cov-report=html

# Format code
black .
isort .

# Lint code
flake8
mypy .

# Type checking
mypy apps/

# Security checks
bandit -r apps/
safety check
```

## Docker (Alternative)

```bash
# From project root
docker compose -f docker/docker-compose.yml up -d

# Run migrations in container
docker compose -f docker/docker-compose.yml exec web python manage.py migrate

# Create superuser in container
docker compose -f docker/docker-compose.yml exec web python manage.py createsuperuser
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp docker/.env.example .env
```

Key variables:
- `DJANGO_SECRET_KEY` - Django secret (required)
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string  
- `DJANGO_DEBUG` - Debug mode (True/False)
- `ENABLE_C_MODULES` - Use C extensions (True/False)

## Troubleshooting

**C modules not building?**
```bash
# Install build dependencies
sudo apt-get install build-essential cmake libssl-dev  # Ubuntu/Debian
brew install cmake openssl  # macOS
```

**Database connection errors?**
```bash
# Make sure PostgreSQL is running
sudo systemctl status postgresql  # Linux
brew services list  # macOS
```

**Import errors?**
```bash
# Reinstall in development mode
uv pip install -e ".[dev]"
```

## Next Steps

1. Read [CONTRIBUTING.md](../CONTRIBUTING.md) for development guidelines
2. Check [docs/architecture.md](../docs/architecture.md) for system design
3. Review [docs/api.md](../docs/api.md) for API documentation

---

**Weekly contribution workflow:**
1. Pull latest changes: `git pull origin main`
2. Create feature branch: `git checkout -b feature/your-feature`
3. Make changes, write tests
4. Run linters and tests: `make lint test`
5. Commit with clear message
6. Push and create PR: `git push origin feature/your-feature`

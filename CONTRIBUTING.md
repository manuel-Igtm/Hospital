# Contributing to Hospital Backend System

Thank you for your interest in contributing to this project! We welcome contributions from the community while respecting the intellectual property rights of the original author.

## 📜 License and Copyright

This project is **Copyright (c) 2025, Immanuel Njogu**. All rights reserved.

By contributing to this project, you acknowledge and agree that:

1. **Your contributions will be licensed under the same terms** as the project (non-commercial use permitted, commercial use requires permission)
2. You grant Immanuel Njogu perpetual, worldwide, non-exclusive, royalty-free license to use, modify, and distribute your contributions
3. You have the right to submit the contribution (it's your original work or you have rights to submit it)
4. You understand that the original author retains full commercial rights

## 🚀 Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Hospital.git
   cd Hospital
   ```
3. **Set up development environment** (see README.md Quick Start)
4. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 🛠️ Development Workflow

### Before You Start

1. Check existing issues and PRs to avoid duplicate work
2. For major changes, open an issue first to discuss your approach
3. Keep changes focused - one feature or fix per PR

### Code Standards

#### Python Code

- **Style**: Follow PEP 8; use `black` for formatting (line length: 120)
- **Imports**: Organized with `isort`
- **Type hints**: Use type annotations; validated with `mypy`
- **Docstrings**: Google-style docstrings for public APIs
- **Testing**: Write tests for all new functionality (target: 85%+ coverage)

```python
# Good example
def calculate_total(items: list[LineItem]) -> Decimal:
    """Calculate total cost from line items.
    
    Args:
        items: List of billing line items
        
    Returns:
        Total cost as Decimal
        
    Raises:
        ValueError: If items list is empty
    """
    if not items:
        raise ValueError("Items list cannot be empty")
    return sum(item.amount for item in items)
```

#### C Code

- **Style**: Use `clang-format` (provided config)
- **Safety**: All buffers bounds-checked; no direct heap sharing with Python
- **Documentation**: Doxygen-style comments for public functions
- **Testing**: Unit tests with CTest; memory checks with Valgrind
- **Error handling**: Return error codes; map to Python exceptions properly

```c
// Good example
/**
 * @brief Validate HL7 segment structure
 * @param segment Null-terminated HL7 segment string
 * @param max_len Maximum allowed length
 * @param error_msg Buffer for error message (min 256 bytes)
 * @return 0 on success, negative error code on failure
 */
int validate_hl7_segment(const char *segment, size_t max_len, char *error_msg);
```

#### Django Apps

- **Structure**: Follow Django best practices (models, views, serializers, services)
- **Permissions**: Explicit permission checks on all views
- **Validation**: Use DRF serializers; supplement with C validators where performance matters
- **Signals**: Use for cross-cutting concerns (audit logging)
- **Admin**: Register all models with useful list displays and filters

### Testing Requirements

All contributions must include tests:

**Python:**
```bash
# Run tests with coverage
pytest --cov=apps --cov-report=html

# Target: >= 85% overall, >= 90% for services
```

**C:**
```bash
cd native/build
ctest --output-on-failure

# Memory checks
ctest -T memcheck
```

**Integration:**
- Add tests for new API endpoints
- Ensure migrations are reversible
- Test with both PostgreSQL and SQLite (if applicable)

### Pre-commit Checks

Install pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

Before committing, ensure:
```bash
make lint    # All linters pass
make test    # All tests pass
make format  # Code is formatted
```

## 📝 Commit Messages

Use clear, descriptive commit messages:

```
type(scope): Brief description

Longer explanation if needed. Wrap at 72 characters.

Fixes #123
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Examples:**
- `feat(billing): Add DRG-based cost calculation in C`
- `fix(auth): Correct token refresh endpoint permissions`
- `docs(api): Update OpenAPI examples for lab results`

## 🔍 Pull Request Process

1. **Update documentation** for any user-facing changes
2. **Add tests** for new functionality
3. **Update CHANGELOG** if applicable (unreleased section)
4. **Ensure CI passes** (linting, tests, security scans)
5. **Request review** from maintainers
6. **Address feedback** promptly and courteously

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings
- [ ] Tests added and passing
- [ ] CI/CD passing
```

## 🐛 Reporting Bugs

Use GitHub Issues with the bug template:

**Required information:**
- **Environment**: OS, Python version, PostgreSQL version
- **Steps to reproduce**: Minimal example
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Logs/errors**: Relevant error messages (redact sensitive data!)

## 💡 Suggesting Features

Open an issue with:
- **Use case**: What problem does this solve?
- **Proposed solution**: How should it work?
- **Alternatives considered**: Other approaches you've thought about
- **Complexity**: Rough estimate of effort (small/medium/large)

## 🔒 Security Issues

**Do not open public issues for security vulnerabilities.**

Email security issues privately to: [contact method for Immanuel Njogu]

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We'll acknowledge within 48 hours and work on a fix before public disclosure.

## 📚 Documentation

We use Markdown for documentation. When contributing docs:

- **Clear and concise**: Avoid jargon; explain technical terms
- **Examples**: Include code samples and command outputs
- **Diagrams**: Use Mermaid or draw.io for architecture diagrams
- **Keep updated**: Update docs alongside code changes

## 🎨 Code Style Guide

### Python

```python
# Use type hints
def process_order(order_id: int, user: User) -> OrderResult:
    pass

# Use descriptive variable names
encounter_duration = end_time - start_time  # Good
ed = et - st  # Bad

# Keep functions focused
def validate_and_save_patient(data):  # Bad - does two things
    pass

def validate_patient(data):  # Good
    pass

def save_patient(patient):  # Good
    pass

# Use list comprehensions for simple transformations
active_patients = [p for p in patients if p.is_active]
```

### C

```c
// Use clear naming
calculate_total_cost()  // Good
calc_tot()             // Bad

// Bounds check everything
if (len > MAX_SEGMENT_SIZE) {
    return ERR_TOO_LARGE;
}

// Free resources on all paths
char *buffer = malloc(size);
if (!buffer) return ERR_NO_MEMORY;

if (process(buffer) < 0) {
    free(buffer);
    return ERR_PROCESSING;
}

free(buffer);
return SUCCESS;
```

## 🤖 CI/CD Pipeline

All PRs must pass:

1. **Linting**: black, isort, flake8, mypy, clang-tidy
2. **Security**: bandit, safety
3. **Tests**: pytest (Python), ctest (C)
4. **Coverage**: >= 85% overall
5. **Build**: Docker image builds successfully

## 📋 Review Criteria

Maintainers will evaluate:

- **Code quality**: Readable, maintainable, follows conventions
- **Testing**: Adequate coverage, edge cases handled
- **Performance**: No obvious inefficiencies, C used appropriately for hot paths
- **Security**: No vulnerabilities, proper input validation, no secrets
- **Documentation**: Clear explanations, updated docs
- **Scope**: Focused changes, one feature/fix per PR

## 🏆 Recognition

Contributors will be acknowledged in:
- CHANGELOG for their contributions
- GitHub contributors page
- Special recognition for significant contributions

## ❓ Questions?

- Check the [README.md](README.md) and [docs/](docs/) first
- Search existing issues
- Open a new issue with the "question" label
- Be respectful and patient - maintainers are volunteers

## 📄 Additional Notes

### Backward Compatibility

- **Breaking changes** require major version bump and migration guide
- **Deprecations** must be announced one minor version ahead
- **API changes** must maintain backward compatibility when possible

### Performance

- **Benchmark** performance-sensitive changes
- **Profile** before optimizing
- **C modules** for hot paths only; Python is often fast enough

### Database

- **Migrations** must be reversible
- **Test** with both PostgreSQL and SQLite
- **Indexes** for foreign keys and common query patterns
- **Partitioning** for high-volume tables (audit logs)

---

Thank you for contributing to modern healthcare infrastructure! 🏥

**Remember**: Quality over quantity. A small, well-tested, documented PR is better than a large, untested one.

*No, really, don't commit secrets. We check.* 🔒

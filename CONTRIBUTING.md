# Contributing to Apex PMS

Thank you for your interest in contributing to Apex!

## Development Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables (see `.env.example`)
4. Run migrations: `alembic upgrade head`
5. Start services: `docker-compose up`

## Code Standards

- Follow PEP 8 for Python code
- Use type hints for all function signatures
- Write tests for new features (target >90% coverage)
- Use async/await for I/O operations
- Document complex algorithms and business logic

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes with clear, atomic commits
3. Write or update tests as needed
4. Update documentation if required
5. Submit PR with detailed description
6. Address review feedback

## Testing

pytest tests/ -v --cov=backend --cov-report=html


## Questions?

Open an issue or contact the maintainers.

# Contributing to Sports Stats Scraper

Thank you for considering contributing to Sports Stats Scraper! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help maintain a welcoming environment for all contributors

## How to Contribute

### Reporting Bugs

If you find a bug:

1. **Check existing issues** to see if it's already reported
2. **Create a new issue** with:
   - Clear, descriptive title
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Python version and OS
   - Relevant log files from `logs/` directory

### Suggesting Features

For feature requests:

1. **Check existing issues** to avoid duplicates
2. **Create a new issue** with:
   - Clear description of the feature
   - Use case / motivation
   - Proposed implementation (if you have ideas)

### Contributing Code

1. **Fork the repository**

2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**:
   - Follow the existing code style
   - Add docstrings to functions
   - Include type hints where appropriate
   - Add comments for complex logic

4. **Test your changes**:
   ```bash
   # Run existing tests
   python -m pytest tests/

   # Add new tests for your feature
   ```

5. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add: Brief description of your changes"
   ```

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**:
   - Provide a clear description
   - Reference related issues
   - Explain what testing you've done

## Development Setup

### Prerequisites

- Python 3.8+
- pip
- git

### Setup Development Environment

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/playerstatscraper.git
cd playerstatscraper

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=src

# Run specific test file
python -m pytest tests/test_base_scraper.py
```

### Code Style

We follow PEP 8 with some exceptions:

- Maximum line length: 100 characters
- Use type hints for function parameters and return values
- Docstrings: Google style

```python
def example_function(param1: str, param2: int) -> bool:
    """
    Brief description of function.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When invalid input is provided
    """
    pass
```

### Testing Guidelines

- Write tests for new features
- Maintain or improve code coverage
- Test edge cases and error conditions
- Use descriptive test names

Example test:
```python
def test_player_name_normalization():
    """Test that player names are properly normalized."""
    scraper = BaseScraper(config, cache, logger)
    result = scraper._normalize_player_name("Patrick Mahomes II")
    assert result == "patrick mahomes ii"
```

## Project Structure

Understanding the codebase:

```
src/
├── cli/              # User interface
│   └── menu.py       # Interactive menu system
│
├── scrapers/         # Web scraping logic
│   ├── base_scraper.py    # Common functionality
│   ├── nfl_scraper.py     # NFL-specific
│   └── mlb_scraper.py     # MLB-specific
│
└── utils/            # Utilities
    ├── cache_manager.py   # Caching
    ├── config_manager.py  # Configuration
    ├── logger.py          # Logging
    ├── display.py         # Terminal output
    └── export.py          # Data export
```

## Adding a New Sport

To add support for a new sport (e.g., NBA, NHL):

1. **Create scraper class**:
   ```python
   # src/scrapers/nba_scraper.py
   from .base_scraper import BaseScraper

   class NBAScraper(BaseScraper):
       BASE_URL = "https://www.basketball-reference.com"
       # Implement required methods
   ```

2. **Add to CLI**:
   - Update `src/cli/menu.py` to include new sport option
   - Add scraper initialization

3. **Update configuration**:
   - Add default settings for the new sport
   - Add favorites section

4. **Add tests**:
   - Create `tests/test_nba_scraper.py`

5. **Update documentation**:
   - Add to README.md
   - Update QUICKSTART.md with examples

## Updating for Website Changes

Websites sometimes change their HTML structure. To update:

1. **Identify the change**:
   - Check error logs
   - Inspect website HTML

2. **Update selectors**:
   ```python
   # Before
   table = soup.find('table', {'id': 'old-id'})

   # After
   table = soup.find('table', {'id': 'new-id'})
   ```

3. **Test thoroughly**:
   - Test with multiple players
   - Test different stat types
   - Verify all positions work

4. **Document the change**:
   - Update comments in code
   - Note in CHANGELOG.md

## Commit Message Guidelines

Use clear, descriptive commit messages:

- **Add**: New features
  - `Add: NHL player stats support`

- **Fix**: Bug fixes
  - `Fix: Handle missing playoff stats gracefully`

- **Update**: Changes to existing features
  - `Update: Improve player search algorithm`

- **Refactor**: Code restructuring
  - `Refactor: Extract common parsing logic`

- **Docs**: Documentation changes
  - `Docs: Add NHL examples to README`

- **Test**: Test additions or changes
  - `Test: Add tests for MLB pitcher stats`

## Pull Request Guidelines

Good pull requests:

- Focus on a single feature or fix
- Include tests
- Update documentation
- Pass all existing tests
- Have clear commit messages
- Reference related issues

Pull request template:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] All tests pass
```

## Questions?

- Open an issue with the "question" label
- Check existing documentation
- Review closed issues for similar questions

## Recognition

Contributors will be recognized in:
- README.md acknowledgments
- Release notes
- Project documentation

Thank you for contributing! 🎉

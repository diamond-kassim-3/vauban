# Contributing to Vauban 🤝

We welcome contributions from the community! Vauban is designed to be modular, making it easy to add new capabilities.

## How to Contribute

1. **Fork the Repository**: Create your own copy of Vauban.
2. **Create a Branch**: `git checkout -b feature/my-new-feature`
3. **Write Code**: Add your module or fix.
4. **Test**: Run `python3 vauban.py --check` and test your changes.
5. **Push**: `git push origin feature/my-new-feature`
6. **Pull Request**: Open a PR on the main repository.

## Adding a New Module

Vauban's architecture makes adding modules easy.

### 1. Create the Script
Create your script in the appropriate `modules/` subdirectory (e.g., `modules/scan/new_vuln.py`).

### 2. Register in Orchestrator
Update `vauban.py` to call your new module.

```python
# vauban.py
def phase_scanning(self, urls_file: str):
    # ... existing calls ...
    self.logger.info("Running new vuln check...")
    self.run_python_module('modules/scan/new_vuln.py', urls_file, scan_dir)
```

### 3. Add to Installation
If your module needs external tools, add them to `install_tools.sh` and `README.md`.

## Code Style

- **Python**: PEP 8.
- **Bash**: Use `shellcheck` to verify scripts.
- **Commits**: Use clear, descriptive commit messages.

## License

By contributing, you agree that your contributions will be licensed under the MIT License of the project.

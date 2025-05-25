# Contributing to Stream notify on Bluesky

First off, thank you for considering contributing! We welcome any help to improve this project. Whether it's reporting a bug, proposing a new feature, or writing code, your contributions are valuable.

## Getting Started

### Development Environment Setup

We highly recommend using Docker for a consistent development environment.

*   **With Docker (Recommended):**
    1.  Ensure you have Docker Desktop for Windows installed and configured for Windows containers.
    2.  Follow the instructions in the "Running with Docker (Windows Containers)" section of the `README.md` to build the image and run the container.
    3.  You can develop by editing files locally, and Docker will use these updated files if you've configured volume mounts appropriately (e.g., for source code, though the provided `docker-compose.yml` primarily mounts `settings.env` and `logs`). For active development, you might want to add a source code volume mount to your `docker-compose.override.yml` or development-specific compose file.
    4.  Remember to create and configure your `settings.env` file as described in the README.

*   **Manual Python Setup:**
    1.  Ensure you have Python 3.10 or higher installed on your Windows machine.
    2.  Clone the repository: `git clone https://github.com/mayu0326/Twitch-Stream-notify-on-Bluesky.git`
    3.  Navigate to the project directory: `cd Twitch-Stream-notify-on-Bluesky`
    4.  Create a virtual environment: `python -m venv venv`
    5.  Activate the virtual environment: `.\venv\Scripts\activate`
    6.  Install dependencies: `pip install -r requirements.txt`
    7.  If a `development-requirements.txt` file exists, install those as well: `pip install -r development-requirements.txt` (This would typically include packages like `pytest`, `autopep8`, `pre-commit`).
    8.  Copy `settings.env.example` to `settings.env` and fill in your credentials.

### `settings.env` Configuration
Regardless of your setup method, you **must** create and configure a `settings.env` file with your API keys and preferences. See `settings.env.example` for details.

## How to Contribute

### Reporting Bugs

*   Before submitting a bug report, please check the [GitHub Issues](https://github.com/mayu0326/Twitch-Stream-notify-on-Bluesky/issues) to see if the bug has already been reported.
*   If you can't find an open issue addressing the problem, please [open a new one](https://github.com/mayu0326/Twitch-Stream-notify-on-Bluesky/issues/new).
*   Be sure to include a **title and clear description**, as much relevant information as possible, and steps to reproduce the issue.

### Suggesting Enhancements

*   If you have an idea for a new feature or an improvement to an existing one, please check the [GitHub Issues](https://github.com/mayu0326/Twitch-Stream-notify-on-Bluesky/issues) to see if it has already been suggested.
*   If not, feel free to [open a new issue](https://github.com/mayu0326/Twitch-Stream-notify-on-Bluesky/issues/new) to discuss your idea.

### Pull Request (PR) Process

1.  **Fork the repository** on GitHub.
2.  **Clone your fork** locally: `git clone https://github.com/YOUR_USERNAME/Twitch-Stream-notify-on-Bluesky.git`
3.  **Create a new branch** for your changes. It's good practice to base your branch off the `dev` branch: `git checkout -b your-feature-branch dev`
4.  **Make your changes** and commit them with clear, descriptive commit messages.
5.  **Ensure your code passes all tests.** (See "Running Tests" below).
6.  **Update documentation** (`README.md`, comments, etc.) if your changes require it.
7.  **Push your branch** to your fork on GitHub: `git push origin your-feature-branch`
8.  **Open a Pull Request** from your branch to the `dev` branch of the `mayu0326/Twitch-Stream-notify-on-Bluesky` repository.
9.  Provide a clear description of the changes in your PR. Reference any related issues.

## Coding Conventions

*   All Python code should adhere to **PEP 8** style guidelines.
*   We aim to use `autopep8` for automatic formatting. If it's integrated into pre-commit hooks, it will help maintain consistency.
*   Use clear and descriptive variable and function names.
*   Include comments where necessary to explain complex logic.

## Running Tests

*   To run the test suite (using `pytest`):
    ```bash
    python -m pytest tests/
    ```
*   **If using Docker for development:**
    You can run tests inside the running container:
    ```bash
    # If your docker-compose service is named 'twitch-bluesky-bot'
    docker-compose exec twitch-bluesky-bot python -m pytest tests/
    ```
    Or, if you have a shell in the container:
    ```bash
    python -m pytest tests/
    ```

## Pre-commit Hooks

This project uses `pre-commit` for managing and maintaining pre-commit hooks.
The current setup includes:
*   `ggshield` (GitGuardian for secret scanning).
*   (Potentially `autopep8` if added as discussed).

To use the hooks:
1.  Install `pre-commit`: `pip install pre-commit`
2.  Set up the git hook scripts: `pre-commit install`
3.  Now, `pre-commit` will run automatically on `git commit`!
4.  To run manually on all files: `pre-commit run --all-files`

## Code Review Process

Once you submit a Pull Request, project maintainers will review your changes. We may ask for modifications or provide feedback. We aim to review PRs in a timely manner.

## Questions?

If you have any questions, feel free to open an issue on GitHub.

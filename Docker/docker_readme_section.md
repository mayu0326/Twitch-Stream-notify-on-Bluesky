## Running with Docker (Windows Containers)

This application can be run inside a Docker container using Windows Containers. This is particularly useful for isolating the application and its dependencies.

### Prerequisites

*   **Docker Desktop for Windows:** Ensure you have Docker Desktop installed and configured to use **Windows containers**.

### Setup

1.  **Configure `settings.env`:**
    *   Before building or running the Docker container, copy the `settings.env.example` file to `settings.env` in the project root directory.
    *   Edit `settings.env` and fill in all your required credentials and configuration details (Twitch API keys, Bluesky credentials, etc.). This file will be mounted into the container.

### Recommended: Using Docker Compose

Docker Compose provides an easy way to manage the container's lifecycle. A `docker-compose.yml` file is provided in the project root.

*   **Start the application (detached mode):**
    ```bash
    docker-compose up -d
    ```
*   **View logs:**
    ```bash
    docker-compose logs -f twitch-bluesky-bot
    ```
    (You can also use `docker-compose logs -f` if it's the only service running)
*   **Stop the application:**
    ```bash
    docker-compose down
    ```
*   **Rebuild and update the application (e.g., after code changes or Dockerfile updates):**
    ```bash
    docker-compose build && docker-compose up -d --force-recreate
    ```

### Alternative: Using `docker run`

You can also build and run the container manually using Docker commands.

1.  **Build the Docker image:**
    If you want to tag the image with a custom name or ensure you're building it from scratch:
    ```bash
    docker build -t your-custom-name/twitch-bluesky-bot .
    ```
    (If you don't specify a custom name, you might rely on the tag used in `docker-compose.yml` or build without a specific tag, then use the image ID).

2.  **Run the Docker container:**
    This command mounts your local `settings.env` and `logs` directory into the container.
    ```bash
    docker run --name twitch-bluesky-bot-manual -v "%CD%\settings.env:C:\app\settings.env" -v "%CD%\logs:C:\app\logs" your-custom-name/twitch-bluesky-bot
    ```
    *   **Note:** Replace `your-custom-name/twitch-bluesky-bot` with the tag you used during the `docker build` command (or the image ID if you didn't tag it).
    *   `%CD%` refers to the current directory in Windows Command Prompt. If using PowerShell, you might need to use `$(pwd)` or provide an absolute path.
    *   To run in detached mode (in the background), add the `-d` flag:
        ```bash
        docker run -d --name twitch-bluesky-bot-manual -v "%CD%\settings.env:C:\app\settings.env" -v "%CD%\logs:C:\app\logs" your-custom-name/twitch-bluesky-bot
        ```

### Accessing Logs

*   When using either Docker Compose or `docker run` with the specified volume mounts, application logs will be persisted in the `./logs` directory in your project root on your local machine. This allows you to access log files even after the container has stopped.

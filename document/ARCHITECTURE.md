# Project Review: Stream notify on Bluesky

## 1. Core Application Logic

### main.py
- **Role:** Main entry point. Orchestrates the overall application.
- **Functionality:**
  - Initializes and runs a Flask web server (waitress for production).
  - Loads configuration, sets up logging, validates settings.
  - Manages Cloudflare tunnel lifecycle via tunnel.py.
  - Handles Twitch EventSub webhook interactions: /webhook endpoint for GET (health check) and POST (notifications).
  - Verifies webhook signatures (eventsub.verify_signature).
  - Processes Twitch webhook_callback_verification challenges.
  - Handles stream.online/stream.offline events, extracting details and posting to Bluesky via BlueskyPoster.
  - Supports per-service notification ON/OFF and template/image path selection (Twitch/YouTube/Niconico/Bluesky/Discord, etc.) via settings.env.
  - Logs revocation messages from Twitch.
  - Manages EventSub subscriptions (cleanup/create).
  - Handles WEBHOOK_SECRET rotation.
  - Ensures TWITCH_BROADCASTER_ID is numeric.
  - Integrates with GUI (Tkinter) for settings/env sync and process control.
- **Key Technologies:** Flask, Waitress, Tkinter (GUI integration)

### eventsub.py
- **Role:** Manages Twitch EventSub and API authentication.
- **Functionality:**
  - OAuth client credentials flow for Twitch app access tokens.
  - Converts usernames to broadcaster IDs.
  - Verifies HMAC SHA256 signatures (with timestamp validation).
  - Manages EventSub subscriptions (get/create/delete/cleanup).
  - Retry mechanism for API calls.
  - Timezone management.
- **Key Technologies:** Twitch API, HMAC, SHA256

### bluesky.py
- **Role:** Handles Bluesky social network interactions.
- **Functionality:**
  - BlueskyPoster class: login, image upload, post notifications (online/offline/new video) using Jinja2 templates.
  - Per-service template/image path support (Twitch/YouTube/Niconico, etc.).
  - Error handling: if template path is unset or file missing, logs error, notifies Discord, aborts posting.
  - Records all post attempts to logs/post_history.csv.
  - Retry mechanism for API calls.
- **Key Technologies:** atproto, Jinja2

### tunnel.py
- **Role:** Manages Cloudflare Tunnel (cloudflared) execution.
- **Functionality:**
  - start_tunnel(): Starts cloudflared using TUNNEL_CMD from settings.env.
  - stop_tunnel(): Terminates cloudflared process.
- **Key Technologies:** subprocess, shlex

### utils.py
- **Role:** Common utilities and decorators.
- **Functionality:**
  - Jinja2 datetime filter, .env file update (preserving comments), retry decorator, secret generation, .env reading, secret rotation, URL validation.
- **Key Technologies:** secrets, datetime, pytz, tzlocal

## 2. Configuration and Settings

### settings.env.example
- **Role:** Template for settings.env, holding all configuration and secrets.
- **Key Configurations:**
  - Twitch: TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET, TWITCH_BROADCASTER_ID
  - Bluesky: BLUESKY_USERNAME, BLUESKY_APP_PASSWORD, BLUESKY_IMAGE_PATH, BLUESKY_TEMPLATE_PATH, BLUESKY_OFFLINE_TEMPLATE_PATH, BLUESKY_YT_ONLINE_TEMPLATE_PATH, BLUESKY_YT_OFFLINE_TEMPLATE_PATH, BLUESKY_NICO_ONLINE_TEMPLATE_PATH, BLUESKY_NICO_OFFLINE_TEMPLATE_PATH, etc.
  - Webhook: WEBHOOK_SECRET, SECRET_LAST_ROTATED, WEBHOOK_CALLBACK_URL
  - Discord: discord_error_notifier_url, discord_notify_level
  - General: TIMEZONE, LOG_LEVEL, LOG_RETENTION_DAYS
  - Tunnel: TUNNEL_CMD
  - API Retry: RETRY_MAX, RETRY_WAIT

### logging_config.py
- **Role:** Configures logging system.
- **Functionality:**
  - AuditLogger (logs/audit.log), AppLogger (logs/app.log, logs/error.log, console).
  - TimedRotatingFileHandler for log rotation/retention.
  - Discord error notifications (optional).
  - Flask logger integration.
- **Key Libraries:** logging, discord_logging.handler

### Cloudflared/config.yml.example
- **Role:** Example config for cloudflared.
- **Functionality:**
  - Defines tunnel UUID, credentials, ingress rules, noTLSVerify for local service.

## 3. Supporting Files and Directories

- requirements.txt: All Python dependencies (Flask, requests, atproto, python-dotenv, Jinja2, waitress, pytz, tzlocal, python-logging-discord-handler, etc.)
- development-requirements.txt: Dev dependencies (pytest, black, autopep8, pre-commit, ggshield)
- templates/: Jinja2 templates for Bluesky posts (per-service: Twitch/YouTube/Niconico, etc.)
- images/: Images for Bluesky posts (noimage.png, etc.)
- logs/: Runtime log files (app.log, error.log, audit.log, post_history.csv)
- Docker/: Dockerfile, docker-compose.yml, docker_readme_section.md

## 4. Development and CI/CD Setup

- .github/: GitHub templates and workflows (bug report, GitGuardian secret scan, etc.)
- .pre-commit-config.yaml: pre-commit hooks (ggshield for secrets)
- pytest.ini: pytest config
- tests/: Automated tests (pytest)

## 5. Documentation Files

- README.md: Main documentation (features, setup, usage, FAQ, Docker, contribution)
- document/CONTRIBUTING.md: Contributor guidelines
- document/comprehensive_summary_japanese.md: Japanese summary
- document/consolidated_summary_japanese.md: Internal notes/recommendations
- document/contributing_readme_section.md: Contributing section snippet
- LICENSE: GPLv2

## Overall Summary

This project is a modular, robust Python bot for notifying Bluesky of Twitch/YouTube/Niconico events, with per-service template/image/webhook/API key management, GUI (Tkinter) integration, strong error handling, and comprehensive documentation/testing. Designed for extensibility and secure operation.

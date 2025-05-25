The user manual for the Stream notify on Bluesky GUI Edition has been updated to reflect the current implementation, including:

- Per-service management of notification ON/OFF, templates, images, Webhook, and API keys (Twitch/YouTube/Niconico/Bluesky/Discord/Tunnel, etc.)
- Bidirectional sync between the GUI and settings.env
- Tabbed layout, improved UI/UX, and removal of redundant/legacy UI methods
- Each service can have its own Bluesky post template, and the posting logic references the correct template per service
- Error handling: if a template path is unset or the file is missing, error log + Discord notification + abort posting
- Log file access and settings editing from the GUI
- Extensibility for future template/UI improvements

Please refer to the Japanese manual (Manual.ja) for a detailed step-by-step guide.

---

User Manual: Stream notify on Bluesky - GUI Edition

1. Introduction
This GUI is designed to make setup and management easier, especially for users who prefer not to edit config files directly. You can:
- Run the initial setup wizard
- Start/stop/restart the bot
- Monitor status of Twitch/YouTube/Niconico/Bluesky/Tunnel
- Customize notification templates/images/webhook/API keys per service
- Edit settings after setup
- Access log files

2. Prerequisites
- Python 3.10+
- cloudflared.exe (in PATH or specify full path in GUI)
- All application files (see README)

3. First-Time Setup
- Run: python app_gui.py
- The wizard will guide you through account/API key input, per-service notification/template/image selection, and saving settings

4. Main Window
- Start/Stop/Restart bot
- Status display for all services
- Edit settings
- Per-service template/image customization
- Log file access

5. Notification Customization
- Enable/disable notifications, select template/image/webhook/API key per service
- Files are copied to templates/images and path saved to settings.env
- See README for template variables

6. Editing Settings After Setup
- Use the settings editor from the main window
- Changes are saved to settings.env and may require bot restart

7. Bot Control
- Start/Stop/Restart buttons manage the bot process
- Status display shows connection/errors for each service

8. Log File Access
- Open app.log, audit.log, post_history.csv from the GUI

9. Error Handling
- If template path is unset or file missing: error log + Discord notification + abort posting
- Major errors/status are shown in the GUI

10. Extensibility
- Per-service management, future template/UI improvements supported

---


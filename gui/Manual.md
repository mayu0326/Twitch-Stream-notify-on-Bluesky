The user manual I created is the text compiled in our conversation. I will now present the complete manual in one message for your convenience.

User Manual: Stream notify on Bluesky - GUI Edition

1. Introduction
Welcome to the GUI Edition of the Stream notify on Bluesky bot!

This graphical user interface (GUI) is designed to make setting up and managing the bot easier, especially if you prefer a visual interface over editing configuration files directly in a text editor. The GUI allows you to:

Perform the initial setup of the bot through a step-by-step wizard.
Start and stop the bot.
Monitor the bot's status and key integrations (Twitch, Bluesky, Tunnel).
Customize notification messages by selecting your own templates.
Attach images to your online notifications by selecting image files.
Easily edit core settings after the initial setup.
Access important log files with a simple click.
This manual will guide you through the installation, setup, and usage of the GUI application.

Intended Audience: This manual is for you if you wish to use the provided GUI for setup and management of the Stream notify on Bluesky bot.

2. Prerequisites
Before you can use the GUI application, please ensure you have the following software and files set up:

Software:

Python: Version 3.10 or newer is recommended. If you don't have Python installed, you can download it from python.org. During installation, make sure to check the box that says "Add Python to PATH."
Cloudflare Tunnel Client (cloudflared.exe): This is required for the bot to receive webhook notifications from Twitch.
Download cloudflared.exe from the Cloudflare Zero Trust dashboard (look for "Downloads" under the "Connectors" section usually, or search "cloudflared download" on the Cloudflare website).
It's highly recommended to place cloudflared.exe in a directory that is part of your system's PATH environment variable. Alternatively, you will need to provide the full path to cloudflared.exe when configuring the "Tunnel Command" in the GUI setup.
You also need a configured Cloudflare Tunnel that points to your local machine (this setup is done via the Cloudflare dashboard and cloudflared command line, prior to using this bot's GUI for tunnel command input).
Application Files:

You should have the complete set of application files for the bot, including all Python scripts and supporting files. These typically include:

GUI Scripts:
app_gui.py (the main GUI application you will run)
setup_wizard.py
main_control_frame.py
settings_editor_dialog.py
notification_customization_frame.py
Core Bot Logic Scripts:
main.py
utils.py
bluesky.py
eventsub.py
tunnel.py
logging_config.py
version.py
Supporting Files & Directories:
templates/ directory containing:
default_template.txt (default template for online notifications)
offline_template.txt (default template for offline notifications)
images/ directory containing:
noimage.png (default image if none is selected or if selected image is not found)
settings.env.example (example settings file; the GUI will help you create your actual settings.env file).
Ensure all these files are kept together in the same main application folder.

3. Getting Started: First-Time Setup
If you are running the application for the first time, or if your settings.env configuration file is missing or incomplete, the GUI will automatically guide you through an Initial Setup Wizard.

Launching the Application:

Navigate to the folder where you have all the application files.
Open a command prompt or terminal window in this folder.
Run the GUI application using Python:
python app_gui.py
(If app_gui.py is not the main executable name, use the correct one provided).
The Initial Setup Wizard (SetupWizard):

The wizard will appear as a series of screens (steps) asking for necessary information.

Step 1: Welcome

Content: A brief welcome message explaining that the wizard will help you configure the bot.
Action: Click the "Next" button to proceed.
Step 2: Twitch Settings

Purpose: Configure the connection to your Twitch account and the channel you want to monitor.
Fields:
Twitch Client ID: Enter your Twitch Application's Client ID. You can get this from the Twitch Developer Console. (Required)
Twitch Client Secret: Enter your Twitch Application's Client Secret. This is also found in the Twitch Developer Console. (Required)
Twitch Broadcaster ID/Username: Enter the Twitch username or numeric User ID of the streamer whose broadcasts you want to notify about. If you provide a username, the bot will attempt to convert it to a User ID automatically when it starts. (Required)
Navigation:
Click "Previous" to return to the Welcome screen.
Click "Next" to proceed after filling in the details. You must fill in all required fields.
Step 3: Bluesky Settings

Purpose: Configure the connection to your Bluesky account where notifications will be posted.
Fields:
Bluesky Username: Your full Bluesky handle (e.g., yourname.bsky.social). (Required)
Bluesky App Password: An App Password generated from your Bluesky account settings. Do not use your main Bluesky password. You can generate App Passwords in Bluesky under Settings -> Advanced -> App Passwords. (Required)
Navigation:
Click "Previous" to return to Twitch Settings.
Click "Next" to proceed.
Step 4: Webhook & Tunnel Settings

Purpose: Configure how the bot receives live notifications from Twitch. This usually involves a tunnel service like Cloudflare Tunnel.
Fields:
Webhook Callback URL: This is the public URL that Twitch will send notifications to. If you are using Cloudflare Tunnel, it will look something like https://your-tunnel-subdomain.cfargotunnel.com/webhook or a custom domain you've configured for your tunnel. (Required)
Tunnel Command (Optional): If you want the bot to attempt to start your tunnel (e.g., cloudflared) automatically, enter the full command here.
Example for cloudflared: C:\path o\cloudflared.exe tunnel --config C:\path o\your\config.yml run <your-tunnel-name>
If you manage your tunnel externally (e.g., it's always running, or you start it manually), you can leave this blank.
Navigation:
Click "Previous" to return to Bluesky Settings.
Click "Next" to proceed.
Step 5: Core Notification Toggles

Purpose: Set initial preferences for which notifications are active.
Fields:
Notify on Stream Online: Check this box if you want to send a Bluesky post when the stream goes live. (Default: Enabled)
Notify on Stream Offline: Check this box if you want to send a Bluesky post when the stream goes offline. (Default: Disabled)
Note: The actual template files and images used for these notifications will initially be set to defaults (templates/default_template.txt, images/noimage.png, etc.). You can customize these in detail from the main application window after completing this initial setup.
Navigation:
Click "Previous" to return to Webhook & Tunnel Settings.
Click "Next" to proceed.
Step 6: Summary & Saving

Content: This screen will display a summary of the settings you've entered (passwords will be masked). Review these carefully.
Navigation:
Click "Previous" if you need to change any of the displayed settings.
Click the "Save Settings" button to save your configuration. This will create or update a file named settings.env in your application folder with all the information you've provided.
Completion: After saving, the wizard will close, and the main application window should appear. If there were any issues saving, an error message should be displayed.
Once the Initial Setup Wizard is complete, the application will store your settings, and you typically won't need to go through the full wizard again unless your settings.env file is deleted or becomes corrupted. You'll be able to edit these settings later from the main application window.

4. The Main Application Window
Once you've completed the initial setup (or if setup was already complete), the main application window will appear. This is your central hub for controlling the bot, monitoring its status, and accessing further customization options.

The main window is designed to be straightforward. Here's an overview of its key sections (based on the MainControlFrame and how app_gui.py is structured):

A. Bot Controls Section:

This area allows you to manage the operational state of the bot.

Start Bot Button:
Click this button to initialize and start the bot.
The bot will attempt to connect to Twitch, Bluesky, start the tunnel (if configured), and begin listening for stream events.
Once clicked, this button will typically become disabled, and the "Stop Bot" button will become active.
Stop Bot Button:
Click this button to gracefully shut down the bot.
This will stop the webhook server, terminate the tunnel process (if started by the bot), and perform any other cleanup.
Once clicked, this button will become disabled, and the "Start Bot" button will become active.
Restart Bot Button:
Click this button to first stop the bot (if it's running) and then immediately start it again. This is useful if you've made configuration changes that require a full restart.
B. Status Display Section:

This section provides real-time feedback on the bot's operational status and its connections to various services.

Bot Status:
Displays the overall state of the bot. Common statuses include:
Stopped: The bot is not running.
Starting...: The bot is in the process of initializing.
Running: The bot is active and monitoring for stream events.
Stopping...: The bot is in the process of shutting down.
Error: [message]: An error occurred. Check the logs for more details. The message might give a hint about the error.
The status text color may change (e.g., green for running, red for stopped/error) to provide a quick visual cue.
Twitch Status:
Indicates the status of the connection to Twitch services (e.g., EventSub subscriptions, API token validity).
Examples: Connected, Disconnected, Token Error.
Bluesky Status:
Indicates the status of the connection to Bluesky (e.g., login status).
Examples: Ready, Login Error.
Tunnel Status:
Indicates the status of the webhook tunnel (e.g., Cloudflare Tunnel).
Examples: Active, Inactive, Error.
C. Accessing Other Features (via Tabs or Menus):

The main window also serves as the entry point to other important functionalities, which are typically organized into tabs or accessible via a menu bar.

Notification Customization Tab/Section (NotificationCustomizationFrame):
This is where you can change the templates used for Bluesky posts and the image attached to online notifications.
(Details in Section 5: Customizing Notifications).
Log Files Section:
This section contains buttons to directly open the bot's log files.
(Details in Section 8: Accessing Log Files).
File Menu (Top of the window):
File -> Edit Settings:
Opens the "Settings Editor" dialog, allowing you to change the configurations you made during the initial setup (like API keys, URLs, etc.).
(Details in Section 6: Editing Settings After Setup).
File -> Exit:
Closes the GUI application. If the bot is running, it will attempt to stop it gracefully before exiting.
This main window provides all the essential tools for the day-to-day operation and management of your Twitch notification bot.

5. Customizing Notifications (NotificationCustomizationFrame)
The GUI provides an easy way to customize the appearance and content of the notifications posted to Bluesky. This is typically done in a dedicated "Notification Customization" tab or section within the main application window.

Here’s how to use these features:

Accessing Notification Customization:

Look for a tab or section labeled "Notification Customization" (or similar) in the main application window.
A. Online Notification Settings:

This section allows you to control notifications for when a stream goes live.

Enable/Disable Online Notifications:

UI Element: A checkbox labeled "Notify on Stream Online" (or similar).
Action: Check this box to enable notifications when the monitored Twitch channel goes live. Uncheck it to disable them. Changes are typically saved automatically.
Changing the Online Notification Template:

Current Template Display: A label shows the path to the currently active template file for online notifications (e.g., templates/default_template.txt).
UI Element: A button labeled "Change Online Template..." (or similar).
Action:
Clicking this button will open a file dialog, allowing you to browse your computer for a .txt file.
Select the text file you want to use as your new template for online notifications.
File Handling: Upon selection, the application will:
Copy your chosen template file into the application's templates/ sub-directory. To avoid conflicts and preserve your original file, it might be renamed (e.g., user_online_template_<timestamp>.txt).
Update the settings.env file to point to this new template path.
The "Current Template Display" label in the GUI will update to show the path of the newly active template.
Note on Template Variables: Refer to the bot's main README or documentation for the list of variables (like {title}, {username}, {url}, {category}) you can use in your template file to have stream-specific information automatically inserted.
Changing the Image for Online Notifications:

Current Image Display: A label shows the path to the image currently used for online notifications (e.g., images/noimage.png). Some GUIs might also show a small preview of the image.
UI Element: A button labeled "Change Image..." (or similar).
Action:
Clicking this button opens a file dialog, allowing you to browse for image files (typically PNG, JPG, or static GIF).
Select the image file you want to attach to your online stream notifications.
File Handling: Upon selection, the application will:
Copy your chosen image file into the application's images/ sub-directory. It might be renamed (e.g., user_online_image_<timestamp>.png) to ensure uniqueness.
Update the settings.env file to point to this new image path.
The "Current Image Display" label (and any preview) will update.
UI Element: A button labeled "Clear Image" (or similar).
Action: Clicking this will reset the image path to the default (e.g., images/noimage.png) or an empty value, meaning no custom image (or the default 'no image' image) will be sent. The settings.env file will be updated accordingly.
B. Offline Notification Settings:

This section allows you to control notifications for when a stream goes offline.

Enable/Disable Offline Notifications:

UI Element: A checkbox labeled "Notify on Stream Offline" (or similar).
Action: Check this box to enable notifications when the monitored Twitch channel goes offline. Uncheck it to disable them. Changes are typically saved automatically.
Changing the Offline Notification Template:

Current Template Display: A label shows the path to the currently active template file for offline notifications (e.g., templates/offline_template.txt).
UI Element: A button labeled "Change Offline Template..." (or similar).
Action:
This works just like changing the online template. Select a .txt file.
File Handling: The application will copy it to the templates/ directory (e.g., as user_offline_template_<timestamp>.txt) and update settings.env.
The display label will update.
Important Notes on File Handling:

The GUI is designed to manage copies of your selected template and image files within its own templates/ and images/ folders. This ensures that the bot always has access to the files it needs, even if you move or delete your original copies.
When you select a new file, the application updates its settings to use the new copied file.
Ensure the application has write permissions to its own templates/ and images/ subdirectories.
By using these customization options, you can tailor the bot's Bluesky posts to better fit your style and information preferences.

6. Editing Settings After Setup (SettingsEditorDialog)
After you have completed the initial setup, you may need to change some of your core configurations, such as API keys, user IDs, or URLs. The GUI provides a "Settings Editor" dialog for this purpose.

Accessing the Settings Editor:

In the main application window, look for a "File" menu at the top.
Click on "File," and then select "Edit Settings" (or a similarly named option).
This will open the "Settings Editor" dialog window. This window is typically modal, meaning you'll need to interact with it (save or cancel) before you can use the main application window again.
Using the Settings Editor Dialog:

The Settings Editor dialog will look very similar in structure to some parts of the Initial Setup Wizard, presenting input fields for various settings.

Loading Settings: When the dialog opens, it will automatically load your current settings from the settings.env file and populate them into the respective fields.

Editable Fields: The dialog is organized into sections, typically:

Twitch Settings:
Twitch Client ID
Twitch Client Secret (displayed as asterisks **** for security)
Twitch Broadcaster ID/Username
Bluesky Settings:
Bluesky Username
Bluesky App Password (displayed as asterisks ****)
Webhook & Tunnel Settings:
Webhook Callback URL
Tunnel Command (if you use the bot to manage your tunnel)
Making Changes:

Simply click into any field and type to make your desired changes.
For password fields, even though they are masked, you can type the new password directly.
Saving Changes:

Once you are satisfied with your changes, click the "Save" button (or "Apply"/"OK").
The application will validate the inputs (e.g., check for empty required fields).
If validation passes, the new settings will be written to your settings.env file, overwriting the previous values for those specific settings.
A confirmation message (e.g., "Settings saved successfully!") should appear, and the dialog will close.
Important: Depending on the settings changed (e.g., API keys, tunnel command), you may need to restart the bot for these changes to take full effect. The application might prompt you if a restart is recommended.
Cancelling Changes:

If you want to close the dialog without saving any modifications you've made, click the "Cancel" button.
The dialog will close, and your settings.env file will remain unchanged.
When to Edit Settings:

If your API keys or app passwords for Twitch or Bluesky have changed or expired.
If you want to monitor a different Twitch channel.
If your Webhook Callback URL changes (e.g., your tunnel subdomain changes).
If you need to update the command used to start your tunnel.
Regularly reviewing these settings, especially if the bot encounters connection errors, can be a useful troubleshooting step.

7. Controlling the Bot
The main application window's "Bot Controls" section provides the primary interface for managing the bot's operation.

Start Bot Button:

Action: Click this button to initiate the bot.
Process:
The GUI will signal the backend to begin its startup sequence.
The "Bot Status" will typically change to "Starting...".
The bot will perform necessary initializations: validating settings, connecting to Twitch and Bluesky, starting the webhook tunnel (if configured), and subscribing to Twitch events.
If all steps are successful, the "Bot Status" will change to "Running" (often with a green indicator), and other status fields (Twitch, Bluesky, Tunnel) should reflect an active state.
The "Start Bot" button will become disabled, and "Stop Bot" / "Restart Bot" will be enabled.
If startup fails: The "Bot Status" will show an "Error" message. Check the application logs for details (see Section 8).
Stop Bot Button:

Action: Click this button to shut down the bot.
Process:
The GUI will signal the backend to begin its shutdown sequence.
The "Bot Status" will change to "Stopping...".
The bot will stop its webhook server, unsubscribe from Twitch events (if applicable), and terminate the tunnel process (if it was started by the bot).
Once shutdown is complete, the "Bot Status" will change to "Stopped" (often with a red indicator).
The "Stop Bot" and "Restart Bot" buttons will become disabled, and "Start Bot" will be enabled.
Restart Bot Button:

Action: Click this button to perform a stop sequence followed immediately by a start sequence.
Process: This is equivalent to clicking "Stop Bot" and then "Start Bot."
Use Case: Useful if you've made configuration changes that you know require a full bot restart, or if the bot seems to be in an unresponsive state.
Always observe the "Bot Status" display for feedback on these operations.

8. Accessing Log Files
The bot maintains several log files that can be very helpful for understanding its activity, diagnosing issues, or simply reviewing its history. The GUI provides direct buttons to open these files using your system's default application for text files or CSV files.

Locating the Log Access Buttons:

In the main application window, look for a section or a set of buttons labeled "Log Files" (or similar). This might be part of the main control view or a separate tab/utility section.
Available Log Files and How to Open Them:

Application Log (app.log):

Content: This is the main operational log. It records detailed information about the bot's startup, when it checks for stream status, errors encountered (e.g., API connection problems, issues posting to Bluesky), and general activity. This is usually the first place to look if the bot isn't behaving as expected.
How to Open: Click the button labeled "View Application Log" (or similar).
Audit Log (audit.log):

Content: This log records security-sensitive or critical operations, such as when EventSub subscriptions are created or deleted, or when the WEBHOOK_SECRET is rotated.
How to Open: Click the button labeled "View Audit Log" (or similar).
Post History (post_history.csv):

Content: This file records a history of every notification the bot has attempted to send to Bluesky. It's a CSV (Comma Separated Values) file, best viewed in a spreadsheet program (like Excel, LibreOffice Calc, Google Sheets). It typically includes:
Date and Time of the post attempt.
Event Type (e.g., "online", "offline").
Stream Title.
Stream Category.
URL of the stream/post.
Success status (whether the post to Bluesky was successful or failed).
How to Open: Click the button labeled "View Post History" (or similar).
What Happens When You Click a Log Button:

The application will try to open the selected log file using the default program your Windows system has associated with .log files (usually a text editor like Notepad) or .csv files (usually a spreadsheet program).
If a Log File Doesn't Exist:
If the bot hasn't run enough to generate a particular log, or if a log file has been deleted, it might not exist.
In this case, the GUI will display a pop-up message, such as "File Not Found: The log file app.log was not found."
Using the Logs:

When troubleshooting, examine the app.log for error messages around the time the issue occurred.
The post_history.csv is useful for confirming whether specific notifications were sent successfully.
The audit.log is typically for more advanced checks or understanding changes to critical components.
Being able to easily access these logs directly from the GUI can significantly speed up the process of monitoring and troubleshooting the bot.

9. Basic Troubleshooting
Even with a GUI, you might occasionally encounter issues. This section provides tips on how to diagnose and resolve some common problems, primarily using the information and tools available within the GUI application.

Issue: Bot does not start or shows "Error" status immediately.

Check Logs:
Use the "View Application Log" button in the GUI to open app.log. Look for error messages at the end of the file. These often provide specific reasons for startup failures (e.g., invalid API keys, network issues, problems with settings.env).
Verify Settings:
Open the Settings Editor (File -> Edit Settings). Double-check all your API keys, secrets, usernames, and URLs. A small typo can prevent the bot from connecting.
Ensure TWITCH_BROADCASTER_ID is correct for the channel you intend to monitor.
Ensure WEBHOOK_CALLBACK_URL is correctly entered and accessible.
Prerequisites:
Ensure Python is installed correctly.
If using the bot to manage the tunnel, ensure cloudflared.exe is accessible and the TUNNEL_CMD is correct. Try running the TUNNEL_CMD manually in a command prompt to see if it works.
Issue: Bot is "Running" but notifications are not being posted to Bluesky.

Check Bot Status Displays:
Look at the "Twitch Status," "Bluesky Status," and "Tunnel Status" in the main GUI window. An error in one of these (e.g., "Twitch Token Error," "Bluesky Login Error," "Tunnel Inactive") will pinpoint where the problem lies.
Check Post History:
Use the "View Post History" button to open post_history.csv. Look for recent entries. The "Success" column will tell you if posts are failing. If they are, the other columns might give context.
Check Application Log:
app.log will likely contain more detailed error messages related to failed posting attempts (e.g., specific API error responses from Bluesky).
Bluesky Account:
Ensure your Bluesky account is not locked or restricted.
Verify the Bluesky App Password is still valid.
Notification Templates/Image:
If you recently changed templates or images, ensure the files are valid and accessible in the templates/ and images/ folders. An error in a template (e.g., referencing a non-existent variable) could cause posting to fail. The app.log might indicate template rendering errors.
Issue: Twitch status shows an error or bot doesn't seem to detect when a stream goes live/offline.

Check Twitch Settings:
In the Settings Editor, verify TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET, and TWITCH_BROADCASTER_ID.
Check Webhook URL and Tunnel:
The WEBHOOK_CALLBACK_URL must be publicly accessible for Twitch to send notifications. If your tunnel is down or misconfigured, the bot won't receive events. Check the "Tunnel Status" in the GUI.
Refer to Cloudflare's dashboard for your tunnel's health.
Check Application Log:
Look for errors related to EventSub subscription creation or webhook signature verification.
Issue: GUI shows "Tunnel Inactive" or "Tunnel Error".

Verify TUNNEL_CMD: If the bot is meant to start the tunnel, ensure the command in the Settings Editor is correct and cloudflared.exe (or your chosen tunnel client) is working.
Manual Check: Try running your tunnel command manually in a terminal to see if it reports any errors.
Cloudflare Configuration: Check your Cloudflare dashboard to ensure the tunnel itself is correctly configured and active.
Issue: "File Not Found" when trying to view a log.

This simply means the bot hasn't generated that specific log file yet (e.g., post_history.csv if no posts have been attempted) or it was deleted. This is usually not an error in itself.
Issue: Selected template or image not being used.

Verify Customization: In the "Notification Customization" section of the GUI, ensure the correct template/image paths are displayed as active.
Restart Bot: Some changes, especially to paths, might require a bot restart to be fully applied, though the GUI aims to apply them immediately by updating settings.env. If in doubt, restart the bot.
General Tip: Restart the Bot.

If you've made configuration changes or if the bot seems stuck, try stopping and starting it using the GUI controls. This can often resolve temporary issues.
If problems persist, the detailed error messages in app.log are your best resource for further investigation.


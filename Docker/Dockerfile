# Base Image: Windows Server Core with Python 3.10
FROM mcr.microsoft.com/windows/servercore/python:3.10-windowsservercore-ltsc2022

# Set the working directory in the container
WORKDIR C:/app

# Download and install cloudflared.exe
SHELL ["powershell", "-Command"]
RUN $ErrorActionPreference = 'Stop';     $ProgressPreference = 'SilentlyContinue';     New-Item -ItemType Directory -Force -Path C:/app/bin;     Invoke-WebRequest -Uri https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe -OutFile C:/app/bin/cloudflared.exe

# Add cloudflared directory to PATH
ENV PATH C:/app/bin;%PATH%

# Copy requirements.txt from project root (build context) to C:/app/ in the image
COPY requirements.txt C:/app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r C:/app/requirements.txt

# Copy application files and directories from project root (build context) to C:/app/ in the image
COPY main.py C:/app/
COPY bluesky.py C:/app/
COPY eventsub.py C:/app/
COPY tunnel.py C:/app/
COPY utils.py C:/app/
COPY logging_config.py C:/app/
COPY version.py C:/app/

COPY templates/ C:/app/templates/
COPY settings.env.example C:/app/settings.env

# Command to run the application
CMD ["python", "main.py"]

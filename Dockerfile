# Use an official Python runtime as a parent image for Windows Server Core
FROM mcr.microsoft.com/windows/servercore/python:3.10-windowsservercore-ltsc2022

# Set the working directory in the container
WORKDIR C:/app

# Download cloudflared.exe
SHELL ["powershell", "-Command"]
RUN $ErrorActionPreference = 'Stop';         $ProgressPreference = 'SilentlyContinue';         New-Item -ItemType Directory -Force -Path C:/app/bin;         Invoke-WebRequest -Uri https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe -OutFile C:/app/bin/cloudflared.exe

# Add cloudflared directory to PATH
ENV PATH C:/app/bin;%PATH%

# Copy the requirements file into the container at C:/app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's source code from the host to the image's filesystem.
COPY . .

# Copy settings.env.example to settings.env
# The user will be expected to mount their actual settings.env or pass environment variables
COPY settings.env.example settings.env

# Run main.py when the container launches
CMD ["python", "main.py"]

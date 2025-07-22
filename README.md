# PDF Watermarker web app

A lightweight and privacy-friendly tool to watermark PDF files via a modern web UI.  
Built with Flask and deployed in a self-contained Docker container.

[Docker Hub](https://hub.docker.com/r/wemubis0/filigrane-pdf)

<br>

## Features

- Live preview before downloading  
- Add watermark to multiple PDFs  
- Multi-user safe: unique filenames per session  
- Automatic cleanup every 24h (2:00 AM via cron)  
- Secrets stored outside the image (via volume)

<br>

## How to run with Docker

### 1. Clone the repo

```bash
git clone https://github.com/Wemubis/filigrane-pdf.git
cd filigrane-pdf
```

### 2. Generate a secure secret key (if not done)
```bash
mkdir -p <PATH>
python3 -c "import secrets; print(secrets.token_hex(32))" > <PATH>/.secret.key
```

You can store it anywhere on your computer. The app requires this file to run.

### 3. Build the image
```bash
docker build -t filigrane-pdf .
```

### 4. Run the container (with mounted secret.key)
```bash
docker run -d -p <PORT>:8080 \
  -v <ABSOLUTE_PATH>/.secret.key:/app/.secret.key:ro \
  --name filigrane-app filigrane-pdf
```

Now open: http://<PORT>:8080

#### Auto-Cleanup

Files in /uploads and /watermarked are deleted daily at 2:00 AM<br>
Scheduled via built-in cron in the container

#### Stop & Remove
```bash
docker stop filigrane-app
docker rm filigrane-app
```
<br><br>

> IMPORTANT NOTES
>
>- `.secret.key` is required and must be mounted at `/app/.secret.key`
>- If missing, the app will not start

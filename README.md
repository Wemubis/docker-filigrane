# PDF Watermarker web app

A lightweight and privacy-friendly tool to watermark PDF files via a modern web UI.  
Built with Flask and deployed in a self-contained Docker container.

[Docker Hub](https://hub.docker.com/r/wemubis0/filigrane-pdf)

<br>

## Features

- Live preview before downloading  
- Add watermark to multiple PDFs  
- Multi-user safe: unique filenames per session  
- Automatic cleanup every 6h 
- Secrets stored outside the image (via volume)

<br>

## How to run with Docker

### 1. Clone the repo

```bash
git clone https://github.com/Wemubis/docker-watermarker
cd docker-watermarker
```

### 2. Generate a secure secret key (if not done)
```bash
mkdir -p <PATH>
python3 -c "import secrets; print(secrets.token_hex(32))" > <PATH>/.secret.key
```

You can store it anywhere on your computer. The app requires this file to run.

### 3. Build the image
```bash
docker build -t pdf-watermarker .
```

### 4. Run the container (with mounted secret.key)
```bash
docker run -d -p <PORT>:8080 \
  --name watermark-app \
  --restart unless-stopped \
  -v <ABSOLUTE_PATH>/.secret.key:/app/.secret.key:ro \
  pdf-watermarker
```

Now open: http://<PORT>:8080

#### Auto-Cleanup

Files modified more than 2h ago in /uploads and /watermarked are deleted every 6h<br>
Scheduled via built-in cron in the container

#### Stop & Remove
```bash
docker stop watermark-app
docker rm watermark-app
```
<br><br>

> IMPORTANT NOTES
>
>- `.secret.key` is required and must be mounted at `/app/.secret.key`
>- If missing, the app will not start

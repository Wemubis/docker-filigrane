#!/bin/bash
find /app/uploads -type f -mtime +0 -delete
find /app/watermarked -type f -mtime +0 -delete

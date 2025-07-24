#!/bin/bash

find /app/uploads -type f -mmin +120 -delete
find /app/watermarked -type f -mmin +120 -delete

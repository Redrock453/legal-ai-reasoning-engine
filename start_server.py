#!/usr/bin/env python3
import sys
import os

# Change to app directory
os.chdir('/root/backend')

# Run uvicorn
os.execv(sys.executable, [sys.executable, '-m', 'uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8001'])
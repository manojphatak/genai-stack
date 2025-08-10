# GenAI Stack Debugging Guide

## Quick Start Debugging

### 1. Normal Execution (No Debugger)
```bash
# Current setup - runs normally without waiting for debugger
docker-compose up api
```

### 2. Normal Mode without Health Check Spam
```bash
# Runs normally but disables health check to avoid HTTP spam
docker-compose -f docker-compose.yml -f docker-compose.no-healthcheck.yml up api
```

### 3. Debug Mode (Wait for debugger)
```bash
# Set DEBUG_WAIT=true to make container wait for debugger
docker-compose -f docker-compose.yml -f docker-compose.debug.yml up api
```

## Environment Variables
- `DEBUG_MODE=true` - Enables debugger on port 5678
- `DEBUG_WAIT=false` - Runs normally, can attach debugger anytime
- `DEBUG_WAIT=true` - Waits for debugger before starting

## Health Check Issue
The health check runs every 5s creating HTTP requests to `/`. To disable:
- Use `docker-compose.no-healthcheck.yml` override
- Or use `docker-compose.debug.yml` which also disables it

## VS Code Debug Configuration
Use "Remote Debug FastAPI Container" configuration to attach.

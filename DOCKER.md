# Docker Deployment Guide

This guide explains how to run the Academic Program Reporting Dashboard using Docker Compose.

## Prerequisites

- Docker (20.10+)
- Docker Compose (2.0+)
- Asana Personal Access Token and Project GID

## Quick Start

### 1. Clone and Configure

```bash
# Copy the environment file
cp .env.example .env

# Edit .env with your Asana credentials
nano .env  # or use your preferred editor
```

### 2. Configure Asana Credentials

Edit the `.env` file with your actual values:

```env
ASANA_ACCESS_TOKEN=your_personal_access_token_here
ASANA_PROJECT_GID=your_project_id_here
ASANA_FIELD_RESEARCHERS_COUNT=field_gid_here
ASANA_FIELD_STUDENTS_COUNT=field_gid_here
ASANA_FIELD_HARDWARE_TYPES=field_gid_here
ASANA_FIELD_POINT_OF_CONTACT=field_gid_here
```

**How to get these values:**

1. **Personal Access Token:** [Asana Developer Console](https://app.asana.com/0/developer-console) → Create new token

2. **Project GID:** Open your Asana project in browser. The URL will be `https://app.asana.com/0/PROJECT_GID/...`

3. **Custom Field GIDs:** Run this command after setting your token and project GID:
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" \
     "https://app.asana.com/api/1.0/projects/YOUR_PROJECT_GID?opt_fields=custom_field_settings.custom_field.name,custom_field_settings.custom_field.gid"
   ```

### 3. Build and Run

```bash
# Production (ACME + OAuth2 reverse proxy)
docker compose up -d

# Local (no OAuth2, direct ports)
docker compose -f docker-compose.local.yml up -d

# View logs
docker compose logs -f

# Stop services
docker compose down
```

### 4. Access the Application

- **Production Dashboard:** https://<FQDN>
- **Local Frontend:** http://localhost:8080
- **Local Backend API:** http://localhost:8000

## Production Deployment

Production uses the built-in Nginx reverse proxy with ACME and OAuth2.

### Required Environment Variables

- `FQDN` (publicly resolvable hostname)
- `ACME_CONTACT`
- `OAUTH2_PROXY_CLIENT_ID`
- `OAUTH2_PROXY_CLIENT_SECRET`
- `OAUTH2_PROXY_COOKIE_SECRET`
- `OAUTH2_PROXY_AZURE_TENANT` (if using Entra ID)

### Start Production

```bash
make setup  # copies .env.example to .env
make up
```

### Database Persistence

The database is stored in `./backend/data/` directory and is mounted as a volume. This ensures data persists across container restarts.

## Docker Commands

```bash
# Build without cache
docker compose build --no-cache

# Rebuild and restart
docker compose up -d --build

# View running containers
docker compose ps

# Stop and remove containers
docker compose down

# Stop and remove containers + volumes
docker compose down -v

# View backend logs
docker compose logs backend

# View frontend logs
docker compose logs frontend

# Execute command in backend container
docker compose exec backend bash

# Restart a specific service
docker compose restart backend
```

## Troubleshooting

### Backend fails to start

Check the logs:
```bash
docker compose logs backend
```

Common issues:
- Missing or invalid Asana credentials in `.env`
- Port 8000 already in use

### Frontend can't connect to backend

1. Check if backend is running:
   ```bash
   docker compose ps
   ```

2. Verify the API URL was set correctly during build:
   ```bash
   docker compose build --no-cache frontend
   ```

### Database issues

To reset the database:
```bash
docker compose down
rm -rf backend/data/academic_program.db
docker compose up -d
```

## Environment Variables

All environment variables are defined in the `.env` file at the project root:

| Variable | Description | Required |
|----------|-------------|----------|
| `ASANA_ACCESS_TOKEN` | Asana personal access token | Yes |
| `ASANA_PROJECT_GID` | Asana project ID | Yes |
| `ASANA_FIELD_RESEARCHERS_COUNT` | Custom field GID for researcher count | Yes |
| `ASANA_FIELD_STUDENTS_COUNT` | Custom field GID for student count | Yes |
| `ASANA_FIELD_HARDWARE_TYPES` | Custom field GID for hardware types | Yes |
| `ASANA_FIELD_POINT_OF_CONTACT` | Custom field GID for point of contact | Yes |
| `CORS_ORIGINS` | Comma-separated allowed origins | Yes |
| `ACME_DIRECTORY_URL` | ACME endpoint for certificates | Yes |
| `ACME_CONTACT` | Contact email for ACME certificates | Yes |
| `FQDN` | Public hostname for TLS certs | Yes |
| `ADDITIONAL_HOSTNAMES` | Comma-separated extra hostnames | No |
| `OAUTH2_PROXY_PROVIDER` | OAuth2 provider (entra-id, oidc, etc.) | Yes |
| `OAUTH2_PROXY_AZURE_TENANT` | Entra ID tenant ID | Yes (Entra) |
| `OAUTH2_PROXY_OIDC_ISSUER_URL` | OIDC issuer URL | Yes |
| `OAUTH2_PROXY_CLIENT_ID` | OAuth2 client ID | Yes |
| `OAUTH2_PROXY_CLIENT_SECRET` | OAuth2 client secret | Yes |
| `OAUTH2_PROXY_COOKIE_SECRET` | OAuth2 cookie secret | Yes |
| `OAUTH2_PROXY_REDIRECT_URL` | OAuth2 redirect URL | Yes |
| `OAUTH2_PROXY_EMAIL_DOMAINS` | Allowed email domains | No |
| `OAUTH2_PROXY_COOKIE_SECURE` | Secure cookie flag | No |
| `OAUTH2_PROXY_COOKIE_SAMESITE` | Cookie SameSite mode | No |
| `OAUTH2_PROXY_WHITELIST_DOMAINS` | Allowed redirect domains | No |
| `OAUTH2_PROXY_COOKIE_DOMAINS` | Cookie domains | No |
| `OAUTH2_PROXY_SKIP_PROVIDER_BUTTON` | Skip provider selection | No |
| `OAUTH2_PROXY_INSECURE_OIDC_SKIP_ISSUER_VERIFICATION` | Skip issuer verification | No |

## Architecture

```
┌────────────────────────────┐
│   Nginx + ACME + OAuth2    │
│   (Ports 80/443)           │
└────────────┬───────────────┘
             │ HTTPS
             │
     ┌───────▼────────┐
     │   Frontend     │
     │   (Nginx:80)   │
     └───────┬────────┘
             │
     ┌───────▼────────┐
     │   Backend      │
     │   (FastAPI)    │
     │   Port 8000    │
     └───────┬────────┘
             │
             │
     ┌───────▼────────┐
     │   SQLite DB    │
     │   (Volume)     │
     └────────────────┘
```

## Security Notes for Production

1. **Don't expose backend ports:** Only Nginx should be exposed in production
2. **Use HTTPS:** ACME certificates are configured via the Nginx container
3. **Secure .env file:** Ensure `.env` has restricted permissions (600)
4. **API keys:** Never commit `.env` to version control
5. **Network isolation:** Backend and frontend are internal-only networks

## Backup

To backup your data:

```bash
# Backup database
cp backend/data/academic_program.db backup/academic_program_$(date +%Y%m%d).db

# Or use Docker
docker compose exec backend cp /app/data/academic_program.db /app/data/backup.db
```

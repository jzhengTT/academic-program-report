# Academic Program Dashboard Docker Compose Management

.PHONY: help build up down logs shell clean restart status setup local-up local-down local-logs local-build

# Default target
help:
	@echo "Academic Program Dashboard Docker Compose Management"
	@echo ""
	@echo "Production (with OAuth2):"
	@echo "  setup     - Copy .env.example to .env and show OAuth2 setup guide"
	@echo "  build     - Build all Docker images"
	@echo "  up        - Start all services (production with OAuth2)"
	@echo "  down      - Stop all services"
	@echo "  logs      - Show logs from all services"
	@echo ""
	@echo "Local Development (no OAuth2):"
	@echo "  local-up    - Start services locally without authentication"
	@echo "  local-down  - Stop local services"
	@echo "  local-logs  - Show logs from local services"
	@echo "  local-build - Build images for local development"
	@echo ""
	@echo "Utilities:"
	@echo "  nginx-shell - Open shell in nginx container"
	@echo "  oauth-shell - Open shell in oauth2-proxy container (production only)"
	@echo "  clean       - Remove containers, networks, and volumes"
	@echo "  restart     - Restart all services"
	@echo "  status      - Show status of all services"

# Shell access
nginx-shell:
	@docker compose ps -q nginx >/dev/null 2>&1 && docker compose exec nginx /bin/bash || \
	 echo "nginx is only available in production compose"

oauth-shell:
	docker compose exec oauth2-proxy /bin/sh

# Clean up everything
clean:
	docker compose down -v --remove-orphans
	docker compose -f docker-compose.local.yml down -v --remove-orphans
	docker system prune -f

# Restart services
restart: down up

# Show service status
status:
	@echo "Production services:"
	@docker compose ps || echo "No production services running"
	@echo ""
	@echo "Local services:"
	@docker compose -f docker-compose.local.yml ps || echo "No local services running"

# Production targets
build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

# Setup environment file
setup:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env file from .env.example"; \
		echo ""; \
		echo "IMPORTANT: Configure before starting production services"; \
		echo "See README.md for deployment guide"; \
		echo ""; \
		echo "Required environment variables:"; \
		echo "  ACME Certificate (HTTP-01 challenge):"; \
		echo "    - ACME_DIRECTORY_URL (default: Let's Encrypt)"; \
		echo "    - ACME_CONTACT"; \
		echo "    - FQDN (must be publicly resolvable)"; \
		echo ""; \
		echo "  OAuth2 Authentication:"; \
		echo "    - OAUTH2_PROXY_PROVIDER"; \
		echo "    - OAUTH2_PROXY_CLIENT_ID"; \
		echo "    - OAUTH2_PROXY_CLIENT_SECRET"; \
		echo "    - OAUTH2_PROXY_COOKIE_SECRET (generate: python -c 'import os,base64; print(base64.urlsafe_b64encode(os.urandom(32)).decode())')"; \
		echo "    - OAUTH2_PROXY_AZURE_TENANT (if using Entra ID)"; \
		echo ""; \
		echo "Please edit .env with your configuration"; \
	else \
		echo ".env file already exists"; \
	fi

# Local development targets
local-build:
	docker compose -f docker-compose.local.yml build

local-up:
	@echo "Starting Academic Program Dashboard locally (no authentication)..."
	@echo "Frontend: http://localhost:8080"
	@echo "Backend: http://localhost:8000"
	docker compose -f docker-compose.local.yml up -d

local-down:
	docker compose -f docker-compose.local.yml down

local-logs:
	docker compose -f docker-compose.local.yml logs -f

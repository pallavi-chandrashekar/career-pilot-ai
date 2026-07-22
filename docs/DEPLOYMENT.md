# Deployment Guide

## Local
Services:
- web
- api
- postgres
- temporal
- temporal-ui
- object-storage
- optional langfuse

Provide:
- `docker compose up`
- health checks
- seed command
- migration command
- test command

## Production
Recommended:
- Managed PostgreSQL
- Managed object storage
- Managed secrets
- Container platform
- Managed Temporal or self-hosted Temporal
- Separate worker deployments
- TLS ingress
- Central logging

## Environments
- local
- test
- staging
- production

Never use production OAuth credentials in local development.

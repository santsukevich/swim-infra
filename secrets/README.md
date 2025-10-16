# Secrets
- cf-token.txt
Cloudflare domain zone API token

- traefik-auth-basic.txt
HTTP BASIC AUTH user file

- minio-env.txt
Minio root user and redirects configuration
WARNING: APP_DOMAI from /.env is not substituted here, you should do it manually

- grafana-admin-user.txt
Admin user name for grafana

- grafana-admin-password.txt
Plain text admin user password for grafana

- prometheus-auth-basic.txt
HTTP BASIC AUTH user file

- alertmanager-telegram-bot-token.txt
Telegram Bot API token for Alertmanager notifications

- prometheus-minio-job-token.txt
Bearer token for Prometheus to access Minio metrics

- postgres-postgres-password.txt
Plain text PostgreSQL root user password

- postgres-repmgr-password.txt
Plain text PostgreSQL repmgr password

- postgres-exporter-config.yml
Postgres exporter config with plain text password

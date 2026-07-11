# RabbitMQ (Docker Compose)

This compose file launches RabbitMQ with the Management UI.

Files:

- `docker-compose.yml` — runs `rabbitmq:3.11-management-alpine` with ports `5672` (AMQP) and `15672` (management UI).

Quick start (from this folder):

```bash
docker-compose up -d
```

Open the management UI in your browser:

  http://localhost:15672

Login credentials (default from compose):

- Username: `user`
- Password: `password`

Verification commands:

```bash
docker-compose ps
docker-compose logs -f rabbitmq
docker-compose exec rabbitmq rabbitmq-diagnostics status
```

Test AMQP connectivity (example using `rabbitmq-diagnostics` inside the container):

```bash
docker-compose exec rabbitmq rabbitmq-diagnostics ping
```

Stop and remove:

```bash
docker-compose down -v
```

Notes:
- Change the default user/password in `docker-compose.yml` before using this in production.
- The management UI exposes metrics, queues, exchanges and is useful for quick inspection.

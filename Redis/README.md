# Local Redis Docker setup

Files added:

- Dockerfile — builds a local Redis image using `redis.conf`
- redis.conf — basic config (AOF on, LRU eviction, 256MB maxmemory)
- docker-compose.yml — convenient compose setup with volume `redis-data`

Quick commands:

Build the image:

```bash
docker build -t local-redis:latest .
```

Run with Docker directly:

```bash
docker run -d --name redis-local -p 6379:6379 -v redis-data:/data local-redis:latest
```

Or use docker-compose:

```bash
docker-compose up -d
```

Use official Redis image (no build):

If you prefer to use the official Redis image rather than building a local image, the `docker-compose.yml` already supports it. The `redis` service will pull `redis:8.2-alpine` automatically when you run:

```bash
docker-compose pull
docker-compose up -d
```

This avoids the `docker build` step. The verification commands below work the same.

Test with `redis-cli` (from another container):

```bash
docker run --rm --link redis-local:redis redis:8.2-alpine redis-cli -h redis -p 6379 ping
# or when using docker-compose, use service name 'redis' as host from another container
```

Next steps:

- Adjust `redis.conf` (maxmemory or persistence) for your needs.
- If you want ACLs or password, add `requirepass <password>` to `redis.conf` and update compose accordingly.

RedisInsight (UI):

- A Redis insights UI is available via the `redislabs/redisinsight` image on port `8001`.
- Start it together with Redis: `docker-compose up -d` (the `redisinsight` service depends on `redis`).
- Open http://localhost:8001 in your browser and create a new connection with:
	- Host: `redis` (or `127.0.0.1` from host)
	- Port: `6379`

If you want to run only RedisInsight briefly (without building the local image):

```bash
docker run -d --name redisinsight -p 8001:8001 --link redis:redis redislabs/redisinsight:latest
```


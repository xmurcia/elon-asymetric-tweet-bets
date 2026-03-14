# Deployment Runbook (Hetzner VPS)

This runbook deploys:
- **Frontend** (CRA build) served by **Nginx**
- **Backend** (FastAPI) via **Docker Compose**
- **Postgres** via **Docker Compose**
- **TLS/SSL** with **Let's Encrypt** (certbot)

Assumptions:
- Ubuntu 22.04+ VPS on Hetzner
- Domain: `YOUR_DOMAIN` (A record points to the VPS public IP)

---

## 0) One-time server bootstrap

### Create a non-root user
```bash
adduser deploy
usermod -aG sudo deploy
```

### Firewall (recommended)
```bash
ufw allow OpenSSH
ufw allow 80
ufw allow 443
ufw enable
ufw status
```

### Install Docker + Compose plugin
```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg

sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo $VERSION_CODENAME) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

sudo usermod -aG docker deploy
newgrp docker

docker version
docker compose version
```

---

## 1) App layout on the server

Recommended structure:
- `/opt/elon-bets/` → git checkout
- `/opt/elon-bets/.env` → production env vars (NOT committed)

```bash
sudo mkdir -p /opt/elon-bets
sudo chown -R deploy:deploy /opt/elon-bets
cd /opt/elon-bets

# Option A: clone
git clone YOUR_REPO_GIT_URL .

# Option B: pull if already cloned
# git pull
```

Create the env file:
```bash
cp .env.example .env
nano .env
```

Minimum variables:
- `DATABASE_URL` (if you override compose defaults)
- `ALCHEMY_WEBHOOK_SECRET` (optional, only if you enable webhook verification)

---

## 2) Backend + Postgres (Docker Compose)

### Start services
```bash
cd /opt/elon-bets

docker compose up -d --build

docker compose ps
```

### Verify health
```bash
curl -fsS http://127.0.0.1:8000/health
curl -fsS http://127.0.0.1:8000/metrics
```

### Log rotation for Docker (recommended)

Create `/etc/docker/daemon.json`:
```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```
Restart docker:
```bash
sudo systemctl restart docker
```

---

## 3) Frontend build + Nginx

### Build frontend
On the VPS:
```bash
cd /opt/elon-bets
npm ci --legacy-peer-deps
npm run build
```

### Install and configure Nginx
```bash
sudo apt-get install -y nginx
```

Create Nginx site config `/etc/nginx/sites-available/elon-bets.conf`:

```nginx
server {
  listen 80;
  server_name YOUR_DOMAIN;

  # Frontend static build
  root /opt/elon-bets/build;
  index index.html;

  # SPA routing
  location / {
    try_files $uri /index.html;
  }

  # Backend API reverse proxy
  location /api/ {
    proxy_pass http://127.0.0.1:8000/api/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
  }

  # Health endpoints (optional)
  location /health {
    proxy_pass http://127.0.0.1:8000/health;
  }

  location /metrics {
    proxy_pass http://127.0.0.1:8000/metrics;
  }
}
```

Enable the site:
```bash
sudo ln -sf /etc/nginx/sites-available/elon-bets.conf /etc/nginx/sites-enabled/elon-bets.conf
sudo nginx -t
sudo systemctl reload nginx
```

---

## 4) SSL with Let's Encrypt

```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d YOUR_DOMAIN
```

Auto-renew is installed automatically, verify:
```bash
sudo systemctl status certbot.timer
```

---

## 5) Process management (recommended)

Docker Compose will keep containers running, but you may want systemd to ensure boot-time startup.

Create `/etc/systemd/system/elon-bets.service`:
```ini
[Unit]
Description=Elon Bets docker-compose
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/elon-bets
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now elon-bets
sudo systemctl status elon-bets
```

---

## 6) Updates

```bash
cd /opt/elon-bets

git pull
npm ci --legacy-peer-deps
npm run build

docker compose up -d --build
sudo systemctl reload nginx
```

---

## 7) Backup & restore (Postgres)

### Backup
```bash
mkdir -p /opt/backups/elon-bets
cd /opt/elon-bets

# Dump from the running container
TS=$(date +%F_%H%M%S)
docker compose exec -T db pg_dump -U user -d elon_bets > /opt/backups/elon-bets/elon_bets_${TS}.sql
```

### Restore
**Destructive** (overwrites target DB):
```bash
cd /opt/elon-bets
cat /opt/backups/elon-bets/elon_bets_YYYY-MM-DD_HHMMSS.sql | docker compose exec -T db psql -U user -d elon_bets
```

---

## 8) Monitoring (basic)

- `GET https://YOUR_DOMAIN/health` → should return `{"status":"ok"}`
- `GET https://YOUR_DOMAIN/metrics` → JSON with uptime + request counters

Recommended external monitoring:
- UptimeRobot / BetterStack: ping `/health` every 1-5 minutes
- Healthchecks.io: (optional) add a cron job or scheduler hook if you later create periodic tasks that must run

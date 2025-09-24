# Server Baseline

**Server Baseline** is a boilerplate project combining NGINX and Django REST Framework (DRF), designed to help you quickly set up a new server project.  
It provides a structured environment with separate configurations for **development** and **deployment**, ensuring a smooth transition from local testing to production.

This project includes pre-configured `nginx.conf`, `Dockerfile`, and `docker-compose.yml` files.

---

## 📦 Features

- 🐳 Docker-Compose included
- 📧 Optional Celery + Redis integration for background tasks

---

## 📌 Getting Started

### 1. Clone the Project
```bash
git clone <your-repository-url>
cd <your-project-directory>
```

### 2. Initialize Django REST Framework

- Refer to `server/README.md` (from the `drf_baseline` project) for how to initialize the Django REST Framework backend.

---

### 3. Using an Database

📄 File: `docker-compose.yml`  
- Delete the following network section for External DB use:
- Rename the following network section for Internal DB use:

```yaml
services:
  server:
    networks:
      - db_baseline_network               # Internal DB Server

networks:
  db_baseline_network:                      # Internal DB Server (Remove if External)
    external: true
```

---

### 4. HTTP Setup

📄 File: `nginx/nginx.conf`  
- Replace `domain.yourdomain.com` with your actual domain:

```nginx
server_name domain.yourdomain.com;
```

✅ Then run:
```bash
docker compose up
```

---

### 5. HTTP & HTTPS Setup

📄 File: `nginx/nginx.conf`  
- Remove the `# HTTP` block entirely.  
- Uncomment the `# HTTPS` block.  
- Replace `domain.yourdomain.com` with your actual domain:

```nginx
# HTTPS
server {
    listen 443 ssl;
    server_name domain.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    ...
}
```

📄 File: `nginx/Dockerfile`  
- Uncomment the following line:
```dockerfile
EXPOSE 443
```

📄 File: `docker-compose.yml`  
- Uncomment the following lines:
```yaml
services:
  nginx:
    ports:
      - "443:443"
    volumes:
      - /etc/letsencrypt:/etc/letsencrypt
```

🔐 Issue SSL certificates on your server using Let’s Encrypt:
```bash
sudo apt update
sudo apt install certbot
sudo certbot certonly --standalone -d yourdomain.com
```

❗ If missing, download the following files to your server:
- `/etc/letsencrypt/options-ssl-nginx.conf`
- `/etc/letsencrypt/ssl-dhparams.pem`

✅ Then run:
```bash
docker compose up
```

---

📎 **Note**  
- Be sure to replace `yourdomain.com` with your actual domain name.  
- It’s recommended to configure a cron job to automatically renew your SSL certificates.

---

## 🗂 Project Structure

```text
├── nginx
│   ├── Dockerfile
│   └── nginx.conf
├── server (drf_baseline)
├── README.md
└── docker-compose.yml
```
# AI Linux Agent - Deployment Guide

This guide provides comprehensive instructions for deploying the AI Linux Agent system in production.

## Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Vue.js        │    │   FastAPI        │    │   MongoDB       │
│   Frontend      │◄──►│   Backend        │◄──►│   Database      │
│   (Port 3000)   │    │   (Port 8000)    │    │   (Port 27017)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │
         │                       │ WebSocket
         │                       ▼
         │              ┌──────────────────┐
         │              │   Python Client  │
         │              │   (Linux Agent)  │
         └──────────────┤   Multiple       │
                        │   Machines       │
                        └──────────────────┘
```

## Prerequisites

### System Requirements
- **Backend**: Linux/Ubuntu 20.04+, 2GB RAM, 1 CPU core
- **Database**: MongoDB 4.4+
- **Frontend**: Node.js 18+, npm/yarn
- **Client**: Python 3.8+, Linux-based systems

### External Services
1. **Firebase Project** with Authentication enabled
2. **Google Cloud** account with Gemini API access
3. **Domain name** (for production deployment)
4. **SSL certificate** (Let's Encrypt recommended)

## Setup Instructions

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv nodejs npm mongodb git nginx certbot python3-certbot-nginx

# Create application user
sudo useradd -m -s /bin/bash aiagent
sudo usermod -aG sudo aiagent
```

### 2. MongoDB Setup

```bash
# Start and enable MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# Create database and user
mongo
> use ai_linux_agent
> db.createUser({
    user: "aiagent",
    pwd: "your_secure_password",
    roles: ["readWrite"]
  })
> exit
```

### 3. Backend Deployment

```bash
# Switch to application user
sudo su - aiagent

# Clone repository
git clone <your-repo-url> ai-linux-agent
cd ai-linux-agent/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env
```

**Backend Environment Configuration (.env):**
```bash
# MongoDB
MONGODB_URL=mongodb://aiagent:your_secure_password@localhost:27017/ai_linux_agent

# Firebase (get from Firebase Console)
FIREBASE_SERVICE_ACCOUNT_KEY={"type": "service_account", ...}

# Gemini API
GEMINI_API_KEY=your_gemini_api_key

# Server
HOST=0.0.0.0
PORT=8000
SECRET_KEY=your_super_secret_key_here

# CORS
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

**Create systemd service:**
```bash
sudo nano /etc/systemd/system/aiagent-backend.service
```

```ini
[Unit]
Description=AI Linux Agent Backend
After=network.target mongod.service

[Service]
Type=simple
User=aiagent
WorkingDirectory=/home/aiagent/ai-linux-agent/backend
Environment=PATH=/home/aiagent/ai-linux-agent/backend/venv/bin
ExecStart=/home/aiagent/ai-linux-agent/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable aiagent-backend
sudo systemctl start aiagent-backend
```

### 4. Frontend Deployment

```bash
cd /home/aiagent/ai-linux-agent/frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.production
nano .env.production
```

**Frontend Environment Configuration:**
```bash
# Firebase Configuration
VITE_FIREBASE_API_KEY=your_firebase_api_key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id

# API Configuration
VITE_API_BASE_URL=https://yourdomain.com/api
VITE_WS_URL=wss://yourdomain.com
```

```bash
# Build for production
npm run build

# Copy build files to web directory
sudo mkdir -p /var/www/aiagent
sudo cp -r dist/* /var/www/aiagent/
sudo chown -R www-data:www-data /var/www/aiagent
```

### 5. Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/aiagent
```

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Frontend
    location / {
        root /var/www/aiagent;
        index index.html;
        try_files $uri $uri/ /index.html;
        
        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "no-referrer-when-downgrade" always;
        add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # WebSocket
    location /ws/ {
        proxy_pass http://localhost:8000/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

```bash
# Enable site and restart nginx
sudo ln -s /etc/nginx/sites-available/aiagent /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6. SSL Certificate Setup

```bash
# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 7. Firewall Configuration

```bash
# Configure UFW
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

## Client Deployment

### Manual Installation

```bash
# On each client machine
git clone <your-repo-url> ai-linux-agent
cd ai-linux-agent/client

# Install dependencies
pip3 install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env
```

**Client Environment (.env):**
```bash
API_KEY=get_from_web_dashboard
SERVER_URL=wss://yourdomain.com
LOG_LEVEL=INFO
HEARTBEAT_INTERVAL=30
```

```bash
# Run client
python3 run_client.py
```

### Systemd Service for Client

```bash
sudo nano /etc/systemd/system/aiagent-client.service
```

```ini
[Unit]
Description=AI Linux Agent Client
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/ai-linux-agent/client
ExecStart=/usr/bin/python3 run_client.py
Restart=always
RestartSec=10
Environment=API_KEY=your_api_key
Environment=SERVER_URL=wss://yourdomain.com

[Install]
WantedBy=multi-user.target
```

### Docker Deployment for Client

```bash
# Create Dockerfile in client directory
nano Dockerfile
```

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "run_client.py"]
```

```bash
# Build and run
docker build -t aiagent-client .
docker run -e API_KEY=your_api_key -e SERVER_URL=wss://yourdomain.com aiagent-client
```

## Security Hardening

### Backend Security

1. **Environment Variables**: Never commit secrets to version control
2. **Rate Limiting**: Already implemented via SlowAPI
3. **Input Validation**: Command validation and sanitization included
4. **HTTPS Only**: Enforce SSL/TLS for all communications
5. **Database Security**: Use strong passwords and network restrictions

### System Security

```bash
# Disable root login
sudo nano /etc/ssh/sshd_config
# Set: PermitRootLogin no
sudo systemctl restart ssh

# Setup fail2ban
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Regular updates
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

### Monitoring Setup

```bash
# Install htop for system monitoring
sudo apt install htop

# Setup log rotation
sudo nano /etc/logrotate.d/aiagent
```

```
/home/aiagent/ai-linux-agent/backend/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    copytruncate
}
```

## Backup Strategy

### Database Backup

```bash
# Create backup script
nano /home/aiagent/backup_db.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/home/aiagent/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

mongodump --db ai_linux_agent --out $BACKUP_DIR/mongo_$DATE
tar -czf $BACKUP_DIR/mongo_$DATE.tar.gz -C $BACKUP_DIR mongo_$DATE
rm -rf $BACKUP_DIR/mongo_$DATE

# Keep only last 7 days
find $BACKUP_DIR -name "mongo_*.tar.gz" -mtime +7 -delete
```

```bash
chmod +x /home/aiagent/backup_db.sh

# Add to cron for daily backups
crontab -e
# Add: 0 2 * * * /home/aiagent/backup_db.sh
```

## Maintenance

### Log Monitoring

```bash
# Backend logs
sudo journalctl -u aiagent-backend -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# MongoDB logs
sudo tail -f /var/log/mongodb/mongod.log
```

### Health Checks

```bash
# Check service status
sudo systemctl status aiagent-backend
sudo systemctl status nginx
sudo systemctl status mongod

# Check API health
curl https://yourdomain.com/health
```

### Updates

```bash
# Update backend
cd /home/aiagent/ai-linux-agent
git pull
cd backend
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart aiagent-backend

# Update frontend
cd /home/aiagent/ai-linux-agent/frontend
npm install
npm run build
sudo cp -r dist/* /var/www/aiagent/
```

## Troubleshooting

### Common Issues

1. **WebSocket Connection Failed**
   - Check nginx WebSocket configuration
   - Verify SSL certificate
   - Check firewall rules

2. **Database Connection Issues**
   - Verify MongoDB is running
   - Check connection string
   - Verify user permissions

3. **Authentication Failures**
   - Check Firebase configuration
   - Verify API keys
   - Check token expiration

### Performance Optimization

1. **Database Indexing**: Already included in models
2. **Connection Pooling**: Configured in MongoDB driver
3. **Static File Caching**: Configure nginx for static assets
4. **Rate Limiting**: Already implemented

## Scaling Considerations

### Horizontal Scaling

1. **Load Balancer**: Use nginx or cloud load balancer
2. **Multiple Backend Instances**: Run on different ports
3. **Database Replication**: MongoDB replica sets
4. **CDN**: For static frontend assets

### Monitoring and Alerting

1. **Prometheus + Grafana**: For metrics collection
2. **ELK Stack**: For log aggregation
3. **Uptime Monitoring**: Services like UptimeRobot
4. **Error Tracking**: Services like Sentry

This deployment guide provides a production-ready setup for the AI Linux Agent system with security, monitoring, and maintenance considerations.
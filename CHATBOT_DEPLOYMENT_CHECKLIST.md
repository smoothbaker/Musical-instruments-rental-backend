# Chatbot System - Deployment Checklist

## Pre-Deployment Checklist

### ✅ Local Development Setup

- [ ] **Ollama Installation**
  - [ ] Downloaded Ollama from https://ollama.ai
  - [ ] Installed for your OS (Windows/Mac/Linux)
  - [ ] Can run `ollama --version` successfully

- [ ] **Model Downloaded**
  - [ ] Ran `ollama pull llama2`
  - [ ] Verified with `ollama list` (llama2 appears)
  - [ ] Model files downloaded (~4GB)

- [ ] **Python Environment**
  - [ ] Python 3.8+ installed
  - [ ] Virtual environment created and activated
  - [ ] `pip install -r requirements.txt` completed
  - [ ] New packages installed:
    - [ ] langchain
    - [ ] langchain-ollama
    - [ ] ollama

- [ ] **Flask App Configuration**
  - [ ] `app/init.py` imports chatbot blueprint
  - [ ] `app/init.py` registers chatbot.blp
  - [ ] Database migration run: `flask db upgrade`
  - [ ] ChatMessage table created

- [ ] **Code Review**
  - [ ] `app/models/chat_message.py` created
  - [ ] `app/services/chatbot_service.py` created
  - [ ] `app/routes/chatbot.py` created
  - [ ] `app/schemas.py` updated with chat schemas
  - [ ] `tests/chatbot_test.py` created

---

### ✅ Testing

- [ ] **Unit Tests**
  - [ ] Run `python tests/chatbot_test.py`
  - [ ] All tests pass (or verify expected test count)
  - [ ] No import errors
  - [ ] Database operations work

- [ ] **Manual Testing with cURL**
  ```bash
  # 1. Get auth token
  curl -X POST http://localhost:5000/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"user@example.com","password":"password"}'
  
  # 2. Test chat endpoint
  curl -X POST http://localhost:5000/api/chatbot/chat \
    -H "Authorization: Bearer {TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{"session_id":"test1","message":"Hello chatbot"}'
  
  # 3. Test history endpoint
  curl -X GET http://localhost:5000/api/chatbot/history/test1 \
    -H "Authorization: Bearer {TOKEN}"
  ```

- [ ] **API Testing with Swagger**
  - [ ] Flask app running on http://localhost:5000
  - [ ] Ollama service running on http://localhost:11434
  - [ ] Navigate to http://localhost:5000/api/docs
  - [ ] All 6 chatbot endpoints appear in Swagger
  - [ ] Can authorize with JWT token
  - [ ] Can execute test requests in Swagger UI

- [ ] **Functional Testing**
  - [ ] User can send message
  - [ ] Chatbot returns response (may take 2-5 sec)
  - [ ] Recommendations are extracted properly
  - [ ] Session history works
  - [ ] User profile integration works

---

### ✅ Documentation

- [ ] **Files Created/Modified**
  - [ ] `CHATBOT_SYSTEM_GUIDE.md` - Complete technical reference
  - [ ] `CHATBOT_QUICK_START.md` - Setup guide for developers
  - [ ] `CHATBOT_IMPLEMENTATION_EXAMPLES.md` - Code examples
  - [ ] `CHATBOT_ARCHITECTURE_VISUAL.md` - System diagrams
  - [ ] `CHATBOT_SUMMARY.md` - High-level overview

- [ ] **Documentation Review**
  - [ ] All endpoints documented
  - [ ] Setup instructions are clear
  - [ ] Examples are runnable
  - [ ] Troubleshooting section present
  - [ ] API response formats documented

---

## Deployment to Production

### ✅ Pre-Production Validation

- [ ] **Performance Verification**
  - [ ] First response time acceptable (5-15 sec is normal)
  - [ ] Subsequent responses are fast (2-5 sec)
  - [ ] Database queries optimized
  - [ ] No memory leaks during extended testing

- [ ] **Security Review**
  - [ ] JWT authentication enforced on all endpoints
  - [ ] User data isolation verified
  - [ ] No sensitive data in logs
  - [ ] Input validation on all endpoints
  - [ ] SQL injection prevention verified

- [ ] **Error Handling**
  - [ ] All error cases handled gracefully
  - [ ] Meaningful error messages returned
  - [ ] No stack traces exposed to users
  - [ ] Ollama connection failures handled
  - [ ] LLM errors don't crash app

- [ ] **Database**
  - [ ] Production database configured
  - [ ] Migrations run successfully
  - [ ] Backups configured
  - [ ] User isolation verified
  - [ ] Data retention policy clear

---

### ✅ Infrastructure Setup

- [ ] **Ollama Deployment**
  - [ ] [ **Option A: Host Same Server**
    - [ ] Ollama installed on production server
    - [ ] Service configured to start on boot
    - [ ] Model (llama2) pre-downloaded
    - [ ] Port 11434 accessible internally only
  
  - [ ] **Option B: Separate Ollama Container**
    - [ ] Docker image ready for Ollama
    - [ ] Persistent volume for model cache
    - [ ] Network configured for Flask app access
    - [ ] Health checks configured
  
  - [ ] **Option C: Cloud Service (Future)**
    - [ ] API key configured
    - [ ] Rate limiting understood
    - [ ] Cost estimates calculated

- [ ] **Flask App Deployment**
  - [ ] [ ] Production WSGI server configured (Gunicorn/uWSGI)
  - [ ] [ ] Environment variables set (DATABASE_URL, SECRET_KEY, etc)
  - [ ] [ ] Logging configured
  - [ ] [ ] Error monitoring set up (Sentry, etc)
  - [ ] [ ] Database URL points to production DB

- [ ] **Load Balancing (if applicable)**
  - [ ] [ ] Multiple instances of Flask app
  - [ ] [ ] Load balancer configured
  - [ ] [ ] Session management across instances
  - [ ] [ ] Database connection pooling configured

---

### ✅ Monitoring & Logging

- [ ] **Logging Setup**
  - [ ] All API calls logged
  - [ ] LLM response times tracked
  - [ ] Errors logged with full context
  - [ ] User interactions logged (privacy-compliant)
  - [ ] Database query times monitored

- [ ] **Monitoring Dashboards**
  - [ ] Chat endpoint request rate
  - [ ] Average response time
  - [ ] Error rate
  - [ ] Active sessions count
  - [ ] Database health

- [ ] **Alerting**
  - [ ] Alert if Ollama unreachable
  - [ ] Alert if response time > threshold
  - [ ] Alert if error rate > threshold
  - [ ] Alert on database connection failures
  - [ ] Alert on JWT validation failures

---

### ✅ Compliance & Security

- [ ] **Data Privacy**
  - [ ] GDPR compliance verified (if applicable)
  - [ ] User consent for storing conversations
  - [ ] Data deletion policy implemented
  - [ ] No sensitive data in conversation storage
  - [ ] PII handling compliant

- [ ] **Accessibility**
  - [ ] API responses follow standards
  - [ ] Documentation accessible
  - [ ] Error messages clear and helpful
  - [ ] Rate limiting implemented (prevent abuse)
  - [ ] No hardcoded secrets in code

- [ ] **Backup & Recovery**
  - [ ] Database backups automated
  - [ ] Backup retention policy set
  - [ ] Recovery testing done
  - [ ] Disaster recovery plan documented
  - [ ] Model cache backups considered

---

## Deployment Steps

### Step 1: Prepare Server

```bash
# SSH into production server
ssh user@production-server

# Create app directory
mkdir -p /var/app/musical-instruments
cd /var/app/musical-instruments

# Clone/copy application code
git clone <your-repo> . 
# OR
cp -r /local/path/* .

# Set up Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Setup Ollama

```bash
# Option A: Install on same server
curl https://ollama.ai/install.sh | sh
ollama pull llama2

# Create systemd service for ollama
sudo nano /etc/systemd/system/ollama.service
# Add content below:
```

**ollama.service:**
```ini
[Unit]
Description=Ollama
After=network-online.target

[Service]
ExecStart=/usr/bin/ollama serve
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable ollama
sudo systemctl start ollama

# Verify it's running
curl http://localhost:11434/api/tags
```

### Step 3: Configure Flask App

```bash
# Set environment variables
export FLASK_ENV=production
export SECRET_KEY=<generate-random-key>
export DATABASE_URL=<production-database-url>
export JWT_SECRET_KEY=<generate-random-key>

# Or create .env file
echo "FLASK_ENV=production" > .env
echo "SECRET_KEY=<random>" >> .env
echo "DATABASE_URL=<db-url>" >> .env
echo "JWT_SECRET_KEY=<random>" >> .env

# Run migrations
flask db upgrade

# Create admin user (if needed)
flask create-admin-user --email admin@example.com --password <secure-password>
```

### Step 4: Setup WSGI Server

**Using Gunicorn:**

```bash
# Install gunicorn
pip install gunicorn

# Create gunicorn config
cat > gunicorn_config.py << 'EOF'
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
timeout = 60
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s"'
error_logfile = '/var/log/app/gunicorn.log'
EOF

# Create systemd service
sudo nano /etc/systemd/system/musical-instruments.service
```

**musical-instruments.service:**
```ini
[Unit]
Description=Musical Instruments Rental API
After=network.target ollama.service

[Service]
User=www-data
WorkingDirectory=/var/app/musical-instruments
ExecStart=/var/app/musical-instruments/venv/bin/gunicorn \
    --config gunicorn_config.py \
    --workers 4 \
    app.init:create_app
Restart=always
RestartSec=5
Environment="FLASK_ENV=production"

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl enable musical-instruments
sudo systemctl start musical-instruments

# Check status
sudo systemctl status musical-instruments
```

### Step 5: Setup Nginx Reverse Proxy

```bash
# Create nginx config
sudo nano /etc/nginx/sites-available/musical-instruments
```

**nginx config:**
```nginx
upstream app {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.example.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.example.com;

    ssl_certificate /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;

    # Performance settings
    client_max_body_size 20M;
    proxy_read_timeout 120s;
    proxy_connect_timeout 120s;

    # Logging
    access_log /var/log/nginx/api_access.log;
    error_log /var/log/nginx/api_error.log;

    location / {
        proxy_pass http://app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Chatbot specific timeout (longer for LLM)
        proxy_read_timeout 180s;
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/musical-instruments \
    /etc/nginx/sites-enabled/

# Test config
sudo nginx -t

# Reload
sudo systemctl reload nginx
```

### Step 6: Setup SSL Certificate

```bash
# Using Let's Encrypt (free)
sudo apt-get install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d api.example.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### Step 7: Verify Deployment

```bash
# Check all services running
sudo systemctl status ollama
sudo systemctl status musical-instruments
sudo systemctl status nginx

# Test API
curl -X GET https://api.example.com/api/health

# Test with auth
TOKEN=$(curl -X POST https://api.example.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}' \
  | jq -r '.access_token')

curl -X POST https://api.example.com/api/chatbot/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"session_id":"test","message":"Hello"}'
```

---

## Post-Deployment

- [ ] **Monitoring Active**
  - [ ] Dashboard showing real-time metrics
  - [ ] Alerts configured and tested
  - [ ] Logs flowing to centralized system

- [ ] **Documentation Updated**
  - [ ] Production endpoints documented
  - [ ] Support runbook created
  - [ ] Incident response plan documented
  - [ ] Team trained on system

- [ ] **User Communication**
  - [ ] Changelog updated
  - [ ] Users notified of new chatbot feature
  - [ ] Support documentation ready
  - [ ] FAQ prepared

- [ ] **Backup Verification**
  - [ ] Database backups running
  - [ ] Model cache backed up
  - [ ] Recovery tested
  - [ ] Retention policy active

---

## Rollback Plan

If issues occur after deployment:

```bash
# Stop current version
sudo systemctl stop musical-instruments

# Revert code to previous version
git revert <commit-hash>
# OR restore from backup

# Revert database if needed
flask db downgrade

# Start service
sudo systemctl start musical-instruments

# Verify
curl https://api.example.com/api/health
```

---

## Success Criteria

✅ Deployment successful when:

1. ✓ All services running without errors
2. ✓ Chatbot endpoints responding within 5 seconds
3. ✓ JWT authentication working
4. ✓ Recommendations generating correctly
5. ✓ Conversation history persisting
6. ✓ Database backups running
7. ✓ Monitoring dashboards showing data
8. ✓ Error alerting configured
9. ✓ Users can access chatbot
10. ✓ No performance degradation observed

---

## Support & Troubleshooting

### Ollama Not Responding
```bash
# Check if running
ps aux | grep ollama

# Check port
netstat -tlnp | grep 11434

# Restart service
sudo systemctl restart ollama

# Check logs
journalctl -u ollama -n 50
```

### Flask App Not Starting
```bash
# Check logs
sudo journalctl -u musical-instruments -n 100

# Test locally
source venv/bin/activate
python run.py

# Check environment variables
printenv | grep FLASK
```

### High Response Times
```bash
# Check Ollama load
curl http://localhost:11434/api/tags

# Monitor system resources
htop

# Check database
sudo systemctl status postgresql  # or your DB

# Reduce history size if needed
# Edit chatbot_service.py, change limit parameter
```

---

**Deployment Complete! Your chatbot is live! 🎉🎵**

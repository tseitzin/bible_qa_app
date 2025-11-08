# Heroku Deployment Guide - Bible Q&A App

This guide will help you deploy both the backend and frontend to Heroku.

## Prerequisites

- [x] Heroku CLI installed
- [ ] Heroku account created
- [ ] OpenAI API key

## Step 1: Login to Heroku

```bash
heroku login
```

## Step 2: Deploy Backend (FastAPI)

### 2.1 Create Backend App

```bash
cd backend
heroku create bible-qa-backend-YOUR_NAME  # Replace YOUR_NAME with something unique
```

### 2.2 Add PostgreSQL Database

```bash
heroku addons:create heroku-postgresql:essential-0
```

### 2.3 Set Environment Variables

```bash
# Set your OpenAI API key
heroku config:set OPENAI_API_KEY=your_openai_api_key_here

# Set allowed origins (we'll update this after deploying frontend)
heroku config:set ALLOWED_ORIGINS=http://localhost:5173

# Set debug to false for production
heroku config:set DEBUG=false
```

### 2.4 Initialize Git and Deploy

```bash
# If not already a git repo
git init
git add .
git commit -m "Initial backend deployment"

# Deploy to Heroku
git push heroku main

# If your branch is named 'master':
# git push heroku master:main
```

### 2.5 Run Database Migrations

```bash
heroku run python -m alembic upgrade head
```

### 2.6 Verify Backend

```bash
# Get your backend URL
heroku apps:info

# Test the health endpoint
curl https://your-backend-app.herokuapp.com/
```

**Save your backend URL - you'll need it for the frontend!**

## Step 3: Deploy Frontend (Vue.js)

### 3.1 Update Frontend Environment Variable

First, update `frontend/app.json` with your actual backend URL:

```json
{
  "env": {
    "VITE_API_URL": {
      "description": "Backend API URL",
      "value": "https://your-backend-app.herokuapp.com"
    }
  }
}
```

### 3.2 Create Frontend App

```bash
cd ../frontend
heroku create bible-qa-frontend-YOUR_NAME  # Replace YOUR_NAME with something unique
```

### 3.3 Set Environment Variable

```bash
# Use your actual backend URL from Step 2.6
heroku config:set VITE_API_URL=https://your-backend-app.herokuapp.com
heroku config:set NODE_ENV=production
```

### 3.4 Build and Deploy

```bash
# Install dependencies and build
npm install
npm run build

# Initialize git if needed
git init
git add .
git commit -m "Initial frontend deployment"

# Deploy
git push heroku main
```

### 3.5 Verify Frontend

```bash
heroku open
```

## Step 4: Update CORS Configuration

Now that both apps are deployed, update the backend's ALLOWED_ORIGINS:

```bash
cd ../backend
heroku config:set ALLOWED_ORIGINS=https://your-frontend-app.herokuapp.com,http://localhost:5173
```

## Step 5: Testing

1. Open your frontend URL: `https://your-frontend-app.herokuapp.com`
2. Try asking a question
3. Check that the backend responds correctly

## Monitoring & Maintenance

### View Logs

```bash
# Backend logs
cd backend
heroku logs --tail

# Frontend logs
cd frontend
heroku logs --tail
```

### Check App Status

```bash
heroku ps
```

### Restart Apps

```bash
heroku restart
```

### Database Management

```bash
# Check database info
heroku pg:info

# Connect to database
heroku pg:psql

# Backup database
heroku pg:backups:capture
heroku pg:backups:download
```

## Troubleshooting

### Backend Issues

**Database connection errors:**
```bash
# Check DATABASE_URL is set
heroku config:get DATABASE_URL

# Run migrations again
heroku run python -m alembic upgrade head
```

**CORS errors:**
```bash
# Verify ALLOWED_ORIGINS includes your frontend URL
heroku config:get ALLOWED_ORIGINS

# Update if needed
heroku config:set ALLOWED_ORIGINS=https://your-frontend-app.herokuapp.com,http://localhost:5173
```

**OpenAI API errors:**
```bash
# Verify API key is set
heroku config:get OPENAI_API_KEY

# Update if needed
heroku config:set OPENAI_API_KEY=your_key_here
```

### Frontend Issues

**Build failures:**
```bash
# Clear build cache
heroku builds:cache:purge

# Rebuild
git commit --allow-empty -m "Rebuild"
git push heroku main
```

**API connection issues:**
```bash
# Verify VITE_API_URL is correct
heroku config:get VITE_API_URL

# Update if needed
heroku config:set VITE_API_URL=https://your-backend-app.herokuapp.com
```

## Cost Management

The apps use Heroku's Eco dynos which cost $5/month each. To minimize costs:

1. **Free Option**: Use Heroku's free tier (limited hours/month)
   ```bash
   heroku ps:scale web=0  # Stop the dyno when not in use
   heroku ps:scale web=1  # Start it again
   ```

2. **Monitor Usage**:
   ```bash
   heroku ps
   heroku pg:info
   ```

## Custom Domain (Optional)

If you want to use a custom domain:

```bash
# Add domain to frontend
cd frontend
heroku domains:add www.yourdomain.com

# Add domain to backend
cd ../backend
heroku domains:add api.yourdomain.com

# Update DNS records as shown in Heroku
heroku domains
```

Then update ALLOWED_ORIGINS:
```bash
cd backend
heroku config:set ALLOWED_ORIGINS=https://www.yourdomain.com,http://localhost:5173
```

## Environment Variables Reference

### Backend (.env or heroku config)
- `DATABASE_URL` - Auto-set by Heroku PostgreSQL addon
- `OPENAI_API_KEY` - Your OpenAI API key (required)
- `ALLOWED_ORIGINS` - Frontend URL(s) for CORS
- `DEBUG` - Set to "false" for production

### Frontend (.env or heroku config)
- `VITE_API_URL` - Backend API URL
- `NODE_ENV` - Set to "production"

## Next Steps

1. ✅ Deploy backend
2. ✅ Deploy frontend
3. ✅ Update CORS settings
4. ✅ Test the application
5. [ ] Set up monitoring (optional)
6. [ ] Configure custom domain (optional)
7. [ ] Set up automated backups (optional)

## Support

If you encounter issues:
1. Check the logs: `heroku logs --tail`
2. Verify environment variables: `heroku config`
3. Check app status: `heroku ps`
4. Review this guide's troubleshooting section

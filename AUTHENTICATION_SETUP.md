# Authentication System Setup Guide

## Overview
Your Bible Q&A app now has a complete JWT-based authentication system with database-backed saved answers!

## What's Been Implemented

### Backend Changes

1. **Database Migrations** (run these to update your database)
   - `0003_add_auth_to_users.py` - Adds email, password, and active status to users table
   - `0004_create_saved_answers.py` - Creates saved_answers table with user association

2. **Authentication System**
   - JWT token generation and validation
   - Password hashing with bcrypt
   - User registration and login endpoints
   - Protected API routes requiring authentication

3. **New API Endpoints**
   - `POST /api/auth/register` - Register new user
   - `POST /api/auth/login` - Login and get JWT token
   - `GET /api/auth/me` - Get current user info
   - `POST /api/saved-answers` - Save a Q&A
   - `GET /api/saved-answers` - Get user's saved answers (with search/filter)
   - `DELETE /api/saved-answers/{id}` - Delete a saved answer
   - `GET /api/saved-answers/tags` - Get user's tags

4. **Protected Endpoints**
   - `POST /api/ask` - Now requires authentication
   - `GET /api/history` - Now requires authentication (uses authenticated user's ID)

### Frontend Changes

1. **New Pages**
   - `/login` - Styled login page
   - `/register` - Styled registration page
   - `/home` - Landing page for authenticated users

2. **Authentication Services**
   - `authService.js` - Handles login, registration, token management
   - `useAuth.js` - Vue composable for auth state management
   - `axiosConfig.js` - Automatic JWT token injection in API requests

3. **Router Guards**
   - Protected routes redirect to login if not authenticated
   - Login/register redirect to home if already authenticated

4. **Updated Services**
   - `savedAnswersService.js` - Now uses API instead of localStorage
   - All API calls automatically include JWT tokens

## Setup Instructions

### 1. Backend Setup

```bash
cd backend

# Install new dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Add SECRET_KEY to .env file (generate a secure random key)
echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env
```

### 2. Frontend Setup

```bash
cd frontend

# No new dependencies needed - axios already installed
# The changes are already in place
```

### 3. Run the Application

**Start Backend:**
```bash
cd backend
uvicorn app.main:app --reload
```

**Start Frontend:**
```bash
cd frontend
npm run dev
```

Or use Docker Compose:
```bash
docker-compose up --build
```

## Usage Flow

1. **First Time User:**
   - Navigate to the app
   - Automatically redirected to `/login`
   - Click "Create one" to register
   - Fill out registration form
   - Automatically logged in and redirected to `/home`

2. **Returning User:**
   - Navigate to `/login`
   - Enter email and password
   - Redirected to `/home` after successful login

3. **Using the App:**
   - From `/home`, navigate to Bible Q&A or Kids Mode
   - Ask questions (now saved to your account)
   - Save answers you want to keep
   - Your saved answers are accessible from any device

4. **Saved Answers:**
   - Answers are now stored in the database
   - Associated with your user account
   - Accessible across devices
   - Include tags for organization
   - Searchable and filterable

## Important Notes

### Security

1. **SECRET_KEY**: Make sure to set a strong SECRET_KEY in your `.env` file (backend)
   ```bash
   SECRET_KEY=your-very-long-random-secret-key-here
   ```

2. **Passwords**: All passwords are hashed with bcrypt before storage

3. **JWT Tokens**: Tokens expire after 7 days (configurable in `app/auth.py`)

### Environment Variables

Add to `backend/.env`:
```env
SECRET_KEY=<generate-with-openssl-rand-hex-32>
DATABASE_URL=<your-database-url>
OPENAI_API_KEY=<your-openai-key>
```

### Data Migration

If you have existing data in localStorage, users will need to manually save their important answers again after logging in. The old localStorage-based system is backed up in `savedAnswersService.old.js` if needed.

## API Changes

### Breaking Changes

1. **All main endpoints now require authentication**
   - Frontend automatically handles this with axios interceptors
   - Manual API calls must include `Authorization: Bearer <token>` header

2. **user_id parameter removed from requests**
   - User is identified by JWT token
   - Backend automatically associates data with authenticated user

### Backward Compatibility

- Health check endpoint (`GET /`) still works without authentication
- Old localStorage saved answers need to be re-saved to the database

## Troubleshooting

### "401 Unauthorized" errors
- Token may have expired (7 days)
- User needs to log in again
- Check that token is being sent in request headers

### Database migration errors
- Ensure database is running
- Check `DATABASE_URL` in `.env`
- Try: `alembic downgrade -1` then `alembic upgrade head`

### Can't log in
- Check that migrations have run
- Verify user exists in database
- Check backend logs for errors

## Next Steps

Consider implementing:
- Password reset functionality
- Email verification
- Remember me feature
- Social login (Google, Facebook)
- Profile management
- Export/import saved answers
- Sharing saved answers with other users

## File Structure

```
backend/
├── alembic/versions/
│   ├── 0003_add_auth_to_users.py
│   └── 0004_create_saved_answers.py
├── app/
│   ├── auth.py (NEW)
│   ├── config.py (UPDATED)
│   ├── database.py (UPDATED)
│   ├── main.py (UPDATED)
│   ├── models/
│   │   └── schemas.py (UPDATED)
│   └── routers/ (NEW)
│       ├── auth.py
│       └── saved_answers.py
└── requirements.txt (UPDATED)

frontend/
├── src/
│   ├── composables/
│   │   └── useAuth.js (NEW)
│   ├── router/
│   │   └── index.js (UPDATED)
│   ├── services/
│   │   ├── authService.js (NEW)
│   │   ├── axiosConfig.js (NEW)
│   │   ├── savedAnswersService.js (UPDATED)
│   │   └── savedAnswersService.old.js (BACKUP)
│   ├── views/
│   │   ├── Home.vue (NEW)
│   │   ├── Login.vue (NEW)
│   │   └── Register.vue (NEW)
│   └── main.js (UPDATED)
```

## Support

If you encounter any issues:
1. Check the browser console for frontend errors
2. Check backend logs for API errors
3. Verify all migrations have run successfully
4. Ensure SECRET_KEY is set in backend .env
5. Clear browser localStorage and try again

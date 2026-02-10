# Django Backend Setup

## Quick Start Commands

### 1. Setup Virtual Environment
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
```

### 2. Install Dependencies
```bash
pip install -r ../requirements.txt
```

### 3. Database Setup
```bash
# Create PostgreSQL database
createdb collabo_db

# Copy environment file
copy .env.example .env
# Edit .env with your database credentials and Stripe keys
```

### 4. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser
```bash
python manage.py createsuperuser
```

### 6. Start Server
```bash
python manage.py runserver
```

## API Endpoints

### Authentication
- POST `/api/auth/register/` - User registration
- POST `/api/auth/login/` - User login
- POST `/api/auth/token/refresh/` - Refresh JWT token
- GET `/api/auth/profile/` - Get user profile
- GET/PUT `/api/auth/influencer-profile/` - Influencer profile
- GET/PUT `/api/auth/company-profile/` - Company profile
- GET `/api/auth/influencers/` - List influencers
- GET `/api/auth/companies/` - List companies

### Campaigns & Collaborations
- GET/POST `/api/collaborations/campaigns/` - List/Create campaigns
- GET/PUT/DELETE `/api/collaborations/campaigns/{id}/` - Campaign details
- GET/POST `/api/collaborations/requests/` - Collaboration requests
- GET/PUT `/api/collaborations/requests/{id}/` - Request details
- POST `/api/collaborations/requests/{id}/accept/` - Accept request
- GET `/api/collaborations/collaborations/` - List collaborations
- GET/PUT `/api/collaborations/collaborations/{id}/` - Collaboration details
- GET/POST `/api/collaborations/reviews/` - Reviews

### Payments
- GET `/api/payments/payments/` - List payments
- POST `/api/payments/create-payment-intent/` - Create Stripe payment
- POST `/api/payments/confirm-payment/` - Confirm payment
- GET/POST `/api/payments/payouts/` - Payouts
- GET `/api/payments/earnings/` - Earnings summary

## Models

### User Types
- `influencer` - Content creators
- `company` - Businesses looking for influencers
- `admin` - Platform administrators

### Key Models
- `User` - Custom user model with role-based access
- `InfluencerProfile` - Influencer-specific data
- `CompanyProfile` - Company-specific data
- `Campaign` - Marketing campaigns created by companies
- `CollaborationRequest` - Applications from influencers
- `Collaboration` - Active partnerships
- `Payment` - Payment processing with Stripe
- `Review` - Ratings and feedback

## Environment Variables

Required in `.env`:
```
SECRET_KEY=your-django-secret-key
DEBUG=True
DB_NAME=collabo_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
REDIS_URL=redis://localhost:6379
```
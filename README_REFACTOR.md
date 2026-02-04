# MintProxy - Premium Residential Proxies

## Architecture & Best Practices

### Code Quality Improvements
- **Security**: Configuration management through environment variables with secure fallbacks
- **Code Structure**: Modular helper functions (`_validate_region_country`, `_get_country_name`, `_generate_proxy_data`) eliminate code duplication
- **Error Handling**: Proper exception handling with try-except blocks and error recovery
- **JSON Parsing**: Replaced unsafe `eval()` with `json.loads()` for secure data serialization
- **Authentication**: Decorator-based access control with `@login_required` for cleaner route protection

### Technical Stack
- Flask web framework
- SQLite3 database with proper indexing
- Werkzeug for password hashing
- Environment-based configuration

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables (create `.env` from `.env.example`):
```bash
export SECRET_KEY="your-secure-key"
export ADMIN_USERNAME="admin"
export ADMIN_PASSWORD="your-secure-password"
export BANK_CARD="5599 0021 1503 7915"
```

3. Run the application:
```bash
python main.py
```

The app will be available at `http://localhost:8080`

## Key Features

- **Global Proxy Network**: Coverage across 5 continents and 70+ countries
- **Secure Admin Panel**: Role-based access control at `/admin`
- **Payment Processing**: RESTful payment workflow with unique transaction IDs
- **Database Optimization**: Indexed queries for efficient payment lookups
- **Error Handling**: Graceful 404/500 error pages with professional UI

## Admin Panel

Access at `http://localhost:8080/admin/login` with configured credentials.

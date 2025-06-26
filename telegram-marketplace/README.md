# Telegram Marketplace System

A complete Telegram marketplace system with multi-account management, member scraping, real-time monitoring, analytics, escrow services, and compliance features.

## Features

### ✅ Core Features Implemented

1. **Multi-Account Authentication** - Login and manage 500+ Telegram accounts with 2FA support
2. **Member Scraping Engine** - Advanced member scraping with filters and rate limiting
3. **Account Rotation System** - Intelligent account selection based on success rate, age, and activity
4. **Real-time Account Monitoring** - Live status monitoring with Redis caching and WebSocket updates
5. **Group Search Functionality** - Search and discover public groups and channels
6. **Proxy Rotation System** - Automatic proxy switching with health monitoring
7. **Human Behavior Simulation** - Anti-detection through realistic behavior patterns
8. **Automated Account Recovery** - Automatic recovery of banned/restricted accounts
9. **Compliance Safeguards** - GDPR-compliant data handling and anonymization
10. **Marketplace Transaction Engine** - Escrow service for secure transactions
11. **Bulk Action Scheduler** - Timezone-aware bulk operations scheduling
12. **Anti-Detection System** - Fingerprint randomization and evasion techniques
13. **Analytics Engine** - Group scoring and engagement analysis
14. **Credit System** - Pay-per-action credit system with multiple packages
15. **Forensic Cleanup** - Secure session data deletion and cleanup

## Project Structure

```
telegram-marketplace/
├── server/                 # Python FastAPI backend
│   ├── auth/              # Authentication modules
│   ├── core/              # Core business logic
│   ├── scraping/          # Member scraping
│   ├── monitoring/        # Account monitoring
│   ├── search/            # Group search
│   ├── infrastructure/    # Proxy management
│   ├── security/          # Anti-detection & cleanup
│   ├── accounts/          # Account recovery
│   ├── compliance/        # GDPR compliance
│   ├── marketplace/       # Escrow service
│   ├── scheduling/        # Bulk operations
│   ├── analytics/         # Analytics engine
│   ├── billing/           # Credit system
│   └── main.py           # FastAPI application
├── client/                # React Next.js frontend
│   ├── pages/            # Dashboard pages
│   ├── components/       # UI components
│   ├── lib/              # API utilities
│   └── styles/           # CSS styles
├── requirements.txt      # Python dependencies
└── .env.template        # Environment variables
```

## Installation

### Backend Setup

1. **Install Python dependencies:**
```bash
cd server
pip install -r requirements.txt
```

2. **Set up environment variables:**
```bash
cp .env.template .env
# Edit .env with your Telegram API credentials
```

3. **Start the server:**
```bash
python main.py
```

### Frontend Setup

1. **Install Node.js dependencies:**
```bash
cd client
npm install
```

2. **Start the development server:**
```bash
npm run dev
```

## Configuration

### Environment Variables

Create a `.env` file in the server directory:

```env
# Telegram API Credentials
API_ID=1234567
API_HASH=yourapihash123

# Database Configuration
REDIS_URL=redis://localhost:6379
DB_URL=postgres://user:pass@localhost:5432/telemarket

# Proxy Configuration
PROXY_LIST=proxy1:port,proxy2:port,proxy3:port

# Security Settings
SESSION_ENCRYPTION_KEY=your_encryption_key_here
```

### Required Services

- **Redis** - For caching and real-time monitoring
- **PostgreSQL** - For data persistence (optional for demo)
- **Proxy Servers** - For IP rotation (optional for demo)

## API Documentation

### Authentication Endpoints

- `POST /auth/login` - Login with Telegram credentials
- `GET /auth/status` - Check authentication status

### Account Management

- `POST /accounts/add` - Add account to rotation pool
- `GET /accounts/stats` - Get account statistics
- `GET /accounts/best` - Get best available account

### Scraping & Search

- `POST /scrape/members` - Scrape members from groups
- `POST /search/groups` - Search for public groups

### Monitoring

- `GET /monitoring/accounts` - Get monitoring statistics
- `GET /monitoring/status/{phone}` - Get specific account status

### Analytics

- `POST /analytics/score-group` - Calculate group engagement score

### Credits & Billing

- `GET /credits/balance` - Get user credit balance
- `POST /credits/purchase` - Purchase credit packages
- `GET /credits/packages` - Get available packages

### Marketplace

- `POST /marketplace/create-transaction` - Create escrow transaction
- `POST /marketplace/confirm-transaction` - Confirm transaction

## Usage Examples

### Basic Member Scraping

```python
from auth.telegram_auth import AuthManager
from scraping.member_scraper import MemberScraper

# Initialize auth
auth = AuthManager("sessions/+1234567890", API_ID, API_HASH)
client = await auth.initialize_client()

# Scrape members
scraper = MemberScraper(client)
members = await scraper.scrape_members("@example_group", limit=500)
```

### Account Rotation

```python
from core.account_rotator import AccountRotator

rotator = AccountRotator()
rotator.add_account("+1234567890", "sessions/+1234567890")
rotator.add_account("+1234567891", "sessions/+1234567891")

# Get best account
best_account = rotator.get_best_account()
```

### Group Scoring

```python
from analytics.group_scorer import GroupScorer

scorer = GroupScorer()
score_result = scorer.calculate_group_score("example_group_id")
print(f"Group score: {score_result['final_score']}/100")
```

## Dashboard Features

### Account Monitor
- Real-time account status display
- Success rate tracking
- Account health monitoring
- Recovery management

### Scraping Panel
- Member scraping interface
- Group search functionality
- Filter options
- Results visualization

### Analytics Dashboard
- Group scoring tool
- Performance charts
- Trend analysis
- Reporting system

### Credit Management
- Balance display
- Package purchasing
- Usage tracking
- Transaction history

## Security Features

### Anti-Detection
- Fingerprint randomization
- Proxy rotation
- Human behavior simulation
- Rate limiting
- Session management

### Compliance
- GDPR data handling
- User data anonymization
- Audit logging
- Data export/deletion

### Forensic Cleanup
- Secure session deletion
- Temporary file cleanup
- Memory trace clearing
- Evidence removal

## Performance & Scaling

### Rate Limiting
- 200 accounts per hour default
- Intelligent spacing
- Timezone-aware scheduling
- Burst protection

### Monitoring
- Real-time status updates
- Health checks every 15 seconds
- Automatic failover
- Performance metrics

### Caching
- Redis for session state
- Account status caching
- Result caching
- Real-time updates

## Legal & Compliance

This system includes built-in compliance features:

- **GDPR Compliance** - Data anonymization and deletion
- **Rate Limiting** - Respects platform limits
- **Terms of Service** - Configurable compliance checks
- **Audit Logging** - Complete action tracking

## Development

### Adding New Features

1. **Backend**: Add new modules in `/server/`
2. **Frontend**: Create components in `/client/components/`
3. **API**: Add endpoints in `/server/main.py`
4. **Database**: Update models as needed

### Testing

```bash
# Backend tests
cd server
python -m pytest

# Frontend tests
cd client
npm test
```

## Deployment

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d
```

### Production Setup

1. Configure environment variables
2. Set up Redis and PostgreSQL
3. Configure proxy servers
4. Set up SSL certificates
5. Configure monitoring

## Support

For issues and questions:

1. Check the documentation
2. Review error logs
3. Verify configuration
4. Check API status

## License

This project is for educational and research purposes. Ensure compliance with Telegram's Terms of Service and local laws.

---

**⚠️ Important Notice**: This system is designed for legitimate business use cases. Users are responsible for complying with all applicable laws and platform terms of service.

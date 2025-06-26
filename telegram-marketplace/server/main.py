from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
import os
from dotenv import load_dotenv
import logging
from typing import Dict, Any, List, Optional

# Import our modules
from auth.telegram_auth import AuthManager
from core.account_rotator import AccountRotator
from scraping.member_scraper import MemberScraper
from monitoring.live_monitor import LiveMonitor
from search.group_finder import GroupFinder
from infrastructure.proxy_manager import ProxyHandler
from security.behavior_simulator import BehaviorSimulator
from security.antidetect import AntiDetectSystem
from accounts.recovery import AccountRecovery
from compliance.gdpr import GDPRHandler
from marketplace.escrow import EscrowService
from scheduling.bulk_actions import BulkActionScheduler
from analytics.group_scorer import GroupScorer
from billing.credit_manager import CreditSystem
from security.cleanup import ForensicCleanup

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Telegram Marketplace API",
    description="Complete Telegram marketplace system with account management, scraping, and analytics",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Global instances
account_rotator = AccountRotator()
live_monitor = LiveMonitor(os.getenv('REDIS_URL', 'redis://localhost:6379'))
proxy_handler = ProxyHandler(os.getenv('PROXY_LIST', '').split(',') if os.getenv('PROXY_LIST') else [])
behavior_simulator = BehaviorSimulator()
antidetect_system = AntiDetectSystem()
account_recovery = AccountRecovery()
gdpr_handler = GDPRHandler()
escrow_service = EscrowService()
bulk_scheduler = BulkActionScheduler(account_rotator)
group_scorer = GroupScorer()
credit_system = CreditSystem()
forensic_cleanup = ForensicCleanup()

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # In production, implement proper JWT token validation
    return {"user_id": "demo_user"}

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Telegram Marketplace API",
        "status": "running",
        "version": "1.0.0"
    }

# Authentication endpoints
@app.post("/auth/login")
async def login(phone: str, code: str = None, password: str = None):
    """Login with Telegram credentials"""
    try:
        api_id = int(os.getenv('API_ID'))
        api_hash = os.getenv('API_HASH')
        
        auth_manager = AuthManager(f"sessions/{phone}", api_id, api_hash)
        result = await auth_manager.login(phone, code, password)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/auth/status")
async def auth_status(phone: str):
    """Check authentication status"""
    try:
        api_id = int(os.getenv('API_ID'))
        api_hash = os.getenv('API_HASH')
        
        auth_manager = AuthManager(f"sessions/{phone}", api_id, api_hash)
        await auth_manager.initialize_client()
        is_auth = await auth_manager.is_authenticated()
        
        return {"phone": phone, "authenticated": is_auth}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Account management endpoints
@app.post("/accounts/add")
async def add_account(phone: str, session_path: str, proxy: str = None, user: dict = Depends(get_current_user)):
    """Add account to rotation pool"""
    account_rotator.add_account(phone, session_path, proxy)
    return {"status": "success", "message": f"Account {phone} added to rotation pool"}

@app.get("/accounts/stats")
async def get_account_stats(user: dict = Depends(get_current_user)):
    """Get account statistics"""
    return account_rotator.get_account_stats()

@app.get("/accounts/best")
async def get_best_account(user: dict = Depends(get_current_user)):
    """Get the best available account"""
    account = account_rotator.get_best_account()
    if account:
        return account
    else:
        raise HTTPException(status_code=404, detail="No available accounts")

# Scraping endpoints
@app.post("/scrape/members")
async def scrape_members(source: str, limit: int = 500, user: dict = Depends(get_current_user)):
    """Scrape members from a group or channel"""
    try:
        # Check credits
        credit_check = credit_system.can_afford_action(user["user_id"], "SCRAPE")
        if not credit_check["can_afford"]:
            raise HTTPException(status_code=402, detail="Insufficient credits")
        
        # Get best account
        account = account_rotator.get_best_account()
        if not account:
            raise HTTPException(status_code=503, detail="No available accounts")
        
        # Initialize client and scraper
        api_id = int(os.getenv('API_ID'))
        api_hash = os.getenv('API_HASH')
        auth_manager = AuthManager(account['session_path'], api_id, api_hash)
        client = await auth_manager.initialize_client()
        
        scraper = MemberScraper(client)
        members = await scraper.scrape_members(source, limit)
        
        # Deduct credits
        credit_system.deduct_credits(user["user_id"], "SCRAPE")
        
        # Mark account as used
        account_rotator.mark_account_used(account['phone'], True)
        
        return {
            "source": source,
            "members_scraped": len(members),
            "members": members
        }
    except Exception as e:
        if 'account' in locals():
            account_rotator.mark_account_used(account['phone'], False)
        raise HTTPException(status_code=400, detail=str(e))

# Search endpoints
@app.post("/search/groups")
async def search_groups(query: str, limit: int = 50, user: dict = Depends(get_current_user)):
    """Search for groups and channels"""
    try:
        # Check credits
        credit_check = credit_system.can_afford_action(user["user_id"], "SEARCH")
        if not credit_check["can_afford"]:
            raise HTTPException(status_code=402, detail="Insufficient credits")
        
        account = account_rotator.get_best_account()
        if not account:
            raise HTTPException(status_code=503, detail="No available accounts")
        
        api_id = int(os.getenv('API_ID'))
        api_hash = os.getenv('API_HASH')
        auth_manager = AuthManager(account['session_path'], api_id, api_hash)
        client = await auth_manager.initialize_client()
        
        group_finder = GroupFinder(client)
        results = await group_finder.search_entities(query, limit=limit)
        
        # Deduct credits
        credit_system.deduct_credits(user["user_id"], "SEARCH")
        
        return {"query": query, "results": results}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Monitoring endpoints
@app.get("/monitoring/accounts")
async def get_account_monitoring(user: dict = Depends(get_current_user)):
    """Get account monitoring statistics"""
    return live_monitor.get_account_statistics()

@app.get("/monitoring/status/{phone}")
async def get_account_status(phone: str, user: dict = Depends(get_current_user)):
    """Get specific account status"""
    status = live_monitor.get_account_status(phone)
    if status:
        return status
    else:
        raise HTTPException(status_code=404, detail="Account not found")

# Proxy management endpoints
@app.get("/proxy/stats")
async def get_proxy_stats(user: dict = Depends(get_current_user)):
    """Get proxy statistics"""
    return proxy_handler.get_proxy_stats()

@app.post("/proxy/test")
async def test_proxies(user: dict = Depends(get_current_user)):
    """Test all proxies"""
    results = await proxy_handler.test_all_proxies()
    return {"test_results": results}

# Analytics endpoints
@app.post("/analytics/score-group")
async def score_group(group_id: str, user: dict = Depends(get_current_user)):
    """Calculate group engagement score"""
    try:
        # Check credits
        credit_check = credit_system.can_afford_action(user["user_id"], "ANALYTICS_REPORT")
        if not credit_check["can_afford"]:
            raise HTTPException(status_code=402, detail="Insufficient credits")
        
        score_result = group_scorer.calculate_group_score(group_id)
        
        # Deduct credits
        credit_system.deduct_credits(user["user_id"], "ANALYTICS_REPORT")
        
        return score_result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Marketplace endpoints
@app.post("/marketplace/create-transaction")
async def create_transaction(buyer: str, seller: str, amount: float, description: str = None, user: dict = Depends(get_current_user)):
    """Create escrow transaction"""
    try:
        tx_id = escrow_service.create_transaction(buyer, seller, amount, description)
        return {"transaction_id": tx_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/marketplace/confirm-transaction")
async def confirm_transaction(tx_id: str, role: str, user: dict = Depends(get_current_user)):
    """Confirm transaction"""
    try:
        result = escrow_service.confirm_transaction(tx_id, user["user_id"], role)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Credit system endpoints
@app.get("/credits/balance")
async def get_credit_balance(user: dict = Depends(get_current_user)):
    """Get user credit balance"""
    balance = credit_system.get_user_credits(user["user_id"])
    return {"user_id": user["user_id"], "credits": balance}

@app.post("/credits/purchase")
async def purchase_credits(package: str, user: dict = Depends(get_current_user)):
    """Purchase credit package"""
    try:
        result = credit_system.purchase_credits(user["user_id"], package)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/credits/packages")
async def get_credit_packages():
    """Get available credit packages"""
    return credit_system.get_available_packages()

# Bulk operations endpoints
@app.post("/bulk/schedule-add-members")
async def schedule_add_members(group: str, users: List[str], accounts_per_hour: int = 200, timezone: str = 'UTC', user: dict = Depends(get_current_user)):
    """Schedule bulk member addition"""
    try:
        task_id = bulk_scheduler.schedule_add_members(group, users, accounts_per_hour, timezone)
        return {"task_id": task_id, "status": "scheduled"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/bulk/task-status/{task_id}")
async def get_task_status(task_id: str, user: dict = Depends(get_current_user)):
    """Get bulk task status"""
    status = bulk_scheduler.get_task_status(task_id)
    return status

# GDPR compliance endpoints
@app.post("/gdpr/request")
async def gdpr_request(user_id: str, request_type: str, user: dict = Depends(get_current_user)):
    """Handle GDPR data request"""
    try:
        result = gdpr_handler.handle_data_request(user_id, request_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Security endpoints
@app.post("/security/cleanup-session")
async def cleanup_session(session_path: str, user: dict = Depends(get_current_user)):
    """Clean up session data"""
    try:
        result = forensic_cleanup.wipe_session_data(session_path)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/security/randomize-fingerprint")
async def randomize_fingerprint(user: dict = Depends(get_current_user)):
    """Generate randomized device fingerprint"""
    fingerprint = antidetect_system.randomize_fingerprint()
    return fingerprint

# Background tasks
@app.on_event("startup")
async def startup_event():
    """Initialize background tasks"""
    logger.info("Starting Telegram Marketplace API")
    
    # Start account monitoring
    # asyncio.create_task(live_monitor.start_monitoring())

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Telegram Marketplace API")
    live_monitor.stop_monitoring()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

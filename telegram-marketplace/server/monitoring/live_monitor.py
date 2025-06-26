import asyncio
import redis
import json
import time
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class LiveMonitor:
    def __init__(self, redis_url: str):
        self.redis_client = redis.from_url(redis_url)
        self.monitoring = False
        self.accounts = []
    
    def add_account(self, phone: str, client):
        """Add account to monitoring list"""
        self.accounts.append({
            'phone': phone,
            'client': client
        })
    
    async def start_monitoring(self):
        """Start continuous account monitoring"""
        self.monitoring = True
        logger.info("Started account monitoring")
        
        while self.monitoring:
            await self._check_all_accounts()
            await asyncio.sleep(15)  # 15-second checks as per specification
    
    def stop_monitoring(self):
        """Stop account monitoring"""
        self.monitoring = False
        logger.info("Stopped account monitoring")
    
    async def _check_all_accounts(self):
        """Check health of all accounts"""
        for account in self.accounts:
            try:
                status = await self._check_account_health(account)
                self._store_account_status(account['phone'], status)
            except Exception as e:
                logger.error(f"Error checking account {account['phone']}: {str(e)}")
                self._store_account_status(account['phone'], {
                    'status': 'ERROR',
                    'error': str(e),
                    'timestamp': time.time()
                })
    
    async def _check_account_health(self, account) -> Dict[str, Any]:
        """Check individual account health"""
        phone = account['phone']
        client = account['client']
        
        try:
            # Check if client is connected
            if not client.is_connected():
                await client.connect()
            
            # Check if authorized
            is_authorized = await client.is_user_authorized()
            
            if not is_authorized:
                return {
                    'status': 'UNAUTHORIZED',
                    'phone': phone,
                    'timestamp': time.time(),
                    'last_check': time.time()
                }
            
            # Try to get user info to verify account is working
            me = await client.get_me()
            
            # Check for flood wait or restrictions
            # This is a basic check - in production you'd want more sophisticated detection
            
            return {
                'status': 'LIVE',
                'phone': phone,
                'user_id': me.id,
                'username': me.username,
                'timestamp': time.time(),
                'last_check': time.time()
            }
            
        except Exception as e:
            error_msg = str(e).lower()
            
            if 'flood' in error_msg:
                status = 'FLOOD_WAIT'
            elif 'banned' in error_msg or 'restricted' in error_msg:
                status = 'BANNED'
            elif 'unauthorized' in error_msg:
                status = 'UNAUTHORIZED'
            else:
                status = 'ERROR'
            
            return {
                'status': status,
                'phone': phone,
                'error': str(e),
                'timestamp': time.time(),
                'last_check': time.time()
            }
    
    def _store_account_status(self, phone: str, status: Dict[str, Any]):
        """Store account status in Redis"""
        try:
            key = f"acc:{phone}:status"
            self.redis_client.setex(key, 300, json.dumps(status))  # 5-minute TTL
            
            # Also store in a hash for easier querying
            self.redis_client.hset("account_statuses", phone, json.dumps(status))
            
        except Exception as e:
            logger.error(f"Error storing status for {phone}: {str(e)}")
    
    def get_account_status(self, phone: str) -> Dict[str, Any]:
        """Get current status of an account"""
        try:
            status_data = self.redis_client.hget("account_statuses", phone)
            if status_data:
                return json.loads(status_data)
            return None
        except Exception as e:
            logger.error(f"Error getting status for {phone}: {str(e)}")
            return None
    
    def get_all_account_statuses(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all monitored accounts"""
        try:
            all_statuses = self.redis_client.hgetall("account_statuses")
            return {
                phone.decode(): json.loads(status.decode())
                for phone, status in all_statuses.items()
            }
        except Exception as e:
            logger.error(f"Error getting all account statuses: {str(e)}")
            return {}
    
    def get_live_accounts(self) -> list:
        """Get list of currently live accounts"""
        all_statuses = self.get_all_account_statuses()
        return [
            phone for phone, status in all_statuses.items()
            if status.get('status') == 'LIVE'
        ]
    
    def get_account_statistics(self) -> Dict[str, Any]:
        """Get monitoring statistics"""
        all_statuses = self.get_all_account_statuses()
        
        stats = {
            'total': len(all_statuses),
            'live': 0,
            'banned': 0,
            'unauthorized': 0,
            'flood_wait': 0,
            'error': 0
        }
        
        for status in all_statuses.values():
            status_type = status.get('status', 'error').lower()
            if status_type == 'live':
                stats['live'] += 1
            elif status_type == 'banned':
                stats['banned'] += 1
            elif status_type == 'unauthorized':
                stats['unauthorized'] += 1
            elif status_type == 'flood_wait':
                stats['flood_wait'] += 1
            else:
                stats['error'] += 1
        
        return stats

import random
import time
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class AccountRotator:
    def __init__(self):
        self.accounts: List[Dict[str, Any]] = []
        
    def add_account(self, phone: str, session_path: str, proxy: Optional[str] = None):
        """Add an account to the rotation pool"""
        account = {
            'phone': phone,
            'session_path': session_path,
            'proxy': proxy,
            'status': 'LIVE',
            'success_rate': 1.0,
            'age': 30,  # days
            'activity': 0.8,
            'last_used': None,
            'total_actions': 0,
            'successful_actions': 0,
            'banned_count': 0,
            'rate_limit_count': 0
        }
        self.accounts.append(account)
        logger.info(f"Added account {phone} to rotation pool")
    
    def get_best_account(self) -> Optional[Dict[str, Any]]:
        """Get the best available account based on weighted scoring"""
        live_accounts = [acc for acc in self.accounts if acc['status'] == 'LIVE']
        
        if not live_accounts:
            return None
        
        # Calculate score for each account
        scored_accounts = []
        for acc in live_accounts:
            score = self._calculate_account_score(acc)
            scored_accounts.append((acc, score))
        
        # Sort by score (highest first)
        scored_accounts.sort(key=lambda x: x[1], reverse=True)
        
        best_account = scored_accounts[0][0]
        logger.info(f"Selected account {best_account['phone']} (score: {scored_accounts[0][1]:.3f})")
        
        return best_account
    
    def _calculate_account_score(self, account: Dict[str, Any]) -> float:
        """Calculate weighted score for account selection"""
        success_rate = account['success_rate']
        age_score = min(account['age'] / 365, 1.0)  # Normalize to max 1 year
        activity_score = account['activity']
        
        # Penalty factors
        cooldown_penalty = self._get_cooldown_penalty(account)
        rate_limit_penalty = max(0, 1 - (account['rate_limit_count'] * 0.1))
        ban_penalty = max(0, 1 - (account['banned_count'] * 0.2))
        
        # Weighted calculation (as per specification)
        score = (
            success_rate * 0.7 +
            age_score * 0.2 +
            activity_score * 0.1
        ) * cooldown_penalty * rate_limit_penalty * ban_penalty
        
        return score
    
    def _get_cooldown_penalty(self, account: Dict[str, Any]) -> float:
        """Apply cooldown penalty if account was used recently"""
        if not account['last_used']:
            return 1.0
        
        time_since_use = time.time() - account['last_used']
        
        # Apply penalty if used within last hour
        if time_since_use < 3600:  # 1 hour
            return 0.5
        elif time_since_use < 1800:  # 30 minutes
            return 0.3
        
        return 1.0
    
    def mark_account_used(self, phone: str, success: bool = True):
        """Mark account as used and update statistics"""
        for account in self.accounts:
            if account['phone'] == phone:
                account['last_used'] = time.time()
                account['total_actions'] += 1
                
                if success:
                    account['successful_actions'] += 1
                
                # Update success rate
                account['success_rate'] = account['successful_actions'] / account['total_actions']
                break
    
    def mark_account_banned(self, phone: str):
        """Mark account as banned"""
        for account in self.accounts:
            if account['phone'] == phone:
                account['status'] = 'BANNED'
                account['banned_count'] += 1
                logger.warning(f"Account {phone} marked as banned")
                break
    
    def mark_account_rate_limited(self, phone: str):
        """Mark account as rate limited"""
        for account in self.accounts:
            if account['phone'] == phone:
                account['rate_limit_count'] += 1
                logger.warning(f"Account {phone} hit rate limit")
                break
    
    def get_account_stats(self) -> Dict[str, Any]:
        """Get statistics about all accounts"""
        total = len(self.accounts)
        live = len([acc for acc in self.accounts if acc['status'] == 'LIVE'])
        banned = len([acc for acc in self.accounts if acc['status'] == 'BANNED'])
        
        avg_success_rate = sum(acc['success_rate'] for acc in self.accounts) / total if total > 0 else 0
        
        return {
            'total_accounts': total,
            'live_accounts': live,
            'banned_accounts': banned,
            'average_success_rate': avg_success_rate
        }
    
    def get_accounts_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get accounts filtered by status"""
        return [acc for acc in self.accounts if acc['status'] == status]

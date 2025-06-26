import time
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class CreditSystem:
    def __init__(self, database_connection=None):
        self.db = database_connection
        self.user_credits = {}  # In-memory storage for demo
        
        # Cost matrix for different actions
        self.cost_matrix = {
            'SCRAPE': 5,
            'ADD_MEMBER': 1,
            'SEARCH': 2,
            'JOIN_GROUP': 3,
            'SEND_MESSAGE': 1,
            'BULK_SCRAPE': 20,
            'PREMIUM_SEARCH': 5,
            'ANALYTICS_REPORT': 10
        }
        
        # Credit packages
        self.credit_packages = {
            'starter': {'credits': 100, 'price': 9.99},
            'standard': {'credits': 500, 'price': 39.99},
            'premium': {'credits': 1500, 'price': 99.99},
            'enterprise': {'credits': 5000, 'price': 299.99}
        }
    
    def get_user_credits(self, user_id: str) -> int:
        """Get current credit balance for user"""
        if self.db:
            # Query database for user credits
            return self._get_credits_from_db(user_id)
        else:
            return self.user_credits.get(user_id, 0)
    
    def add_credits(self, user_id: str, amount: int, reason: str = None) -> Dict[str, Any]:
        """Add credits to user account"""
        current_credits = self.get_user_credits(user_id)
        new_balance = current_credits + amount
        
        if self.db:
            success = self._update_credits_in_db(user_id, new_balance)
        else:
            self.user_credits[user_id] = new_balance
            success = True
        
        if success:
            # Log credit transaction
            self._log_credit_transaction(user_id, amount, 'ADD', reason)
            
            logger.info(f"Added {amount} credits to user {user_id}. New balance: {new_balance}")
            
            return {
                'status': 'success',
                'user_id': user_id,
                'credits_added': amount,
                'new_balance': new_balance,
                'reason': reason
            }
        else:
            return {
                'status': 'error',
                'message': 'Failed to add credits'
            }
    
    def deduct_credits(self, user_id: str, action_type: str, custom_amount: int = None) -> Dict[str, Any]:
        """Deduct credits for an action"""
        cost = custom_amount if custom_amount is not None else self.cost_matrix.get(action_type, 1)
        current_credits = self.get_user_credits(user_id)
        
        if current_credits < cost:
            return {
                'status': 'insufficient_credits',
                'user_id': user_id,
                'required_credits': cost,
                'current_credits': current_credits,
                'shortfall': cost - current_credits
            }
        
        new_balance = current_credits - cost
        
        if self.db:
            success = self._update_credits_in_db(user_id, new_balance)
        else:
            self.user_credits[user_id] = new_balance
            success = True
        
        if success:
            # Log credit transaction
            self._log_credit_transaction(user_id, -cost, 'DEDUCT', action_type)
            
            logger.info(f"Deducted {cost} credits from user {user_id} for {action_type}. New balance: {new_balance}")
            
            return {
                'status': 'success',
                'user_id': user_id,
                'action_type': action_type,
                'credits_deducted': cost,
                'new_balance': new_balance
            }
        else:
            return {
                'status': 'error',
                'message': 'Failed to deduct credits'
            }
    
    def purchase_credits(self, user_id: str, package_name: str, payment_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """Purchase credits package"""
        if package_name not in self.credit_packages:
            return {
                'status': 'error',
                'message': f'Invalid package: {package_name}'
            }
        
        package = self.credit_packages[package_name]
        
        # Process payment (mock implementation)
        payment_result = self._process_payment(user_id, package['price'], payment_info)
        
        if payment_result['status'] == 'success':
            # Add credits to user account
            credit_result = self.add_credits(
                user_id, 
                package['credits'], 
                f"Purchase: {package_name} package"
            )
            
            if credit_result['status'] == 'success':
                return {
                    'status': 'success',
                    'user_id': user_id,
                    'package': package_name,
                    'credits_purchased': package['credits'],
                    'amount_paid': package['price'],
                    'new_balance': credit_result['new_balance'],
                    'transaction_id': payment_result['transaction_id']
                }
            else:
                # Refund if credit addition failed
                self._process_refund(payment_result['transaction_id'])
                return {
                    'status': 'error',
                    'message': 'Credit addition failed, payment refunded'
                }
        else:
            return {
                'status': 'payment_failed',
                'message': payment_result.get('message', 'Payment processing failed')
            }
    
    def check_action_cost(self, action_type: str) -> int:
        """Get the credit cost for an action"""
        return self.cost_matrix.get(action_type, 1)
    
    def can_afford_action(self, user_id: str, action_type: str, quantity: int = 1) -> Dict[str, Any]:
        """Check if user can afford an action"""
        cost_per_action = self.check_action_cost(action_type)
        total_cost = cost_per_action * quantity
        current_credits = self.get_user_credits(user_id)
        
        return {
            'can_afford': current_credits >= total_cost,
            'current_credits': current_credits,
            'required_credits': total_cost,
            'cost_per_action': cost_per_action,
            'quantity': quantity
        }
    
    def get_credit_history(self, user_id: str, limit: int = 50) -> list:
        """Get user's credit transaction history"""
        if self.db:
            return self._get_credit_history_from_db(user_id, limit)
        else:
            # Mock history for demo
            return [
                {
                    'id': 1,
                    'user_id': user_id,
                    'amount': 100,
                    'type': 'ADD',
                    'reason': 'Initial credits',
                    'timestamp': time.time() - 86400
                }
            ]
    
    def get_credit_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get credit usage statistics for user"""
        history = self.get_credit_history(user_id, 1000)  # Get more for stats
        
        total_earned = sum(tx['amount'] for tx in history if tx['amount'] > 0)
        total_spent = sum(abs(tx['amount']) for tx in history if tx['amount'] < 0)
        
        # Action breakdown
        action_costs = {}
        for tx in history:
            if tx['amount'] < 0 and tx.get('reason'):
                action = tx['reason']
                action_costs[action] = action_costs.get(action, 0) + abs(tx['amount'])
        
        return {
            'current_balance': self.get_user_credits(user_id),
            'total_earned': total_earned,
            'total_spent': total_spent,
            'transaction_count': len(history),
            'action_breakdown': action_costs,
            'average_daily_spend': total_spent / 30 if len(history) > 0 else 0  # Last 30 days estimate
        }
    
    def apply_discount(self, user_id: str, discount_code: str) -> Dict[str, Any]:
        """Apply discount code for credit bonus"""
        discount_codes = {
            'WELCOME10': {'bonus_percentage': 10, 'max_uses': 1},
            'BULK20': {'bonus_percentage': 20, 'max_uses': 3},
            'PREMIUM50': {'bonus_percentage': 50, 'max_uses': 1}
        }
        
        if discount_code not in discount_codes:
            return {'status': 'invalid_code', 'message': 'Invalid discount code'}
        
        discount = discount_codes[discount_code]
        
        # Check if user has already used this code
        if self._has_used_discount(user_id, discount_code):
            return {'status': 'already_used', 'message': 'Discount code already used'}
        
        # Apply bonus credits
        current_credits = self.get_user_credits(user_id)
        bonus_credits = int(current_credits * discount['bonus_percentage'] / 100)
        
        if bonus_credits > 0:
            result = self.add_credits(user_id, bonus_credits, f"Discount: {discount_code}")
            
            if result['status'] == 'success':
                self._mark_discount_used(user_id, discount_code)
                
                return {
                    'status': 'success',
                    'discount_code': discount_code,
                    'bonus_credits': bonus_credits,
                    'new_balance': result['new_balance']
                }
        
        return {'status': 'error', 'message': 'Failed to apply discount'}
    
    def _get_credits_from_db(self, user_id: str) -> int:
        """Get credits from database"""
        # Mock implementation
        return self.user_credits.get(user_id, 0)
    
    def _update_credits_in_db(self, user_id: str, new_balance: int) -> bool:
        """Update credits in database"""
        # Mock implementation
        self.user_credits[user_id] = new_balance
        return True
    
    def _log_credit_transaction(self, user_id: str, amount: int, transaction_type: str, reason: str):
        """Log credit transaction"""
        transaction = {
            'user_id': user_id,
            'amount': amount,
            'type': transaction_type,
            'reason': reason,
            'timestamp': time.time()
        }
        
        logger.info(f"Credit transaction: {transaction}")
        
        # In production, this would be stored in database
    
    def _process_payment(self, user_id: str, amount: float, payment_info: Dict[str, Any]) -> Dict[str, Any]:
        """Process payment (mock implementation)"""
        # Mock payment processing
        import uuid
        
        # Simulate payment gateway response
        if amount > 0:
            return {
                'status': 'success',
                'transaction_id': str(uuid.uuid4()),
                'amount': amount,
                'user_id': user_id
            }
        else:
            return {
                'status': 'failed',
                'message': 'Invalid amount'
            }
    
    def _process_refund(self, transaction_id: str) -> Dict[str, Any]:
        """Process payment refund (mock implementation)"""
        logger.info(f"Refund processed for transaction {transaction_id}")
        return {'status': 'success', 'refund_id': f"ref_{transaction_id}"}
    
    def _get_credit_history_from_db(self, user_id: str, limit: int) -> list:
        """Get credit history from database"""
        # Mock implementation
        return []
    
    def _has_used_discount(self, user_id: str, discount_code: str) -> bool:
        """Check if user has used discount code"""
        # Mock implementation
        return False
    
    def _mark_discount_used(self, user_id: str, discount_code: str):
        """Mark discount code as used by user"""
        # Mock implementation
        logger.info(f"Discount {discount_code} marked as used by {user_id}")
    
    def get_available_packages(self) -> Dict[str, Dict[str, Any]]:
        """Get available credit packages"""
        return self.credit_packages.copy()
    
    def estimate_action_credits(self, actions: Dict[str, int]) -> Dict[str, Any]:
        """Estimate total credits needed for multiple actions"""
        total_cost = 0
        breakdown = {}
        
        for action_type, quantity in actions.items():
            cost_per_action = self.check_action_cost(action_type)
            action_total = cost_per_action * quantity
            total_cost += action_total
            
            breakdown[action_type] = {
                'quantity': quantity,
                'cost_per_action': cost_per_action,
                'total_cost': action_total
            }
        
        return {
            'total_cost': total_cost,
            'breakdown': breakdown,
            'recommended_package': self._recommend_package(total_cost)
        }
    
    def _recommend_package(self, needed_credits: int) -> str:
        """Recommend appropriate credit package"""
        for package_name, package_info in self.credit_packages.items():
            if package_info['credits'] >= needed_credits:
                return package_name
        
        return 'enterprise'  # Largest package if none sufficient

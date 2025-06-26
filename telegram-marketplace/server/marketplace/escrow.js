import uuid
import time
from typing import Dict, Any, Optional
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)

class TransactionStatus(Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    DISPUTED = "DISPUTED"
    REFUNDED = "REFUNDED"

class EscrowService:
    def __init__(self, database_connection=None):
        self.transactions = {}  # In-memory storage for demo
        self.db = database_connection
        
    def create_transaction(self, buyer: str, seller: str, amount: float, 
                          item_description: str = None) -> str:
        """Create a new escrow transaction"""
        tx_id = str(uuid.uuid4())
        
        transaction = {
            'id': tx_id,
            'buyer': buyer,
            'seller': seller,
            'amount': amount,
            'status': TransactionStatus.PENDING.value,
            'item_description': item_description,
            'created_at': time.time(),
            'updated_at': time.time(),
            'escrow_fee': amount * 0.05,  # 5% escrow fee
            'total_amount': amount * 1.05,
            'buyer_confirmed': False,
            'seller_confirmed': False,
            'completion_deadline': time.time() + (7 * 24 * 3600),  # 7 days
            'dispute_reason': None,
            'refund_reason': None
        }
        
        self.transactions[tx_id] = transaction
        
        if self.db:
            self._store_transaction(transaction)
        
        logger.info(f"Created escrow transaction {tx_id} for ${amount} between {buyer} and {seller}")
        
        return tx_id
    
    def confirm_transaction(self, tx_id: str, user_id: str, role: str) -> Dict[str, Any]:
        """Confirm transaction by buyer or seller"""
        if tx_id not in self.transactions:
            return {'status': 'error', 'message': 'Transaction not found'}
        
        transaction = self.transactions[tx_id]
        
        if transaction['status'] != TransactionStatus.PENDING.value:
            return {'status': 'error', 'message': 'Transaction cannot be confirmed in current status'}
        
        if role == 'buyer' and transaction['buyer'] == user_id:
            transaction['buyer_confirmed'] = True
        elif role == 'seller' and transaction['seller'] == user_id:
            transaction['seller_confirmed'] = True
        else:
            return {'status': 'error', 'message': 'Unauthorized confirmation'}
        
        # Check if both parties have confirmed
        if transaction['buyer_confirmed'] and transaction['seller_confirmed']:
            transaction['status'] = TransactionStatus.CONFIRMED.value
            transaction['updated_at'] = time.time()
            
            # Start delivery process
            self._initiate_delivery(tx_id)
        
        if self.db:
            self._update_transaction(transaction)
        
        return {
            'status': 'success',
            'transaction_id': tx_id,
            'current_status': transaction['status']
        }
    
    def complete_transaction(self, tx_id: str, user_id: str) -> Dict[str, Any]:
        """Mark transaction as completed (usually by buyer)"""
        if tx_id not in self.transactions:
            return {'status': 'error', 'message': 'Transaction not found'}
        
        transaction = self.transactions[tx_id]
        
        if transaction['buyer'] != user_id:
            return {'status': 'error', 'message': 'Only buyer can complete transaction'}
        
        if transaction['status'] != TransactionStatus.CONFIRMED.value:
            return {'status': 'error', 'message': 'Transaction must be confirmed before completion'}
        
        # Complete the transaction
        transaction['status'] = TransactionStatus.COMPLETED.value
        transaction['completed_at'] = time.time()
        transaction['updated_at'] = time.time()
        
        # Release funds to seller
        self._release_funds(transaction)
        
        if self.db:
            self._update_transaction(transaction)
        
        logger.info(f"Transaction {tx_id} completed successfully")
        
        return {
            'status': 'success',
            'transaction_id': tx_id,
            'message': 'Transaction completed, funds released to seller'
        }
    
    def dispute_transaction(self, tx_id: str, user_id: str, reason: str) -> Dict[str, Any]:
        """Raise a dispute for a transaction"""
        if tx_id not in self.transactions:
            return {'status': 'error', 'message': 'Transaction not found'}
        
        transaction = self.transactions[tx_id]
        
        if user_id not in [transaction['buyer'], transaction['seller']]:
            return {'status': 'error', 'message': 'Unauthorized dispute'}
        
        if transaction['status'] in [TransactionStatus.COMPLETED.value, TransactionStatus.REFUNDED.value]:
            return {'status': 'error', 'message': 'Cannot dispute completed or refunded transaction'}
        
        transaction['status'] = TransactionStatus.DISPUTED.value
        transaction['dispute_reason'] = reason
        transaction['disputed_by'] = user_id
        transaction['disputed_at'] = time.time()
        transaction['updated_at'] = time.time()
        
        # Freeze funds until dispute resolution
        self._freeze_funds(transaction)
        
        if self.db:
            self._update_transaction(transaction)
        
        logger.warning(f"Transaction {tx_id} disputed by {user_id}: {reason}")
        
        return {
            'status': 'success',
            'transaction_id': tx_id,
            'message': 'Dispute raised, funds frozen until resolution'
        }
    
    def cancel_transaction(self, tx_id: str, user_id: str, reason: str = None) -> Dict[str, Any]:
        """Cancel a pending transaction"""
        if tx_id not in self.transactions:
            return {'status': 'error', 'message': 'Transaction not found'}
        
        transaction = self.transactions[tx_id]
        
        if user_id not in [transaction['buyer'], transaction['seller']]:
            return {'status': 'error', 'message': 'Unauthorized cancellation'}
        
        if transaction['status'] != TransactionStatus.PENDING.value:
            return {'status': 'error', 'message': 'Only pending transactions can be cancelled'}
        
        transaction['status'] = TransactionStatus.CANCELLED.value
        transaction['cancelled_by'] = user_id
        transaction['cancel_reason'] = reason
        transaction['cancelled_at'] = time.time()
        transaction['updated_at'] = time.time()
        
        # Refund any deposited funds
        self._refund_funds(transaction)
        
        if self.db:
            self._update_transaction(transaction)
        
        logger.info(f"Transaction {tx_id} cancelled by {user_id}")
        
        return {
            'status': 'success',
            'transaction_id': tx_id,
            'message': 'Transaction cancelled and funds refunded'
        }
    
    def get_transaction(self, tx_id: str) -> Optional[Dict[str, Any]]:
        """Get transaction details"""
        return self.transactions.get(tx_id)
    
    def get_user_transactions(self, user_id: str) -> list:
        """Get all transactions for a user"""
        user_transactions = []
        
        for tx in self.transactions.values():
            if tx['buyer'] == user_id or tx['seller'] == user_id:
                user_transactions.append(tx)
        
        return sorted(user_transactions, key=lambda x: x['created_at'], reverse=True)
    
    def _initiate_delivery(self, tx_id: str):
        """Initiate delivery process after confirmation"""
        # This would trigger delivery workflow
        logger.info(f"Delivery initiated for transaction {tx_id}")
    
    def _release_funds(self, transaction: Dict[str, Any]):
        """Release escrowed funds to seller"""
        # This would handle actual fund transfer
        seller = transaction['seller']
        amount = transaction['amount']
        logger.info(f"Released ${amount} to seller {seller}")
    
    def _freeze_funds(self, transaction: Dict[str, Any]):
        """Freeze funds during dispute"""
        # This would freeze the escrowed funds
        logger.info(f"Funds frozen for disputed transaction {transaction['id']}")
    
    def _refund_funds(self, transaction: Dict[str, Any]):
        """Refund funds to buyer"""
        # This would handle refund processing
        buyer = transaction['buyer']
        amount = transaction['total_amount']
        logger.info(f"Refunded ${amount} to buyer {buyer}")
    
    def _store_transaction(self, transaction: Dict[str, Any]):
        """Store transaction in database"""
        # This would insert transaction into database
        pass
    
    def _update_transaction(self, transaction: Dict[str, Any]):
        """Update transaction in database"""
        # This would update transaction in database
        pass
    
    def get_escrow_statistics(self) -> Dict[str, Any]:
        """Get escrow service statistics"""
        total_transactions = len(self.transactions)
        
        if total_transactions == 0:
            return {
                'total_transactions': 0,
                'total_volume': 0,
                'completion_rate': 0,
                'dispute_rate': 0
            }
        
        completed = sum(1 for tx in self.transactions.values() 
                       if tx['status'] == TransactionStatus.COMPLETED.value)
        disputed = sum(1 for tx in self.transactions.values() 
                      if tx['status'] == TransactionStatus.DISPUTED.value)
        total_volume = sum(tx['amount'] for tx in self.transactions.values())
        
        return {
            'total_transactions': total_transactions,
            'total_volume': total_volume,
            'completion_rate': completed / total_transactions,
            'dispute_rate': disputed / total_transactions,
            'average_transaction_value': total_volume / total_transactions
        }

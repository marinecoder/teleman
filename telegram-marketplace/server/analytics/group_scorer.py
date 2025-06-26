import pandas as pd
import numpy as np
from typing import Dict, Any, List
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class GroupScorer:
    def __init__(self, database_connection=None):
        self.db = database_connection
        
    def calculate_group_score(self, group_id: str) -> Dict[str, Any]:
        """Calculate comprehensive group score based on engagement metrics"""
        
        try:
            # Get group data
            group_data = self._get_group_data(group_id)
            
            if not group_data:
                return {'score': 0, 'error': 'Group data not found'}
            
            # Calculate individual metrics
            metrics = {
                'member_activity': self._calculate_member_activity_score(group_data),
                'growth_rate': self._calculate_growth_rate_score(group_data),
                'engagement_quality': self._calculate_engagement_quality_score(group_data),
                'content_quality': self._calculate_content_quality_score(group_data),
                'admin_activity': self._calculate_admin_activity_score(group_data),
                'member_retention': self._calculate_member_retention_score(group_data)
            }
            
            # Weighted scoring
            weights = {
                'member_activity': 0.25,
                'growth_rate': 0.20,
                'engagement_quality': 0.20,
                'content_quality': 0.15,
                'admin_activity': 0.10,
                'member_retention': 0.10
            }
            
            # Calculate final score
            final_score = sum(metrics[metric] * weights[metric] for metric in metrics)
            
            # Normalize to 0-100 scale
            final_score = min(100, max(0, final_score * 100))
            
            result = {
                'group_id': group_id,
                'final_score': round(final_score, 2),
                'metrics': metrics,
                'weights': weights,
                'calculated_at': datetime.now().isoformat()
            }
            
            logger.info(f"Calculated score for group {group_id}: {final_score}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating group score for {group_id}: {str(e)}")
            return {'score': 0, 'error': str(e)}
    
    def _calculate_member_activity_score(self, group_data: Dict[str, Any]) -> float:
        """Calculate member activity score based on message frequency"""
        
        # Get recent message data
        recent_messages = group_data.get('recent_messages', [])
        total_members = group_data.get('member_count', 1)
        
        if not recent_messages or total_members == 0:
            return 0.0
        
        # Calculate daily message rate
        daily_messages = len([msg for msg in recent_messages 
                            if self._is_recent_message(msg, days=1)])
        
        # Calculate active member ratio
        active_members = len(set(msg.get('user_id') for msg in recent_messages 
                               if self._is_recent_message(msg, days=7)))
        
        activity_ratio = active_members / total_members
        message_density = daily_messages / total_members
        
        # Scoring: balance between activity and sustainability
        score = (activity_ratio * 0.7) + (min(message_density, 0.5) * 0.3)
        
        return min(1.0, score)
    
    def _calculate_growth_rate_score(self, group_data: Dict[str, Any]) -> float:
        """Calculate growth rate score"""
        
        member_history = group_data.get('member_history', [])
        
        if len(member_history) < 2:
            return 0.5  # Neutral score for new groups
        
        # Calculate growth over different periods
        growth_7d = self._calculate_period_growth(member_history, 7)
        growth_30d = self._calculate_period_growth(member_history, 30)
        
        # Penalize negative growth, reward sustainable growth
        if growth_7d < 0 or growth_30d < 0:
            return 0.0
        
        # Optimal growth rate: 1-5% per week
        optimal_weekly_growth = 0.03  # 3%
        
        score_7d = 1.0 - abs(growth_7d - optimal_weekly_growth) / optimal_weekly_growth
        score_30d = 1.0 - abs(growth_30d * 7 / 30 - optimal_weekly_growth) / optimal_weekly_growth
        
        return max(0.0, (score_7d * 0.6 + score_30d * 0.4))
    
    def _calculate_engagement_quality_score(self, group_data: Dict[str, Any]) -> float:
        """Calculate engagement quality based on interaction types"""
        
        recent_messages = group_data.get('recent_messages', [])
        
        if not recent_messages:
            return 0.0
        
        # Analyze message types and interactions
        total_messages = len(recent_messages)
        
        # Count different engagement types
        replies = sum(1 for msg in recent_messages if msg.get('reply_to'))
        reactions = sum(msg.get('reaction_count', 0) for msg in recent_messages)
        forwards = sum(1 for msg in recent_messages if msg.get('forward_count', 0) > 0)
        media_messages = sum(1 for msg in recent_messages if msg.get('has_media'))
        
        # Calculate engagement ratios
        reply_ratio = replies / total_messages
        reaction_ratio = reactions / total_messages
        media_ratio = media_messages / total_messages
        
        # Weighted engagement score
        engagement_score = (
            reply_ratio * 0.4 +
            min(reaction_ratio / 2.0, 1.0) * 0.3 +  # Normalize reactions
            media_ratio * 0.2 +
            min(forwards / total_messages, 0.2) * 0.1  # Cap forwards
        )
        
        return min(1.0, engagement_score)
    
    def _calculate_content_quality_score(self, group_data: Dict[str, Any]) -> float:
        """Calculate content quality score"""
        
        recent_messages = group_data.get('recent_messages', [])
        
        if not recent_messages:
            return 0.0
        
        # Analyze content characteristics
        total_messages = len(recent_messages)
        
        # Quality indicators
        spam_messages = sum(1 for msg in recent_messages if self._is_spam_message(msg))
        short_messages = sum(1 for msg in recent_messages if len(msg.get('text', '')) < 10)
        unique_messages = len(set(msg.get('text', '') for msg in recent_messages))
        
        # Calculate quality metrics
        spam_ratio = spam_messages / total_messages
        diversity_ratio = unique_messages / total_messages
        substantive_ratio = 1 - (short_messages / total_messages)
        
        # Quality score (higher is better)
        quality_score = (
            (1 - spam_ratio) * 0.4 +
            diversity_ratio * 0.3 +
            substantive_ratio * 0.3
        )
        
        return max(0.0, quality_score)
    
    def _calculate_admin_activity_score(self, group_data: Dict[str, Any]) -> float:
        """Calculate admin activity and moderation score"""
        
        admin_actions = group_data.get('admin_actions', [])
        recent_messages = group_data.get('recent_messages', [])
        
        if not admin_actions and not recent_messages:
            return 0.5  # Neutral for new groups
        
        # Recent admin activity
        recent_admin_actions = [action for action in admin_actions 
                               if self._is_recent_action(action, days=7)]
        
        # Admin message activity
        admin_messages = [msg for msg in recent_messages 
                         if msg.get('is_admin', False)]
        
        # Score based on appropriate admin presence
        admin_action_frequency = len(recent_admin_actions) / 7  # Actions per day
        admin_message_ratio = len(admin_messages) / len(recent_messages) if recent_messages else 0
        
        # Optimal: Some admin activity but not overwhelming
        action_score = min(1.0, admin_action_frequency / 2.0)  # 2 actions per day is optimal
        message_score = 1.0 - abs(admin_message_ratio - 0.1) / 0.1  # 10% admin messages is optimal
        
        return max(0.0, (action_score * 0.6 + message_score * 0.4))
    
    def _calculate_member_retention_score(self, group_data: Dict[str, Any]) -> float:
        """Calculate member retention score"""
        
        member_activity = group_data.get('member_activity_history', {})
        
        if not member_activity:
            return 0.5  # Neutral for groups without history
        
        # Calculate retention over different periods
        current_active = set(member_activity.get('current_week', []))
        prev_week_active = set(member_activity.get('previous_week', []))
        prev_month_active = set(member_activity.get('previous_month', []))
        
        if not prev_week_active:
            return 0.5
        
        # Week-over-week retention
        weekly_retention = len(current_active.intersection(prev_week_active)) / len(prev_week_active)
        
        # Month-over-month retention (if available)
        monthly_retention = 0.5
        if prev_month_active:
            monthly_retention = len(current_active.intersection(prev_month_active)) / len(prev_month_active)
        
        # Combined retention score
        retention_score = weekly_retention * 0.7 + monthly_retention * 0.3
        
        return min(1.0, retention_score)
    
    def _get_group_data(self, group_id: str) -> Dict[str, Any]:
        """Get group data from database or cache"""
        
        # Mock data for demonstration
        # In production, this would fetch from database
        return {
            'group_id': group_id,
            'member_count': 1500,
            'recent_messages': self._generate_mock_messages(100),
            'member_history': self._generate_mock_member_history(),
            'admin_actions': self._generate_mock_admin_actions(),
            'member_activity_history': self._generate_mock_activity_history()
        }
    
    def _generate_mock_messages(self, count: int) -> List[Dict[str, Any]]:
        """Generate mock messages for testing"""
        messages = []
        base_time = datetime.now() - timedelta(days=7)
        
        for i in range(count):
            message = {
                'id': f"msg_{i}",
                'user_id': f"user_{np.random.randint(1, 100)}",
                'text': f"Sample message {i}",
                'timestamp': base_time + timedelta(hours=np.random.randint(0, 168)),
                'reply_to': f"msg_{i-1}" if np.random.random() < 0.3 and i > 0 else None,
                'reaction_count': np.random.randint(0, 10),
                'has_media': np.random.random() < 0.2,
                'is_admin': np.random.random() < 0.1
            }
            messages.append(message)
        
        return messages
    
    def _generate_mock_member_history(self) -> List[Dict[str, Any]]:
        """Generate mock member history"""
        history = []
        base_count = 1000
        
        for days_ago in range(30, 0, -1):
            growth = np.random.normal(0.02, 0.01)  # 2% average growth with variation
            base_count = int(base_count * (1 + growth))
            
            history.append({
                'date': (datetime.now() - timedelta(days=days_ago)).date().isoformat(),
                'member_count': base_count
            })
        
        return history
    
    def _generate_mock_admin_actions(self) -> List[Dict[str, Any]]:
        """Generate mock admin actions"""
        actions = []
        base_time = datetime.now() - timedelta(days=7)
        
        for i in range(np.random.randint(5, 20)):
            action = {
                'id': f"action_{i}",
                'type': np.random.choice(['delete_message', 'ban_user', 'pin_message', 'edit_description']),
                'timestamp': base_time + timedelta(hours=np.random.randint(0, 168)),
                'admin_id': f"admin_{np.random.randint(1, 5)}"
            }
            actions.append(action)
        
        return actions
    
    def _generate_mock_activity_history(self) -> Dict[str, List[str]]:
        """Generate mock activity history"""
        return {
            'current_week': [f"user_{i}" for i in range(1, 101)],
            'previous_week': [f"user_{i}" for i in range(1, 96)],
            'previous_month': [f"user_{i}" for i in range(1, 91)]
        }
    
    def _is_recent_message(self, message: Dict[str, Any], days: int) -> bool:
        """Check if message is within recent time period"""
        if 'timestamp' not in message:
            return False
        
        msg_time = message['timestamp']
        if isinstance(msg_time, str):
            msg_time = datetime.fromisoformat(msg_time.replace('Z', '+00:00'))
        
        cutoff = datetime.now() - timedelta(days=days)
        return msg_time > cutoff
    
    def _is_recent_action(self, action: Dict[str, Any], days: int) -> bool:
        """Check if admin action is within recent time period"""
        if 'timestamp' not in action:
            return False
        
        action_time = action['timestamp']
        if isinstance(action_time, str):
            action_time = datetime.fromisoformat(action_time.replace('Z', '+00:00'))
        
        cutoff = datetime.now() - timedelta(days=days)
        return action_time > cutoff
    
    def _is_spam_message(self, message: Dict[str, Any]) -> bool:
        """Simple spam detection"""
        text = message.get('text', '').lower()
        
        spam_indicators = [
            'buy now', 'click here', 'free money', 'urgent',
            'http://', 'https://', '@everyone', 'crypto'
        ]
        
        return any(indicator in text for indicator in spam_indicators)
    
    def _calculate_period_growth(self, history: List[Dict[str, Any]], days: int) -> float:
        """Calculate growth rate over specified period"""
        if len(history) < 2:
            return 0.0
        
        # Sort by date
        sorted_history = sorted(history, key=lambda x: x['date'])
        
        if len(sorted_history) < days:
            # Use available data
            start_count = sorted_history[0]['member_count']
            end_count = sorted_history[-1]['member_count']
            actual_days = len(sorted_history)
        else:
            # Use exact period
            start_count = sorted_history[-days]['member_count']
            end_count = sorted_history[-1]['member_count']
            actual_days = days
        
        if start_count == 0:
            return 0.0
        
        # Calculate daily growth rate
        growth_rate = (end_count - start_count) / start_count / actual_days
        
        return growth_rate

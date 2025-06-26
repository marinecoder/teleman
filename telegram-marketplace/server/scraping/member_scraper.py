from telethon import TelegramClient
from typing import List, Dict, Any, Optional
import asyncio
import logging

logger = logging.getLogger(__name__)

class MemberScraper:
    def __init__(self, client: TelegramClient):
        self.client = client
    
    async def scrape_members(self, source: str, limit: int = 500) -> List[Dict[str, Any]]:
        """Scrape members from a Telegram group or channel"""
        try:
            members = []
            entity = await self.client.get_entity(source)
            
            async for user in self.client.iter_participants(entity, limit=limit):
                if user.username and not user.bot:
                    member_data = {
                        'id': user.id,
                        'username': user.username,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'phone': user.phone,
                        'is_premium': getattr(user, 'premium', False),
                        'status': str(user.status) if user.status else None
                    }
                    members.append(member_data)
                
                # Rate limiting
                await asyncio.sleep(0.1)
            
            logger.info(f"Scraped {len(members)} members from {source}")
            return members
            
        except Exception as e:
            logger.error(f"Error scraping members from {source}: {str(e)}")
            raise e
    
    async def scrape_members_with_filters(self, source: str, filters: Dict[str, Any], limit: int = 500) -> List[Dict[str, Any]]:
        """Scrape members with advanced filters"""
        try:
            members = []
            entity = await self.client.get_entity(source)
            
            async for user in self.client.iter_participants(entity, limit=limit):
                if user.username and not user.bot:
                    # Apply filters
                    if self._passes_filters(user, filters):
                        member_data = {
                            'id': user.id,
                            'username': user.username,
                            'first_name': user.first_name,
                            'last_name': user.last_name,
                            'phone': user.phone,
                            'is_premium': getattr(user, 'premium', False),
                            'status': str(user.status) if user.status else None,
                            'last_seen': self._get_last_seen(user.status)
                        }
                        members.append(member_data)
                
                await asyncio.sleep(0.1)
            
            return members
            
        except Exception as e:
            logger.error(f"Error scraping filtered members: {str(e)}")
            raise e
    
    def _passes_filters(self, user, filters: Dict[str, Any]) -> bool:
        """Check if user passes the specified filters"""
        if filters.get('premium_only') and not getattr(user, 'premium', False):
            return False
        
        if filters.get('has_username') and not user.username:
            return False
        
        if filters.get('online_only'):
            from telethon.tl.types import UserStatusOnline, UserStatusRecently
            if not isinstance(user.status, (UserStatusOnline, UserStatusRecently)):
                return False
        
        return True
    
    def _get_last_seen(self, status) -> Optional[str]:
        """Extract last seen information from user status"""
        if not status:
            return None
        
        from telethon.tl.types import (
            UserStatusOnline, UserStatusOffline, 
            UserStatusRecently, UserStatusLastWeek, 
            UserStatusLastMonth
        )
        
        if isinstance(status, UserStatusOnline):
            return "online"
        elif isinstance(status, UserStatusRecently):
            return "recently"
        elif isinstance(status, UserStatusLastWeek):
            return "last_week"
        elif isinstance(status, UserStatusLastMonth):
            return "last_month"
        elif isinstance(status, UserStatusOffline):
            return "offline"
        
        return "unknown"

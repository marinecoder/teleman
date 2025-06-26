from telethon import TelegramClient
from telethon.errors import PhoneCodeInvalidError, PhoneNumberInvalidError, SessionPasswordNeededError
import os
import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class AuthManager:
    def __init__(self, session_path: str, api_id: int, api_hash: str):
        self.session_path = session_path
        self.api_id = api_id
        self.api_hash = api_hash
        self.client = None
    
    async def initialize_client(self):
        """Initialize Telegram client"""
        self.client = TelegramClient(self.session_path, self.api_id, self.api_hash)
        await self.client.connect()
        return self.client
    
    async def login(self, phone: str, code: Optional[str] = None, password: Optional[str] = None):
        """Login to Telegram with phone number, code, and optional 2FA password"""
        try:
            if not self.client:
                await self.initialize_client()
            
            if not await self.client.is_user_authorized():
                # Send code request
                await self.client.send_code_request(phone)
                
                if code:
                    try:
                        await self.client.sign_in(phone, code)
                    except SessionPasswordNeededError:
                        if password:
                            await self.client.sign_in(password=password)
                        else:
                            raise Exception("2FA password required")
                    
                    logger.info(f"Successfully authenticated {phone}")
                    return {"status": "success", "message": "Authentication successful"}
                else:
                    return {"status": "code_required", "message": "Code sent to phone"}
            else:
                return {"status": "already_authenticated", "message": "Already logged in"}
                
        except PhoneCodeInvalidError:
            return {"status": "error", "message": "Invalid code"}
        except PhoneNumberInvalidError:
            return {"status": "error", "message": "Invalid phone number"}
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def logout(self):
        """Logout and disconnect client"""
        if self.client:
            await self.client.log_out()
            await self.client.disconnect()
    
    async def is_authenticated(self) -> bool:
        """Check if client is authenticated"""
        if not self.client:
            return False
        return await self.client.is_user_authorized()
    
    async def get_me(self):
        """Get current user info"""
        if self.client and await self.is_authenticated():
            return await self.client.get_me()
        return None

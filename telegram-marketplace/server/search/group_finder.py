from telethon import functions, types
import logging

logger = logging.getLogger(__name__)

class GroupFinder:
    def __init__(self, client):
        self.client = client
    
    async def search_entities(self, query: str, entity_type: str = 'group', limit: int = 100):
        """Search for groups, channels, or users"""
        try:
            if entity_type == 'group':
                filter_type = types.InputMessagesFilterChatPhotos()
            elif entity_type == 'channel':
                filter_type = types.InputMessagesFilterChatPhotos()
            else:
                filter_type = None
            
            result = await self.client(functions.contacts.SearchRequest(
                q=query,
                limit=limit
            ))
            
            entities = []
            for entity in result.chats + result.users:
                if hasattr(entity, 'title') or hasattr(entity, 'username'):
                    entity_data = {
                        'id': entity.id,
                        'title': getattr(entity, 'title', None),
                        'username': getattr(entity, 'username', None),
                        'type': 'channel' if hasattr(entity, 'broadcast') else 'group',
                        'participants_count': getattr(entity, 'participants_count', 0),
                        'access_hash': getattr(entity, 'access_hash', None)
                    }
                    entities.append(entity_data)
            
            logger.info(f"Found {len(entities)} entities for query: {query}")
            return entities
            
        except Exception as e:
            logger.error(f"Error searching entities: {str(e)}")
            raise e
    
    async def search_global(self, query: str, limit: int = 50):
        """Search for public groups and channels globally"""
        try:
            result = await self.client(functions.contacts.SearchRequest(
                q=query,
                limit=limit
            ))
            
            entities = []
            for entity in result.chats:
                if hasattr(entity, 'username') and entity.username:  # Only public entities
                    entity_data = {
                        'id': entity.id,
                        'title': entity.title,
                        'username': entity.username,
                        'type': 'channel' if hasattr(entity, 'broadcast') else 'group',
                        'participants_count': getattr(entity, 'participants_count', 0),
                        'verified': getattr(entity, 'verified', False),
                        'scam': getattr(entity, 'scam', False)
                    }
                    entities.append(entity_data)
            
            return entities
            
        except Exception as e:
            logger.error(f"Error in global search: {str(e)}")
            raise e
    
    async def get_entity_info(self, entity_input):
        """Get detailed information about a specific entity"""
        try:
            entity = await self.client.get_entity(entity_input)
            
            info = {
                'id': entity.id,
                'title': getattr(entity, 'title', None),
                'username': getattr(entity, 'username', None),
                'about': getattr(entity, 'about', None),
                'participants_count': getattr(entity, 'participants_count', 0),
                'type': 'channel' if hasattr(entity, 'broadcast') else 'group',
                'verified': getattr(entity, 'verified', False),
                'restricted': getattr(entity, 'restricted', False),
                'scam': getattr(entity, 'scam', False)
            }
            
            # Get additional stats if possible
            try:
                full_entity = await self.client(functions.channels.GetFullChannelRequest(entity))
                info['full_info'] = {
                    'online_count': getattr(full_entity.full_chat, 'online_count', 0),
                    'can_view_participants': getattr(full_entity.full_chat, 'can_view_participants', False),
                    'can_set_username': getattr(full_entity.full_chat, 'can_set_username', False)
                }
            except:
                pass
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting entity info: {str(e)}")
            raise e

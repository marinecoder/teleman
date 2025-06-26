import random
import uuid
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class AntiDetectSystem:
    def __init__(self):
        self.device_models = [
            'iPhone 13', 'iPhone 14', 'iPhone 15',
            'Samsung Galaxy S21', 'Samsung Galaxy S22', 'Samsung Galaxy S23',
            'Google Pixel 6', 'Google Pixel 7', 'Google Pixel 8',
            'OnePlus 9', 'OnePlus 10', 'OnePlus 11',
            'Xiaomi Mi 11', 'Xiaomi Mi 12', 'Xiaomi Mi 13'
        ]
        
        self.app_versions = [
            '8.4.1', '8.4.2', '8.4.3',
            '9.1.0', '9.1.1', '9.1.2',
            '9.3.0', '9.3.1', '9.3.2',
            '9.4.0', '9.4.1'
        ]
        
        self.operating_systems = [
            'iOS 15.0', 'iOS 15.1', 'iOS 16.0', 'iOS 16.1', 'iOS 17.0',
            'Android 11', 'Android 12', 'Android 13', 'Android 14'
        ]
        
        self.languages = [
            'en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ko'
        ]
    
    def randomize_fingerprint(self) -> Dict[str, Any]:
        """Generate randomized device fingerprint"""
        device_model = random.choice(self.device_models)
        is_ios = 'iPhone' in device_model
        
        fingerprint = {
            'device_model': device_model,
            'app_version': random.choice(self.app_versions),
            'os_version': random.choice([os for os in self.operating_systems 
                                       if ('iOS' in os) == is_ios]),
            'language': random.choice(self.languages),
            'timezone': random.choice([
                'UTC', 'America/New_York', 'Europe/London', 'Asia/Tokyo',
                'Australia/Sydney', 'America/Los_Angeles', 'Europe/Berlin'
            ]),
            'device_id': str(uuid.uuid4()),
            'session_id': str(uuid.uuid4())
        }
        
        return fingerprint
    
    def generate_user_agent(self, fingerprint: Dict[str, Any]) -> str:
        """Generate realistic user agent string"""
        device = fingerprint['device_model']
        os_version = fingerprint['os_version']
        app_version = fingerprint['app_version']
        
        if 'iPhone' in device:
            return f"Telegram/{app_version} (iPhone; {os_version}; Scale/2.00)"
        else:
            return f"Telegram/{app_version} (Android {os_version.split()[-1]}; {device})"
    
    def get_random_activity_pattern(self) -> Dict[str, Any]:
        """Generate random but realistic activity pattern"""
        return {
            'daily_messages': random.randint(10, 200),
            'daily_groups_joined': random.randint(0, 5),
            'daily_searches': random.randint(1, 20),
            'online_hours': random.uniform(2.0, 16.0),
            'peak_activity_hour': random.randint(8, 23),
            'weekend_activity_factor': random.uniform(0.5, 1.5)
        }
    
    def get_random_network_timing(self) -> Dict[str, float]:
        """Generate realistic network timing parameters"""
        return {
            'connection_delay': random.uniform(0.1, 2.0),
            'request_interval': random.uniform(1.0, 5.0),
            'retry_delay': random.uniform(2.0, 10.0),
            'timeout': random.uniform(15.0, 45.0)
        }
    
    def randomize_message_style(self) -> Dict[str, Any]:
        """Generate randomized message style parameters"""
        return {
            'typing_speed': random.uniform(30, 80),  # WPM
            'uses_emoji': random.choice([True, False]),
            'emoji_frequency': random.uniform(0.1, 0.3),
            'uses_abbreviations': random.choice([True, False]),
            'message_length_preference': random.choice(['short', 'medium', 'long']),
            'punctuation_style': random.choice(['minimal', 'normal', 'excessive'])
        }
    
    def get_proxy_rotation_schedule(self) -> List[Dict[str, Any]]:
        """Generate proxy rotation schedule"""
        schedule = []
        
        # Change proxy every 30-120 minutes
        for i in range(24):  # 24 hours
            schedule.append({
                'hour': i,
                'change_probability': random.uniform(0.1, 0.8),
                'min_actions_before_change': random.randint(10, 100),
                'max_actions_before_change': random.randint(100, 500)
            })
        
        return schedule
    
    def generate_session_parameters(self) -> Dict[str, Any]:
        """Generate session-specific parameters"""
        return {
            'max_session_duration': random.uniform(1800, 7200),  # 30min to 2h
            'max_actions_per_session': random.randint(50, 300),
            'cooldown_between_sessions': random.uniform(300, 1800),  # 5min to 30min
            'session_activity_pattern': random.choice([
                'burst', 'steady', 'random', 'declining'
            ])
        }
    
    def should_trigger_anti_detection(self, action_count: int, session_duration: float) -> bool:
        """Determine if anti-detection measures should be triggered"""
        # Trigger if too many actions in short time
        if action_count > 100 and session_duration < 600:  # 100 actions in 10 minutes
            return True
        
        # Random trigger for unpredictability
        if random.random() < 0.05:  # 5% random chance
            return True
        
        return False
    
    def get_evasion_action(self) -> Dict[str, Any]:
        """Get random evasion action"""
        actions = [
            {'type': 'pause', 'duration': random.uniform(60, 300)},
            {'type': 'change_proxy', 'immediate': True},
            {'type': 'reduce_activity', 'factor': random.uniform(0.3, 0.7)},
            {'type': 'switch_account', 'delay': random.uniform(30, 120)},
            {'type': 'simulate_human_behavior', 'actions': random.randint(3, 8)}
        ]
        
        return random.choice(actions)

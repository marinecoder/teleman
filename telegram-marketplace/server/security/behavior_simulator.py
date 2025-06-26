import random
import asyncio
import time
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class BehaviorSimulator:
    def __init__(self):
        self.typing_delays = (1.0, 2.5)
        self.scroll_delays = (0.2, 1.8)
        self.click_delays = (0.5, 1.2)
        self.read_delays = (2.0, 5.0)
    
    def simulate_human(self) -> List[Dict[str, Any]]:
        """Generate human-like behavior actions"""
        actions = [
            {'action': 'typing', 'delay': random.uniform(*self.typing_delays)},
            {'action': 'scroll', 'delay': random.uniform(*self.scroll_delays)},
            {'action': 'click', 'delay': random.uniform(*self.click_delays)},
            {'action': 'read', 'delay': random.uniform(*self.read_delays)}
        ]
        
        # Randomize order
        random.shuffle(actions)
        
        # Sometimes add pauses
        if random.random() < 0.3:
            actions.append({'action': 'pause', 'delay': random.uniform(1.0, 3.0)})
        
        return actions
    
    async def execute_human_delay(self, action_type: str = 'general'):
        """Execute a human-like delay based on action type"""
        delays = {
            'typing': self.typing_delays,
            'scroll': self.scroll_delays,
            'click': self.click_delays,
            'read': self.read_delays,
            'general': (0.5, 2.0)
        }
        
        delay_range = delays.get(action_type, delays['general'])
        delay = random.uniform(*delay_range)
        
        logger.debug(f"Human delay ({action_type}): {delay:.2f}s")
        await asyncio.sleep(delay)
    
    def get_random_message_delay(self) -> float:
        """Get random delay for sending messages"""
        # Simulate human typing speed (30-60 WPM)
        base_delay = random.uniform(1.0, 2.0)
        
        # Add random variation
        variation = random.uniform(0.5, 1.5)
        
        return base_delay * variation
    
    def get_random_action_interval(self) -> float:
        """Get random interval between actions"""
        # Most actions happen quickly, but sometimes there are longer pauses
        if random.random() < 0.1:  # 10% chance of long pause
            return random.uniform(30.0, 120.0)  # 30s to 2min
        elif random.random() < 0.3:  # 30% chance of medium pause
            return random.uniform(5.0, 30.0)    # 5s to 30s
        else:  # 60% chance of short pause
            return random.uniform(0.5, 5.0)     # 0.5s to 5s
    
    def simulate_user_activity_pattern(self) -> List[Dict[str, Any]]:
        """Simulate realistic user activity pattern"""
        current_time = time.time()
        activities = []
        
        # Simulate activity over a period
        for i in range(random.randint(3, 8)):
            activity_type = random.choice([
                'view_profile', 'send_message', 'join_group', 
                'leave_group', 'search', 'scroll_chat'
            ])
            
            activity = {
                'type': activity_type,
                'timestamp': current_time + (i * self.get_random_action_interval()),
                'duration': random.uniform(1.0, 10.0)
            }
            
            activities.append(activity)
        
        return activities
    
    def get_realistic_batch_timing(self, batch_size: int) -> List[float]:
        """Get realistic timing for batch operations"""
        timings = []
        
        for i in range(batch_size):
            if i == 0:
                # First action can be immediate
                timings.append(0)
            else:
                # Subsequent actions have human-like delays
                base_delay = random.uniform(1.0, 3.0)
                
                # Add some longer pauses occasionally
                if random.random() < 0.1:
                    base_delay += random.uniform(10.0, 30.0)
                
                timings.append(base_delay)
        
        return timings
    
    def simulate_reading_time(self, content_length: int) -> float:
        """Simulate time needed to read content"""
        # Average reading speed: 200-300 words per minute
        words_per_char = 1/5  # Rough estimate
        words = content_length * words_per_char
        
        # Reading speed in words per second
        reading_speed = random.uniform(3.0, 5.0)  # 180-300 WPM
        
        base_time = words / reading_speed
        
        # Add some variation
        variation = random.uniform(0.5, 1.5)
        
        return max(1.0, base_time * variation)  # Minimum 1 second

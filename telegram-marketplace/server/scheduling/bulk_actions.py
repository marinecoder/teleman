import asyncio
from datetime import datetime, timedelta
import pytz
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class BulkActionScheduler:
    def __init__(self, account_rotator=None):
        self.account_rotator = account_rotator
        self.scheduled_tasks = []
        self.running_tasks = {}
        
    def schedule_add_members(self, group: str, users: List[str], 
                           accounts_per_hour: int = 200, timezone: str = 'UTC') -> str:
        """Schedule bulk member addition with timezone-aware distribution"""
        
        # Calculate distribution
        total_users = len(users)
        accounts_needed = min(len(users), self.account_rotator.get_account_stats()['live_accounts'])
        
        # Distribute users across accounts and time
        distribution = self._calculate_distribution(
            total_users, accounts_needed, accounts_per_hour, timezone
        )
        
        task_id = f"add_members_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        task = {
            'id': task_id,
            'type': 'ADD_MEMBERS',
            'group': group,
            'users': users,
            'distribution': distribution,
            'timezone': timezone,
            'created_at': datetime.now(),
            'status': 'SCHEDULED',
            'progress': 0,
            'total_actions': total_users
        }
        
        self.scheduled_tasks.append(task)
        logger.info(f"Scheduled bulk add members task {task_id} for {total_users} users")
        
        return task_id
    
    def schedule_bulk_scrape(self, sources: List[str], accounts_per_hour: int = 100,
                           timezone: str = 'UTC') -> str:
        """Schedule bulk scraping across multiple sources"""
        
        distribution = self._calculate_scrape_distribution(
            sources, accounts_per_hour, timezone
        )
        
        task_id = f"bulk_scrape_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        task = {
            'id': task_id,
            'type': 'BULK_SCRAPE',
            'sources': sources,
            'distribution': distribution,
            'timezone': timezone,
            'created_at': datetime.now(),
            'status': 'SCHEDULED',
            'progress': 0,
            'total_actions': len(sources)
        }
        
        self.scheduled_tasks.append(task)
        logger.info(f"Scheduled bulk scrape task {task_id} for {len(sources)} sources")
        
        return task_id
    
    def _calculate_distribution(self, total_users: int, accounts_count: int, 
                              accounts_per_hour: int, timezone: str) -> List[Dict[str, Any]]:
        """Calculate timezone-aware distribution logic"""
        
        tz = pytz.timezone(timezone)
        current_time = datetime.now(tz)
        
        # Calculate optimal timing based on timezone
        peak_hours = self._get_peak_hours(timezone)
        
        distribution = []
        users_per_account = total_users // accounts_count
        remaining_users = total_users % accounts_count
        
        actions_per_hour_per_account = accounts_per_hour // accounts_count
        
        start_time = current_time
        
        for i in range(accounts_count):
            # Calculate users for this account
            account_users = users_per_account + (1 if i < remaining_users else 0)
            
            # Calculate timing slots
            hours_needed = account_users / actions_per_hour_per_account
            
            # Distribute across optimal hours
            account_distribution = {
                'account_index': i,
                'users_count': account_users,
                'start_time': start_time + timedelta(minutes=i * 10),  # Stagger starts
                'hours_needed': hours_needed,
                'actions_per_hour': actions_per_hour_per_account,
                'time_slots': self._generate_time_slots(
                    start_time + timedelta(minutes=i * 10),
                    hours_needed,
                    actions_per_hour_per_account,
                    peak_hours
                )
            }
            
            distribution.append(account_distribution)
        
        return distribution
    
    def _calculate_scrape_distribution(self, sources: List[str], 
                                     accounts_per_hour: int, timezone: str) -> List[Dict[str, Any]]:
        """Calculate distribution for scraping tasks"""
        
        tz = pytz.timezone(timezone)
        current_time = datetime.now(tz)
        
        distribution = []
        sources_per_batch = max(1, len(sources) // accounts_per_hour)
        
        for i in range(0, len(sources), sources_per_batch):
            batch_sources = sources[i:i + sources_per_batch]
            
            batch_distribution = {
                'batch_index': i // sources_per_batch,
                'sources': batch_sources,
                'start_time': current_time + timedelta(minutes=i),
                'estimated_duration': len(batch_sources) * 2  # 2 minutes per source
            }
            
            distribution.append(batch_distribution)
        
        return distribution
    
    def _get_peak_hours(self, timezone: str) -> List[int]:
        """Get peak activity hours for timezone"""
        # This would ideally be based on regional data
        timezone_peaks = {
            'UTC': [9, 10, 11, 14, 15, 16, 19, 20],
            'America/New_York': [9, 10, 11, 13, 14, 15, 18, 19, 20],
            'Europe/London': [8, 9, 10, 12, 13, 14, 17, 18, 19],
            'Asia/Tokyo': [7, 8, 9, 11, 12, 13, 16, 17, 18],
            'Australia/Sydney': [7, 8, 9, 11, 12, 13, 16, 17, 18]
        }
        
        return timezone_peaks.get(timezone, timezone_peaks['UTC'])
    
    def _generate_time_slots(self, start_time: datetime, hours_needed: float,
                           actions_per_hour: int, peak_hours: List[int]) -> List[Dict[str, Any]]:
        """Generate optimal time slots for actions"""
        
        time_slots = []
        current_time = start_time
        remaining_hours = hours_needed
        
        while remaining_hours > 0:
            slot_duration = min(1.0, remaining_hours)  # Max 1 hour slots
            
            # Adjust actions based on whether it's peak time
            hour = current_time.hour
            if hour in peak_hours:
                slot_actions = int(actions_per_hour * 1.2)  # 20% more during peak
            else:
                slot_actions = int(actions_per_hour * 0.8)  # 20% less during off-peak
            
            time_slot = {
                'start_time': current_time,
                'duration_hours': slot_duration,
                'target_actions': min(slot_actions, int(remaining_hours * actions_per_hour)),
                'is_peak_time': hour in peak_hours
            }
            
            time_slots.append(time_slot)
            
            current_time += timedelta(hours=1)
            remaining_hours -= slot_duration
        
        return time_slots
    
    async def execute_scheduled_task(self, task_id: str):
        """Execute a scheduled task"""
        task = self._get_task(task_id)
        if not task:
            logger.error(f"Task {task_id} not found")
            return
        
        if task['status'] != 'SCHEDULED':
            logger.warning(f"Task {task_id} is not in SCHEDULED status")
            return
        
        task['status'] = 'RUNNING'
        task['started_at'] = datetime.now()
        self.running_tasks[task_id] = task
        
        try:
            if task['type'] == 'ADD_MEMBERS':
                await self._execute_add_members_task(task)
            elif task['type'] == 'BULK_SCRAPE':
                await self._execute_bulk_scrape_task(task)
            
            task['status'] = 'COMPLETED'
            task['completed_at'] = datetime.now()
            
        except Exception as e:
            logger.error(f"Error executing task {task_id}: {str(e)}")
            task['status'] = 'FAILED'
            task['error'] = str(e)
        
        finally:
            self.running_tasks.pop(task_id, None)
    
    async def _execute_add_members_task(self, task: Dict[str, Any]):
        """Execute bulk add members task"""
        distribution = task['distribution']
        
        for account_dist in distribution:
            # Get account for this distribution
            account = self.account_rotator.get_best_account()
            
            if not account:
                logger.warning("No available accounts for task execution")
                continue
            
            # Execute time slots for this account
            for time_slot in account_dist['time_slots']:
                # Wait until slot start time
                slot_start = time_slot['start_time']
                now = datetime.now(slot_start.tzinfo)
                
                if slot_start > now:
                    wait_seconds = (slot_start - now).total_seconds()
                    await asyncio.sleep(wait_seconds)
                
                # Execute actions for this time slot
                target_actions = time_slot['target_actions']
                
                for action_num in range(target_actions):
                    try:
                        # This would be actual member addition logic
                        await self._add_single_member(account, task['group'], task['users'][action_num])
                        
                        task['progress'] += 1
                        
                        # Delay between actions
                        await asyncio.sleep(3600 / time_slot['target_actions'])  # Spread evenly over hour
                        
                    except Exception as e:
                        logger.error(f"Error adding member: {str(e)}")
    
    async def _execute_bulk_scrape_task(self, task: Dict[str, Any]):
        """Execute bulk scrape task"""
        distribution = task['distribution']
        
        for batch in distribution:
            # Wait until batch start time
            batch_start = batch['start_time']
            now = datetime.now(batch_start.tzinfo)
            
            if batch_start > now:
                wait_seconds = (batch_start - now).total_seconds()
                await asyncio.sleep(wait_seconds)
            
            # Process sources in this batch
            for source in batch['sources']:
                try:
                    account = self.account_rotator.get_best_account()
                    if account:
                        # This would be actual scraping logic
                        await self._scrape_single_source(account, source)
                        task['progress'] += 1
                        
                        # Delay between sources
                        await asyncio.sleep(120)  # 2 minutes
                
                except Exception as e:
                    logger.error(f"Error scraping source {source}: {str(e)}")
    
    async def _add_single_member(self, account: Dict[str, Any], group: str, user: str):
        """Add single member (mock implementation)"""
        logger.debug(f"Adding user {user} to group {group} using account {account['phone']}")
        await asyncio.sleep(0.5)  # Simulate API call
    
    async def _scrape_single_source(self, account: Dict[str, Any], source: str):
        """Scrape single source (mock implementation)"""
        logger.debug(f"Scraping source {source} using account {account['phone']}")
        await asyncio.sleep(1.0)  # Simulate API call
    
    def _get_task(self, task_id: str) -> Dict[str, Any]:
        """Get task by ID"""
        for task in self.scheduled_tasks:
            if task['id'] == task_id:
                return task
        return None
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get task status and progress"""
        task = self._get_task(task_id)
        if not task:
            return {'status': 'not_found'}
        
        return {
            'id': task['id'],
            'type': task['type'],
            'status': task['status'],
            'progress': task['progress'],
            'total_actions': task['total_actions'],
            'progress_percentage': (task['progress'] / task['total_actions']) * 100,
            'created_at': task['created_at'].isoformat(),
            'error': task.get('error')
        }
    
    def list_tasks(self, status_filter: str = None) -> List[Dict[str, Any]]:
        """List all tasks with optional status filter"""
        tasks = self.scheduled_tasks.copy()
        
        if status_filter:
            tasks = [task for task in tasks if task['status'] == status_filter]
        
        return [self.get_task_status(task['id']) for task in tasks]

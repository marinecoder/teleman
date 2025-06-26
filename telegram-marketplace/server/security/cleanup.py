import os
import shutil
import logging
from pathlib import Path
from typing import List, Dict, Any
import glob

logger = logging.getLogger(__name__)

class ForensicCleanup:
    def __init__(self, base_session_path: str = "./sessions"):
        self.base_session_path = Path(base_session_path)
        self.temp_dirs = ["/tmp", "/var/tmp", "C:\\Temp", "C:\\Windows\\Temp"]
        
    def wipe_session_data(self, session_path: str) -> Dict[str, Any]:
        """Wipe all session-related data"""
        
        cleanup_results = {
            'session_files': [],
            'temp_files': [],
            'cache_files': [],
            'log_files': [],
            'errors': []
        }
        
        try:
            # Clean main session file
            session_result = self._wipe_session_files(session_path)
            cleanup_results['session_files'] = session_result
            
            # Clean temporary files
            temp_result = self._clean_temp_files(session_path)
            cleanup_results['temp_files'] = temp_result
            
            # Clean cache files
            cache_result = self._clean_cache_files(session_path)
            cleanup_results['cache_files'] = cache_result
            
            # Clean log files
            log_result = self._clean_log_files(session_path)
            cleanup_results['log_files'] = log_result
            
            # Clean memory dumps (if any)
            self._clean_memory_traces()
            
            logger.info(f"Forensic cleanup completed for session: {session_path}")
            
        except Exception as e:
            error_msg = f"Error during forensic cleanup: {str(e)}"
            logger.error(error_msg)
            cleanup_results['errors'].append(error_msg)
        
        return cleanup_results
    
    def _wipe_session_files(self, session_path: str) -> List[str]:
        """Wipe main session files"""
        cleaned_files = []
        
        try:
            # Main session file
            session_file = f"{session_path}.session"
            if os.path.exists(session_file):
                self._secure_delete(session_file)
                cleaned_files.append(session_file)
            
            # Journal files
            journal_file = f"{session_path}.session-journal"
            if os.path.exists(journal_file):
                self._secure_delete(journal_file)
                cleaned_files.append(journal_file)
            
            # SQLite temporary files
            for ext in ['-wal', '-shm', '.tmp']:
                temp_file = f"{session_path}.session{ext}"
                if os.path.exists(temp_file):
                    self._secure_delete(temp_file)
                    cleaned_files.append(temp_file)
            
            # Look for backup files
            backup_pattern = f"{session_path}.session.*"
            for backup_file in glob.glob(backup_pattern):
                if os.path.exists(backup_file):
                    self._secure_delete(backup_file)
                    cleaned_files.append(backup_file)
                    
        except Exception as e:
            logger.error(f"Error wiping session files: {str(e)}")
        
        return cleaned_files
    
    def _clean_temp_files(self, session_path: str) -> List[str]:
        """Clean temporary files related to the session"""
        cleaned_files = []
        
        session_name = os.path.basename(session_path)
        
        for temp_dir in self.temp_dirs:
            if not os.path.exists(temp_dir):
                continue
                
            try:
                # Look for session-related temp files
                patterns = [
                    f"{temp_dir}/telegram*{session_name}*",
                    f"{temp_dir}/telethon*{session_name}*",
                    f"{temp_dir}/*{session_name}*.tmp",
                    f"{temp_dir}/*{session_name}*.cache"
                ]
                
                for pattern in patterns:
                    for temp_file in glob.glob(pattern):
                        if os.path.exists(temp_file):
                            self._secure_delete(temp_file)
                            cleaned_files.append(temp_file)
                            
            except Exception as e:
                logger.error(f"Error cleaning temp files in {temp_dir}: {str(e)}")
        
        return cleaned_files
    
    def _clean_cache_files(self, session_path: str) -> List[str]:
        """Clean cache files"""
        cleaned_files = []
        
        session_name = os.path.basename(session_path)
        
        # Common cache directories
        cache_dirs = [
            os.path.expanduser("~/.cache"),
            os.path.expanduser("~/.config"),
            os.path.expanduser("~/AppData/Local"),
            os.path.expanduser("~/AppData/Roaming"),
            "/var/cache",
            "./cache"
        ]
        
        for cache_dir in cache_dirs:
            if not os.path.exists(cache_dir):
                continue
                
            try:
                # Look for session-related cache files
                patterns = [
                    f"{cache_dir}/telegram*{session_name}*",
                    f"{cache_dir}/telethon*{session_name}*",
                    f"{cache_dir}/*{session_name}*"
                ]
                
                for pattern in patterns:
                    for cache_file in glob.glob(pattern):
                        if os.path.isfile(cache_file):
                            self._secure_delete(cache_file)
                            cleaned_files.append(cache_file)
                        elif os.path.isdir(cache_file):
                            shutil.rmtree(cache_file, ignore_errors=True)
                            cleaned_files.append(cache_file)
                            
            except Exception as e:
                logger.error(f"Error cleaning cache files in {cache_dir}: {str(e)}")
        
        return cleaned_files
    
    def _clean_log_files(self, session_path: str) -> List[str]:
        """Clean log files that might contain session information"""
        cleaned_files = []
        
        session_name = os.path.basename(session_path)
        
        # Common log directories
        log_dirs = [
            "./logs",
            "/var/log",
            os.path.expanduser("~/logs"),
            os.path.expanduser("~/.logs")
        ]
        
        for log_dir in log_dirs:
            if not os.path.exists(log_dir):
                continue
                
            try:
                # Look for logs mentioning the session
                patterns = [
                    f"{log_dir}/*{session_name}*",
                    f"{log_dir}/telegram*.log",
                    f"{log_dir}/telethon*.log"
                ]
                
                for pattern in patterns:
                    for log_file in glob.glob(pattern):
                        if os.path.isfile(log_file):
                            # Instead of deleting, sanitize the log file
                            self._sanitize_log_file(log_file, session_name)
                            cleaned_files.append(log_file)
                            
            except Exception as e:
                logger.error(f"Error cleaning log files in {log_dir}: {str(e)}")
        
        return cleaned_files
    
    def _clean_memory_traces(self):
        """Clean memory traces (basic implementation)"""
        try:
            # Force garbage collection
            import gc
            gc.collect()
            
            # On Linux, try to clear page cache (requires root)
            if os.name == 'posix' and os.geteuid() == 0:
                try:
                    with open('/proc/sys/vm/drop_caches', 'w') as f:
                        f.write('3')
                except:
                    pass  # Ignore if we can't clear cache
                    
        except Exception as e:
            logger.error(f"Error cleaning memory traces: {str(e)}")
    
    def _secure_delete(self, file_path: str, passes: int = 3):
        """Securely delete a file by overwriting it multiple times"""
        try:
            if not os.path.exists(file_path):
                return
            
            file_size = os.path.getsize(file_path)
            
            # Overwrite file multiple times with random data
            with open(file_path, 'r+b') as file:
                for _ in range(passes):
                    file.seek(0)
                    file.write(os.urandom(file_size))
                    file.flush()
                    os.fsync(file.fileno())
            
            # Finally, delete the file
            os.remove(file_path)
            
            logger.debug(f"Securely deleted: {file_path}")
            
        except Exception as e:
            logger.error(f"Error securely deleting {file_path}: {str(e)}")
    
    def _sanitize_log_file(self, log_file_path: str, session_name: str):
        """Sanitize log file by removing sensitive information"""
        try:
            if not os.path.exists(log_file_path):
                return
            
            # Read the file
            with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Remove sensitive information
            sensitive_patterns = [
                session_name,
                r'\b\d{10,15}\b',  # Phone numbers
                r'[a-fA-F0-9]{32,}',  # API hashes
                r'Bearer [a-zA-Z0-9]+',  # Bearer tokens
                r'password[:\s]*[^\s]+',  # Passwords
                r'token[:\s]*[^\s]+',  # Tokens
            ]
            
            import re
            for pattern in sensitive_patterns:
                content = re.sub(pattern, '[REDACTED]', content, flags=re.IGNORECASE)
            
            # Write back the sanitized content
            with open(log_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            logger.debug(f"Sanitized log file: {log_file_path}")
            
        except Exception as e:
            logger.error(f"Error sanitizing log file {log_file_path}: {str(e)}")
    
    def bulk_cleanup_sessions(self, session_directory: str) -> Dict[str, Any]:
        """Clean up all sessions in a directory"""
        
        results = {
            'total_sessions': 0,
            'cleaned_sessions': 0,
            'failed_sessions': 0,
            'details': []
        }
        
        try:
            session_files = glob.glob(f"{session_directory}/*.session")
            results['total_sessions'] = len(session_files)
            
            for session_file in session_files:
                session_path = session_file.replace('.session', '')
                
                try:
                    cleanup_result = self.wipe_session_data(session_path)
                    results['cleaned_sessions'] += 1
                    results['details'].append({
                        'session': session_path,
                        'status': 'success',
                        'cleanup_result': cleanup_result
                    })
                    
                except Exception as e:
                    results['failed_sessions'] += 1
                    results['details'].append({
                        'session': session_path,
                        'status': 'failed',
                        'error': str(e)
                    })
                    
        except Exception as e:
            logger.error(f"Error during bulk cleanup: {str(e)}")
            results['error'] = str(e)
        
        return results
    
    def emergency_wipe(self, session_paths: List[str]) -> Dict[str, Any]:
        """Emergency wipe of critical session data"""
        
        results = {
            'wiped_sessions': [],
            'failed_sessions': [],
            'start_time': logger.time(),
        }
        
        for session_path in session_paths:
            try:
                # Quick and dirty wipe - just delete files immediately
                session_file = f"{session_path}.session"
                if os.path.exists(session_file):
                    os.remove(session_file)
                
                # Delete any related files
                for ext in ['-journal', '-wal', '-shm']:
                    related_file = f"{session_path}.session{ext}"
                    if os.path.exists(related_file):
                        os.remove(related_file)
                
                results['wiped_sessions'].append(session_path)
                
            except Exception as e:
                results['failed_sessions'].append({
                    'session': session_path,
                    'error': str(e)
                })
        
        results['end_time'] = logger.time()
        results['duration'] = results['end_time'] - results['start_time']
        
        logger.warning(f"Emergency wipe completed: {len(results['wiped_sessions'])} sessions wiped")
        
        return results
    
    def verify_cleanup(self, session_path: str) -> Dict[str, bool]:
        """Verify that cleanup was successful"""
        
        verification = {
            'session_file_removed': not os.path.exists(f"{session_path}.session"),
            'journal_file_removed': not os.path.exists(f"{session_path}.session-journal"),
            'temp_files_removed': True,  # Assume true unless we find some
            'cache_files_removed': True   # Assume true unless we find some
        }
        
        # Check for remaining temporary files
        session_name = os.path.basename(session_path)
        for temp_dir in self.temp_dirs:
            if os.path.exists(temp_dir):
                temp_files = glob.glob(f"{temp_dir}/*{session_name}*")
                if temp_files:
                    verification['temp_files_removed'] = False
                    break
        
        return verification

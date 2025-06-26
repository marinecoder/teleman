from itertools import cycle
import random
import aiohttp
import asyncio
import logging

logger = logging.getLogger(__name__)

class ProxyHandler:
    def __init__(self, proxies: list):
        self.proxies = proxies
        self.proxy_cycle = cycle(proxies) if proxies else cycle([])
        self.failed_proxies = set()
        self.proxy_stats = {proxy: {'success': 0, 'failures': 0} for proxy in proxies}
    
    def get_next_proxy(self):
        """Get next proxy in rotation"""
        if not self.proxies:
            return None
        
        # Try to get a working proxy
        attempts = 0
        while attempts < len(self.proxies):
            proxy = next(self.proxy_cycle)
            if proxy not in self.failed_proxies:
                return proxy
            attempts += 1
        
        # If all proxies failed, reset and try again
        self.failed_proxies.clear()
        return next(self.proxy_cycle)
    
    def get_best_proxy(self):
        """Get proxy with best success rate"""
        if not self.proxies:
            return None
        
        working_proxies = [p for p in self.proxies if p not in self.failed_proxies]
        if not working_proxies:
            return self.get_next_proxy()
        
        # Calculate success rates
        best_proxy = max(working_proxies, key=lambda p: self._get_success_rate(p))
        return best_proxy
    
    def _get_success_rate(self, proxy: str) -> float:
        """Calculate success rate for a proxy"""
        stats = self.proxy_stats.get(proxy, {'success': 0, 'failures': 0})
        total = stats['success'] + stats['failures']
        if total == 0:
            return 1.0
        return stats['success'] / total
    
    def mark_proxy_success(self, proxy: str):
        """Mark proxy as successful"""
        if proxy in self.proxy_stats:
            self.proxy_stats[proxy]['success'] += 1
        
        # Remove from failed list if it was there
        self.failed_proxies.discard(proxy)
    
    def mark_proxy_failure(self, proxy: str):
        """Mark proxy as failed"""
        if proxy in self.proxy_stats:
            self.proxy_stats[proxy]['failures'] += 1
        
        # Add to failed list if too many failures
        if self._get_success_rate(proxy) < 0.3:  # Less than 30% success rate
            self.failed_proxies.add(proxy)
    
    async def test_proxy(self, proxy: str, timeout: int = 10) -> bool:
        """Test if a proxy is working"""
        try:
            proxy_url = f"http://{proxy}"
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "http://httpbin.org/ip",
                    proxy=proxy_url,
                    timeout=aiohttp.ClientTimeout(total=timeout)
                ) as response:
                    if response.status == 200:
                        self.mark_proxy_success(proxy)
                        return True
                    else:
                        self.mark_proxy_failure(proxy)
                        return False
        except Exception as e:
            logger.warning(f"Proxy {proxy} test failed: {str(e)}")
            self.mark_proxy_failure(proxy)
            return False
    
    async def test_all_proxies(self) -> dict:
        """Test all proxies and return results"""
        results = {}
        tasks = []
        
        for proxy in self.proxies:
            task = self.test_proxy(proxy)
            tasks.append((proxy, task))
        
        for proxy, task in tasks:
            try:
                result = await task
                results[proxy] = result
            except Exception as e:
                results[proxy] = False
                logger.error(f"Error testing proxy {proxy}: {str(e)}")
        
        return results
    
    def get_proxy_stats(self) -> dict:
        """Get statistics for all proxies"""
        stats = {}
        for proxy in self.proxies:
            proxy_stat = self.proxy_stats.get(proxy, {'success': 0, 'failures': 0})
            stats[proxy] = {
                'success_rate': self._get_success_rate(proxy),
                'total_requests': proxy_stat['success'] + proxy_stat['failures'],
                'is_failed': proxy in self.failed_proxies
            }
        return stats
    
    def get_working_proxies(self) -> list:
        """Get list of currently working proxies"""
        return [p for p in self.proxies if p not in self.failed_proxies]
    
    def add_proxy(self, proxy: str):
        """Add a new proxy to the pool"""
        if proxy not in self.proxies:
            self.proxies.append(proxy)
            self.proxy_stats[proxy] = {'success': 0, 'failures': 0}
            # Recreate cycle with new proxy list
            self.proxy_cycle = cycle(self.proxies)
    
    def remove_proxy(self, proxy: str):
        """Remove a proxy from the pool"""
        if proxy in self.proxies:
            self.proxies.remove(proxy)
            self.proxy_stats.pop(proxy, None)
            self.failed_proxies.discard(proxy)
            # Recreate cycle with updated proxy list
            self.proxy_cycle = cycle(self.proxies) if self.proxies else cycle([])

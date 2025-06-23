import requests
import threading
import time
import statistics
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import mysql.connector
from collections import defaultdict
import sys

class PerformanceMonitor:
    def __init__(self, base_url, mysql_config):
        self.base_url = base_url
        self.mysql_config = mysql_config
        self.response_times = []
        self.success_count = 0
        self.failure_count = 0
        self.errors = []
        self.start_time = None
        self.end_time = None
        self.db_metrics = []
        self.lock = threading.Lock()
    
    def test_single_user_session(self, user_id):
        """Simulate a complete user session and measure response times"""
        session = requests.Session()
        session_metrics = {
            'user_id': user_id,
            'responses': [],
            'errors': [],
            'total_time': 0
        }
        
        session_start = time.time()
        
        try:
            # Test 1: Homepage
            start_time = time.time()
            response = session.get(f'{self.base_url}/', timeout=30)
            response_time = time.time() - start_time
            
            session_metrics['responses'].append({
                'endpoint': 'homepage',
                'status_code': response.status_code,
                'response_time': response_time,
                'success': response.status_code == 200
            })
            
            # Test 2: Products page
            start_time = time.time()
            response = session.get(f'{self.base_url}/products', timeout=30)
            response_time = time.time() - start_time
            
            session_metrics['responses'].append({
                'endpoint': 'products',
                'status_code': response.status_code,
                'response_time': response_time,
                'success': response.status_code == 200
            })
            
            # Test 3: User Registration
            start_time = time.time()
            user_data = {
                'username': f'testuser_{user_id}_{int(time.time() * 1000) % 100000}',
                'email': f'test_{user_id}_{int(time.time() * 1000) % 100000}@example.com',
                'first_name': 'Test',
                'last_name': 'User',
                'password': 'testpass123',
                'password2': 'testpass123',
                'submit': 'Register'
            }
            
            # Get CSRF token first
            reg_page = session.get(f'{self.base_url}/auth/register')
            response = session.post(f'{self.base_url}/auth/register', data=user_data, timeout=30)
            response_time = time.time() - start_time
            
            session_metrics['responses'].append({
                'endpoint': 'register',
                'status_code': response.status_code,
                'response_time': response_time,
                'success': response.status_code in [200, 302]  # 302 for redirect after success
            })
            
            # Test 4: Login
            if response.status_code in [200, 302]:
                start_time = time.time()
                login_data = {
                    'username': user_data['username'],
                    'password': user_data['password'],
                    'submit': 'Login'
                }
                response = session.post(f'{self.base_url}/auth/login', data=login_data, timeout=30)
                response_time = time.time() - start_time
                
                session_metrics['responses'].append({
                    'endpoint': 'login',
                    'status_code': response.status_code,
                    'response_time': response_time,
                    'success': response.status_code in [200, 302]
                })
                
                # Test 5: Add to cart (if login successful)
                if response.status_code in [200, 302]:
                    start_time = time.time()
                    response = session.get(f'{self.base_url}/shop/add_to_cart/1?quantity=1', timeout=30)
                    response_time = time.time() - start_time
                    
                    session_metrics['responses'].append({
                        'endpoint': 'add_to_cart',
                        'status_code': response.status_code,
                        'response_time': response_time,
                        'success': response.status_code in [200, 302]
                    })
                    
                    # Test 6: View cart
                    start_time = time.time()
                    response = session.get(f'{self.base_url}/shop/cart', timeout=30)
                    response_time = time.time() - start_time
                    
                    session_metrics['responses'].append({
                        'endpoint': 'cart',
                        'status_code': response.status_code,
                        'response_time': response_time,
                        'success': response.status_code == 200
                    })
            
        except Exception as e:
            session_metrics['errors'].append(str(e))
        
        session_metrics['total_time'] = time.time() - session_start
        
        # Update global metrics
        with self.lock:
            for resp in session_metrics['responses']:
                self.response_times.append(resp['response_time'])
                if resp['success']:
                    self.success_count += 1
                else:
                    self.failure_count += 1
            
            for error in session_metrics['errors']:
                self.errors.append(error)
        
        return session_metrics
    
    def get_database_metrics(self):
        """Get database connection pool and performance metrics"""
        try:
            connection = mysql.connector.connect(**self.mysql_config)
            cursor = connection.cursor()
            
            # Query 1: Connection status
            cursor.execute("SHOW STATUS LIKE 'Connections'")
            connections = cursor.fetchone()
            
            # Query 2: Thread status
            cursor.execute("SHOW STATUS LIKE 'Threads_%'")
            thread_stats = cursor.fetchall()
            
            # Query 3: Query performance
            cursor.execute("SHOW STATUS LIKE 'Queries'")
            queries = cursor.fetchone()
            
            # Query 4: Connection pool info (if available)
            cursor.execute("SHOW VARIABLES LIKE 'max_connections'")
            max_connections = cursor.fetchone()
            
            # Query 5: Current processes
            cursor.execute("SHOW PROCESSLIST")
            processes = cursor.fetchall()

            # Safely convert values to int
            total_conns = int(connections[1]) if connections and connections[1].isdigit() else 0
            total_queries = int(queries[1]) if queries and queries[1].isdigit() else 0
            max_conns = int(max_connections[1]) if max_connections and max_connections[1].isdigit() else 0
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'total_connections': total_conns,
                'max_connections': max_conns,
                'current_processes': len(processes),
                'thread_stats': {k: int(v) if isinstance(v, (str, bytes)) and str(v).isdigit() else v for k, v in thread_stats},
                'total_queries': total_queries
            }
            
            cursor.close()
            connection.close()
            
            return metrics
            
        except Exception as e:
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    def run_load_test(self, num_users=100, duration_seconds=None):
        """Run the load test with specified number of concurrent users"""
        print(f"Starting load test with {num_users} concurrent users...")
        print(f"Target URL: {self.base_url}")
        print(f"Start time: {datetime.now()}")
        print("-" * 50)
        
        self.start_time = time.time()
        
        # Start database monitoring in separate thread
        db_monitor_thread = threading.Thread(target=self._monitor_database)
        db_monitor_thread.daemon = True
        db_monitor_thread.start()
        
        # Run concurrent user sessions
        with ThreadPoolExecutor(max_workers=num_users) as executor:
            future_to_user = {
                executor.submit(self.test_single_user_session, i): i 
                for i in range(num_users)
            }
            
            completed = 0
            for future in as_completed(future_to_user):
                user_id = future_to_user[future]
                try:
                    result = future.result()
                    completed += 1
                    if completed % 10 == 0:
                        print(f"Completed {completed}/{num_users} user sessions...")
                except Exception as e:
                    with self.lock:
                        self.errors.append(f"User {user_id}: {str(e)}")
        
        self.end_time = time.time()
        
        # Wait a bit for database monitoring to complete
        time.sleep(2)
        
        return self.generate_report()
    
    def _monitor_database(self):
        """Monitor database metrics during the test"""
        start_time = time.time()
        while self.end_time is None or time.time() - start_time < 30:
            metrics = self.get_database_metrics()
            self.db_metrics.append(metrics)
            time.sleep(1)  # Check every second
    
    def generate_report(self):
        """Generate comprehensive performance report"""
        if not self.response_times:
            return {"error": "No response times recorded"}
        
        total_requests = self.success_count + self.failure_count
        success_rate = (self.success_count / total_requests * 100) if total_requests > 0 else 0
        
        # Calculate database connection pool utilization
        db_utilization = 0
        if self.db_metrics:
            valid_metrics = [m for m in self.db_metrics if 'error' not in m]
            if valid_metrics:
                avg_processes = statistics.mean([m['current_processes'] for m in valid_metrics])
                max_conn = valid_metrics[0].get('max_connections', 100)
                db_utilization = (avg_processes / max_conn * 100) if max_conn > 0 else 0
        
        report = {
            'test_summary': {
                'total_duration': self.end_time - self.start_time,
                'total_requests': total_requests,
                'successful_requests': self.success_count,
                'failed_requests': self.failure_count,
                'success_rate_percent': round(success_rate, 2)
            },
            'response_time_metrics': {
                'average_response_time': round(statistics.mean(self.response_times), 3),
                'median_response_time': round(statistics.median(self.response_times), 3),
                'min_response_time': round(min(self.response_times), 3),
                'max_response_time': round(max(self.response_times), 3),
                'p95_response_time': round(statistics.quantiles(self.response_times, n=20)[18], 3),
                'p99_response_time': round(statistics.quantiles(self.response_times, n=100)[98], 3)
            },
            'database_metrics': {
                'average_connection_pool_utilization_percent': round(db_utilization, 2),
                'database_samples_collected': len(self.db_metrics),
                'database_errors': len([m for m in self.db_metrics if 'error' in m])
            },
            'errors': self.errors[:10],  # Show first 10 errors
            'total_errors': len(self.errors)
        }
        
        return report

def main():
    # Configuration
    BASE_URL = 'http://13.48.90.245'  # Change to your server URL
    
    # MySQL configuration - update with your credentials
    MYSQL_CONFIG = {
        'host': 'localhost',
        'user': 'ecommerce_user',
        'password': 'mysql123',  # Update this
        'database': 'ecommerce_db'
    }
    
    # Test parameters
    NUM_USERS = 100
    
    if len(sys.argv) > 1:
        NUM_USERS = int(sys.argv[1])
    
    if len(sys.argv) > 2:
        BASE_URL = sys.argv[2]
    
    # Run the test
    monitor = PerformanceMonitor(BASE_URL, MYSQL_CONFIG)
    
    try:
        report = monitor.run_load_test(NUM_USERS)
        
        # Print detailed report
        print("\n" + "="*60)
        print("PERFORMANCE TEST RESULTS")
        print("="*60)
        
        print(f"\nTEST SUMMARY:")
        print(f"Duration: {report['test_summary']['total_duration']:.2f} seconds")
        print(f"Total Requests: {report['test_summary']['total_requests']}")
        print(f"Successful Requests: {report['test_summary']['successful_requests']}")
        print(f"Failed Requests: {report['test_summary']['failed_requests']}")
        print(f"Success Rate: {report['test_summary']['success_rate_percent']}%")
        
        print(f"\nRESPONSE TIME METRICS:")
        print(f"Average Response Time: {report['response_time_metrics']['average_response_time']} seconds")
        print(f"Median Response Time: {report['response_time_metrics']['median_response_time']} seconds")
        print(f"Min Response Time: {report['response_time_metrics']['min_response_time']} seconds")
        print(f"Max Response Time (Peak): {report['response_time_metrics']['max_response_time']} seconds")
        print(f"95th Percentile: {report['response_time_metrics']['p95_response_time']} seconds")
        print(f"99th Percentile: {report['response_time_metrics']['p99_response_time']} seconds")
        
        print(f"\nDATABASE METRICS:")
        print(f"Avg Connection Pool Utilization: {report['database_metrics']['average_connection_pool_utilization_percent']}%")
        print(f"Database Samples Collected: {report['database_metrics']['database_samples_collected']}")
        print(f"Database Errors: {report['database_metrics']['database_errors']}")
        
        if report['errors']:
            print(f"\nSAMPLE ERRORS:")
            for i, error in enumerate(report['errors'][:5], 1):
                print(f"{i}. {error}")
        
        # Save detailed report to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"performance_report_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nDetailed report saved to: {filename}")
        print("="*60)
        
    except Exception as e:
        print(f"Error running performance test: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())

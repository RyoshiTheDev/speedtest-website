"""
Official-Grade Speed Test - Railway/Cloud Optimized
Works perfectly on Railway, Render, and other cloud platforms
"""

from flask import Flask, render_template, jsonify
import time
import statistics
from datetime import datetime
import threading
import os
import traceback
import urllib.request
import socket

app = Flask(__name__)
test_results = []

class NetworkTester:
    def __init__(self):
        self.status = "idle"
        self.progress = 0
        self.current_test = None
        self.error_message = None
        
    def measure_ping(self):
        """HTTP ping - works everywhere"""
        self.status = "testing_ping"
        self.progress = 5
        
        import requests
        latencies = []
        
        hosts = [
            'https://www.google.com',
            'https://www.cloudflare.com',
            'https://www.amazon.com'
        ]
        
        for i in range(10):
            try:
                host = hosts[i % len(hosts)]
                start = time.time()
                response = requests.head(host, timeout=2)
                if response.status_code < 500:
                    latency = (time.time() - start) * 1000
                    latencies.append(latency)
                self.progress = 5 + (i + 1)
            except Exception as e:
                print(f"Ping attempt {i+1} failed: {e}")
            time.sleep(0.1)
        
        if latencies:
            avg = statistics.mean(latencies)
            jitter = statistics.stdev(latencies) if len(latencies) > 1 else 0
            print(f"✓ Ping: {avg:.2f} ms (jitter: {jitter:.2f} ms)")
            return {'latency': round(avg, 2), 'jitter': round(jitter, 2)}
        
        return {'latency': 0, 'jitter': 0}
    
    def measure_download(self):
        """HTTP download test - works on all platforms"""
        self.status = "testing_download"
        self.progress = 20
        
        # Test files of different sizes (use multiple for accuracy)
        test_urls = [
            ('http://speedtest.ftp.otenet.gr/files/test10Mb.db', 10),
            ('http://speedtest.ftp.otenet.gr/files/test100Mb.db', 100),
        ]
        
        speeds = []
        
        try:
            import requests
            
            print("\n⬇️ Testing Download Speed...")
            
            # Test with 10MB file first
            url, size_mb = test_urls[0]
            print(f"Downloading {size_mb}MB test file...")
            
            start = time.time()
            response = requests.get(url, timeout=30, stream=True)
            
            total_size = 0
            chunk_size = 8192
            
            for chunk in response.iter_content(chunk_size=chunk_size):
                total_size += len(chunk)
                elapsed = time.time() - start
                
                # Update progress
                self.progress = 20 + min(int((elapsed / 15) * 30), 30)
                
                # Stop after 15 seconds max
                if elapsed > 15:
                    break
            
            elapsed = time.time() - start
            
            if elapsed > 0 and total_size > 0:
                # Calculate Mbps
                mbps = (total_size * 8) / (elapsed * 1_000_000)
                print(f"✓ Download: {mbps:.2f} Mbps ({total_size/1_000_000:.1f} MB in {elapsed:.1f}s)")
                
                self.progress = 50
                return round(mbps, 2)
            
        except Exception as e:
            print(f"Download test error: {e}")
            traceback.print_exc()
        
        # Fallback: smaller test
        try:
            print("Trying smaller test file...")
            url = 'http://speedtest.ftp.otenet.gr/files/test1Mb.db'
            
            start = time.time()
            response = requests.get(url, timeout=10)
            elapsed = time.time() - start
            
            size = len(response.content)
            mbps = (size * 8) / (elapsed * 1_000_000)
            print(f"✓ Download (fallback): {mbps:.2f} Mbps")
            return round(mbps, 2)
        except:
            pass
        
        return 0
    
    def measure_upload(self):
        """HTTP upload test - works on all platforms"""
        self.status = "testing_upload"
        self.progress = 60
        
        try:
            import requests
            
            print("\n⬆️ Testing Upload Speed...")
            
            # Create test data (1MB)
            data_size = 1 * 1024 * 1024  # 1MB
            test_data = b'0' * data_size
            
            # Use httpbin.org for upload testing
            url = 'https://httpbin.org/post'
            
            start = time.time()
            
            # Upload the data
            response = requests.post(
                url,
                data=test_data,
                timeout=20,
                headers={'Content-Type': 'application/octet-stream'}
            )
            
            elapsed = time.time() - start
            
            if elapsed > 0 and response.status_code == 200:
                # Calculate Mbps
                mbps = (data_size * 8) / (elapsed * 1_000_000)
                print(f"✓ Upload: {mbps:.2f} Mbps ({data_size/1_000_000:.1f} MB in {elapsed:.1f}s)")
                
                self.progress = 90
                return round(mbps, 2)
            
        except Exception as e:
            print(f"Upload test error: {e}")
            traceback.print_exc()
        
        return 0
    
    def get_server_info(self):
        """Get server information"""
        try:
            import requests
            
            # Get public IP and ISP info
            response = requests.get('https://ipapi.co/json/', timeout=5)
            data = response.json()
            
            return {
                'name': f"Test Server - {data.get('city', 'Unknown')}",
                'location': f"{data.get('city', 'Unknown')}, {data.get('country_name', 'Unknown')}",
                'distance': 0,
                'latency': 0,
                'host': 'Cloud Platform',
                'isp': data.get('org', 'Unknown ISP'),
                'ip': data.get('ip', 'Unknown')
            }
        except Exception as e:
            print(f"Error getting server info: {e}")
        
        return {
            'name': 'Speed Test Server',
            'location': 'Cloud',
            'distance': 0,
            'latency': 0,
            'host': 'Internet',
            'isp': 'Your ISP',
            'ip': 'Unknown'
        }
    
    def run_full_test(self):
        """Run complete speed test"""
        print("\n" + "="*70)
        print("🚀 CLOUD-OPTIMIZED SPEED TEST")
        print("="*70)
        
        self.status = "initializing"
        self.progress = 0
        self.error_message = None
        
        try:
            # Step 1: Ping
            print("\n[1/3] Testing Latency...")
            ping_results = self.measure_ping()
            
            # Step 2: Download
            print("\n[2/3] Testing Download Speed...")
            download_speed = self.measure_download()
            
            # Step 3: Upload
            print("\n[3/3] Testing Upload Speed...")
            upload_speed = self.measure_upload()
            
            # Get server details
            server_info = self.get_server_info()
            
            # Complete
            self.status = "complete"
            self.progress = 100
            
            result = {
                'timestamp': datetime.now().isoformat(),
                'ping': ping_results['latency'],
                'jitter': ping_results['jitter'],
                'download': download_speed,
                'upload': upload_speed,
                'server': server_info['name'],
                'location': server_info['location'],
                'distance': server_info['distance'],
                'server_latency': server_info['latency'],
                'isp': server_info['isp'],
                'ip': server_info['ip']
            }
            
            print("\n" + "="*70)
            print("✅ TEST COMPLETE")
            print("="*70)
            print(f"  Ping:      {result['ping']} ms")
            print(f"  Jitter:    {result['jitter']} ms")
            print(f"  Download:  {result['download']} Mbps")
            print(f"  Upload:    {result['upload']} Mbps")
            print(f"  ISP:       {result['isp']}")
            print("="*70 + "\n")
            
            # Store result
            test_results.append(result)
            if len(test_results) > 100:
                test_results.pop(0)
            
            self.current_test = result
            return result
            
        except Exception as e:
            self.status = "error"
            self.error_message = str(e)
            print(f"\n❌ Test Error: {e}")
            traceback.print_exc()
            return None

# Global tester
tester = NetworkTester()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/start-test', methods=['POST'])
def start_test():
    if tester.status not in ["idle", "complete", "error"]:
        return jsonify({'error': 'Test already running'}), 400
    
    def run_test():
        try:
            tester.run_full_test()
        except Exception as e:
            print(f"Thread error: {e}")
            traceback.print_exc()
    
    thread = threading.Thread(target=run_test)
    thread.daemon = True
    thread.start()
    
    return jsonify({'status': 'started'})

@app.route('/api/test-status')
def test_status():
    return jsonify({
        'status': tester.status,
        'progress': tester.progress,
        'result': tester.current_test,
        'error': tester.error_message
    })

@app.route('/api/test-history')
def test_history():
    return jsonify({'results': test_results[-10:]})

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    
    # Get port from environment variable (for Railway/Render/Heroku)
    port = int(os.environ.get('PORT', 5000))
    
    print("\n" + "="*70)
    print("🌐 CLOUD-OPTIMIZED SPEED TEST")
    print("="*70)
    print(f"📍 Running on port: {port}")
    print("="*70)
    print("⚡ HTTP-based testing (works on all cloud platforms)")
    print("🌍 Automatic server detection")
    print("="*70 + "\n")
    
    # Use debug=False in production
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode, threaded=True)

"""
Speed Test - Railway Production Version
"""

from flask import Flask, render_template, jsonify
import time
import statistics
from datetime import datetime
import threading
import os
import traceback

app = Flask(__name__)
test_results = []

class NetworkTester:
    def __init__(self):
        self.status = "idle"
        self.progress = 0
        self.current_test = None
        self.error_message = None
        
    def measure_ping(self):
        """HTTP ping"""
        self.status = "testing_ping"
        self.progress = 5
        
        try:
            import requests
            latencies = []
            
            hosts = ['https://www.google.com', 'https://www.cloudflare.com']
            
            for i in range(10):
                try:
                    start = time.time()
                    requests.head(hosts[i % len(hosts)], timeout=2)
                    latencies.append((time.time() - start) * 1000)
                    self.progress = 5 + (i + 1)
                except:
                    pass
                time.sleep(0.1)
            
            if latencies:
                return {
                    'latency': round(statistics.mean(latencies), 2),
                    'jitter': round(statistics.stdev(latencies), 2) if len(latencies) > 1 else 0
                }
        except Exception as e:
            print(f"Ping error: {e}")
        
        return {'latency': 0, 'jitter': 0}
    
    def measure_download(self):
        """Download test with multiple fallbacks"""
        self.status = "testing_download"
        self.progress = 20
        
        # Multiple test file sources
        test_urls = [
            'http://speedtest.ftp.otenet.gr/files/test10Mb.db',
            'http://ipv4.download.thinkbroadband.com/10MB.zip',
            'http://212.183.159.230/10MB.zip',
            'https://proof.ovh.net/files/10Mb.dat',
        ]
        
        try:
            import requests
            
            # Try each URL until one works
            for url in test_urls:
                try:
                    print(f"Trying {url[:50]}...")
                    
                    start = time.time()
                    response = requests.get(url, timeout=30, stream=True)
                    
                    total_size = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        total_size += len(chunk)
                        if time.time() - start > 15:
                            break
                    
                    elapsed = time.time() - start
                    
                    if elapsed > 0 and total_size > 100000:  # At least 100KB downloaded
                        mbps = (total_size * 8) / (elapsed * 1_000_000)
                        print(f"✓ Download: {mbps:.2f} Mbps from {url[:40]}")
                        self.progress = 50
                        return round(mbps, 2)
                    
                except Exception as e:
                    print(f"Failed {url[:40]}: {e}")
                    continue
                
        except Exception as e:
            print(f"Download error: {e}")
        
        return 0
    
    def measure_upload(self):
        """Upload test"""
        self.status = "testing_upload"
        self.progress = 60
        
        try:
            import requests
            
            data_size = 1 * 1024 * 1024
            test_data = b'0' * data_size
            
            start = time.time()
            response = requests.post(
                'https://httpbin.org/post',
                data=test_data,
                timeout=20
            )
            elapsed = time.time() - start
            
            if elapsed > 0 and response.status_code == 200:
                mbps = (data_size * 8) / (elapsed * 1_000_000)
                self.progress = 90
                return round(mbps, 2)
                
        except Exception as e:
            print(f"Upload error: {e}")
        
        return 0
    
    def get_server_info(self):
        """Get server info"""
        try:
            import requests
            response = requests.get('https://ipapi.co/json/', timeout=5)
            data = response.json()
            
            return {
                'name': f"Test Server - {data.get('city', 'Cloud')}",
                'location': f"{data.get('city', 'Cloud')}, {data.get('country_name', 'Internet')}",
                'isp': data.get('org', 'Unknown'),
                'ip': data.get('ip', 'Unknown')
            }
        except:
            pass
        
        return {
            'name': 'Speed Test Server',
            'location': 'Cloud',
            'isp': 'Internet',
            'ip': 'Unknown'
        }
    
    def run_full_test(self):
        """Run test"""
        print("\n=== Starting Speed Test ===")
        
        self.status = "initializing"
        self.progress = 0
        self.error_message = None
        
        try:
            ping_results = self.measure_ping()
            download_speed = self.measure_download()
            upload_speed = self.measure_upload()
            server_info = self.get_server_info()
            
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
                'distance': 0,
                'server_latency': 0,
                'isp': server_info['isp'],
                'ip': server_info['ip']
            }
            
            print(f"✅ Complete - Ping: {result['ping']}ms, Down: {result['download']}Mbps, Up: {result['upload']}Mbps")
            
            test_results.append(result)
            if len(test_results) > 100:
                test_results.pop(0)
            
            self.current_test = result
            return result
            
        except Exception as e:
            self.status = "error"
            self.error_message = str(e)
            print(f"❌ Error: {e}")
            traceback.print_exc()
            return None

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
    
    thread = threading.Thread(target=run_test, daemon=True)
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

@app.route('/health')
def health():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"\n🚀 Starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)

"""
Official-Grade Speed Test
Matches speedtest.net as closely as possible
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
        self.st = None
        self.status = "idle"
        self.progress = 0
        self.current_test = None
        self.error_message = None
        
    def measure_ping(self):
        """ICMP ping - exactly like official speedtest"""
        self.status = "testing_ping"
        self.progress = 5
        
        try:
            import ping3
            ping3.EXCEPTIONS = True
            latencies = []
            
            # Ping multiple times like official speedtest
            for i in range(10):
                try:
                    delay = ping3.ping('8.8.8.8', timeout=2, unit='ms')
                    if delay and delay > 0:
                        latencies.append(delay)
                    self.progress = 5 + (i + 1)
                except Exception as e:
                    print(f"Ping attempt {i+1} failed: {e}")
                time.sleep(0.1)
            
            if len(latencies) >= 3:  # Need at least 3 successful pings
                avg = statistics.mean(latencies)
                jitter = statistics.stdev(latencies) if len(latencies) > 1 else 0
                print(f"✓ Ping: {avg:.2f} ms (jitter: {jitter:.2f} ms)")
                return {'latency': round(avg, 2), 'jitter': round(jitter, 2)}
            else:
                print("⚠ Not enough successful pings, using fallback")
                return self.ping_fallback()
                
        except ImportError:
            print("⚠ ping3 not available, using fallback")
            return self.ping_fallback()
        except Exception as e:
            print(f"⚠ Ping error: {e}, using fallback")
            return self.ping_fallback()
    
    def ping_fallback(self):
        """Fallback ping method"""
        import requests
        latencies = []
        for _ in range(5):
            try:
                start = time.time()
                requests.head('https://www.google.com', timeout=2)
                latencies.append((time.time() - start) * 1000)
                time.sleep(0.1)
            except:
                pass
        
        if latencies:
            return {
                'latency': round(statistics.mean(latencies), 2),
                'jitter': round(statistics.stdev(latencies), 2) if len(latencies) > 1 else 0
            }
        return {'latency': 0, 'jitter': 0}
    
    def measure_download(self):
        """Multi-threaded download - EXACTLY like official speedtest"""
        self.status = "testing_download"
        self.progress = 20
        
        try:
            import speedtest
            
            print("\n📡 Initializing Speedtest...")
            self.st = speedtest.Speedtest()
            self.progress = 25
            
            print("🌍 Finding best server (testing latency to multiple servers)...")
            # This is what makes it accurate - tests latency to find truly best server
            self.st.get_best_server()
            
            server = self.st.results.server
            print(f"✓ Selected: {server['sponsor']} - {server['name']}, {server['country']}")
            print(f"  Distance: {server['d']:.2f} km")
            print(f"  Latency: {server['latency']:.2f} ms")
            
            self.progress = 40
            
            print("\n⬇️  Testing Download Speed...")
            print("   Using multiple connections (like official speedtest)...")
            
            # Use default threading (usually 8-16 threads) - just like speedtest.net
            download_bps = self.st.download()
            
            download_mbps = round(download_bps / 1_000_000, 2)
            print(f"✓ Download: {download_mbps} Mbps")
            
            self.progress = 60
            return download_mbps
            
        except Exception as e:
            print(f"❌ Download test failed: {e}")
            traceback.print_exc()
            return 0
    
    def measure_upload(self):
        """Multi-threaded upload - EXACTLY like official speedtest"""
        self.status = "testing_upload"
        self.progress = 60
        
        try:
            if not self.st:
                print("❌ No speedtest client available")
                return 0
            
            print("\n⬆️  Testing Upload Speed...")
            print("   Using multiple connections (like official speedtest)...")
            
            # Use default threading (usually 8-16 threads) - just like speedtest.net
            upload_bps = self.st.upload()
            
            upload_mbps = round(upload_bps / 1_000_000, 2)
            print(f"✓ Upload: {upload_mbps} Mbps")
            
            self.progress = 90
            return upload_mbps
            
        except Exception as e:
            print(f"❌ Upload test failed: {e}")
            traceback.print_exc()
            return 0
    
    def get_server_info(self):
        """Get detailed server information"""
        try:
            if self.st and hasattr(self.st, 'results'):
                server = self.st.results.server
                client = self.st.results.client
                
                return {
                    'name': server.get('sponsor', 'Unknown'),
                    'location': f"{server.get('name', '')}, {server.get('country', '')}",
                    'distance': round(server.get('d', 0), 2),
                    'latency': round(server.get('latency', 0), 2),
                    'host': server.get('host', ''),
                    'isp': client.get('isp', 'Unknown'),
                    'ip': client.get('ip', 'Unknown')
                }
        except Exception as e:
            print(f"Error getting server info: {e}")
        
        return {
            'name': 'Unknown',
            'location': 'Unknown',
            'distance': 0,
            'latency': 0,
            'host': '',
            'isp': 'Unknown',
            'ip': 'Unknown'
        }
    
    def run_full_test(self):
        """Run complete speed test - OFFICIAL GRADE"""
        print("\n" + "="*70)
        print("🚀 OFFICIAL-GRADE SPEED TEST")
        print("="*70)
        
        self.status = "initializing"
        self.progress = 0
        self.error_message = None
        
        try:
            # Step 1: Ping
            print("\n[1/3] Testing Latency (ICMP Ping)...")
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
            print(f"  Server:    {result['server']} - {result['location']}")
            print(f"  Distance:  {result['distance']} km")
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
        finally:
            self.st = None

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
    
    print("\n" + "="*70)
    print("🌐 OFFICIAL-GRADE SPEED TEST")
    print("="*70)
    print("📍 Local:     http://localhost:5000")
    print("📍 Network:   http://0.0.0.0:5000")
    print("="*70)
    print("⚡ Multi-threaded download & upload (maximum throughput)")
    print("📡 ICMP ping for accurate latency measurement")
    print("🌍 Intelligent server selection (tests multiple servers)")
    print("="*70)
    print("\n⚠️  IMPORTANT: Run as Administrator for ICMP ping!")
    print("   Windows: Right-click PowerShell → Run as Administrator")
    print("   Linux/Mac: sudo python web_app_official.py")
    print("="*70)
    print("\n💡 Press Ctrl+C to stop")
    print("="*70 + "\n")
    
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)

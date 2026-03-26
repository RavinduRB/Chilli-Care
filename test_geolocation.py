"""
Test IP Geolocation System
Tests the ip-api.com integration with both private and public IPs
"""

import requests
import time

def test_ip_geolocation(test_ips):
    """Test geolocation for multiple IPs"""
    print("=" * 70)
    print("Testing IP Geolocation with ip-api.com")
    print("=" * 70)
    
    for ip_info in test_ips:
        ip = ip_info['ip']
        description = ip_info['description']
        
        try:
            print(f"\n{description}")
            print(f"IP: {ip}")
            
            # Handle private IPs
            if (ip.startswith('192.168.') or ip.startswith('10.') or 
                ip.startswith('172.16.') or ip.startswith('172.17.') or
                ip in ['127.0.0.1', 'localhost']):
                print(f"  ⚠️  PRIVATE IP - Cannot be geolocated")
                print(f"  Type: RFC 1918 Private Network Address")
                print(f"  Location: Unknown (local network only)")
                continue
            
            # Query ip-api.com
            response = requests.get(
                f'http://ip-api.com/json/{ip}',
                params={'fields': 'status,country,regionName,city,lat,lon,isp'},
                timeout=3
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'success':
                    print(f"  ✓ SUCCESS - Public IP Geolocated!")
                    print(f"  City: {data.get('city', 'Unknown')}")
                    print(f"  Region: {data.get('regionName', 'Unknown')}")
                    print(f"  Country: {data.get('country', 'Unknown')}")
                    print(f"  Coordinates: ({data.get('lat')}, {data.get('lon')})")
                    print(f"  ISP: {data.get('isp', 'Unknown')}")
                else:
                    print(f"  ✗ Failed: {data.get('message', 'Unknown error')}")
            else:
                print(f"  ✗ HTTP Error: {response.status_code}")
            
            # Rate limiting: 45 requests/minute = ~1.3 seconds between requests
            time.sleep(1.5)
            
        except Exception as e:
            print(f"  ✗ Error: {e}")

if __name__ == '__main__':
    print("\n🔍 IP GEOLOCATION TEST - Private vs Public IPs\n")
    
    # Test with both private and public IPs
    test_ips = [
        # Private IPs (will NOT be geolocated)
        {
            'ip': '127.0.0.1',
            'description': '🏠 TEST 1: Localhost (Private)'
        },
        {
            'ip': '192.168.1.1',
            'description': '🏠 TEST 2: Home Router IP (Private - RFC 1918)'
        },
        {
            'ip': '10.0.0.1',
            'description': '🏠 TEST 3: Corporate Network IP (Private - RFC 1918)'
        },
        {
            'ip': '172.16.0.1',
            'description': '🏠 TEST 4: Private Network IP (Private - RFC 1918)'
        },
        
        # Public IPs (WILL be geolocated)
        {
            'ip': '8.8.8.8',
            'description': '🌐 TEST 5: Google DNS (Public)'
        },
        {
            'ip': '1.1.1.1',
            'description': '🌐 TEST 6: Cloudflare DNS (Public)'
        },
        {
            'ip': '208.67.222.222',
            'description': '🌐 TEST 7: OpenDNS (Public)'
        },
        {
            'ip': '203.101.231.1',
            'description': '🌐 TEST 8: Thailand Public IP'
        },
        {
            'ip': '103.112.200.1',
            'description': '🌐 TEST 9: Sri Lanka Public IP'
        },
    ]
    
    test_ip_geolocation(test_ips)
    
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print("\n✅ Private IPs (127.0.0.1, 192.168.x.x, 10.x.x.x, 172.16-31.x.x):")
    print("   - Cannot be geolocated")
    print("   - Used in local networks only")
    print("   - Will show as 'Private Network' in your system")
    
    print("\n✅ Public IPs (all other IPs):")
    print("   - Can be geolocated to city/region/country")
    print("   - Provided by ISPs to internet-connected devices")
    print("   - Your production system will track these successfully")
    
    print("\n🎯 NEXT STEP:")
    print("   Deploy your app to production (Heroku, AWS, Railway)")
    print("   to see real location tracking with public IPs!")
    print("=" * 70)


"""
Test script to verify IP-based location detection
Tests both private and public IP geolocation
"""

import requests
from datetime import datetime

def get_public_ip():
    """Get the public IP address"""
    try:
        services = [
            'https://api.ipify.org?format=json',
            'https://api.myip.com',
            'https://ipapi.co/json/'
        ]
        
        for service in services:
            try:
                response = requests.get(service, timeout=2)
                if response.status_code == 200:
                    data = response.json()
                    return data.get('ip') or data.get('IP') or data.get('query')
            except:
                continue
        return None
    except Exception as e:
        print(f"Error getting public IP: {e}")
        return None


def get_location_from_ip(ip_address):
    """Get location from IP address using ip-api.com"""
    try:
        response = requests.get(
            f'http://ip-api.com/json/{ip_address}',
            params={'fields': 'status,country,regionName,city,lat,lon'},
            timeout=3
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return {
                    'city': data.get('city', 'Unknown'),
                    'region': data.get('regionName', 'Unknown'),
                    'country': data.get('country', 'Unknown'),
                    'latitude': data.get('lat'),
                    'longitude': data.get('lon')
                }
            else:
                return {'error': data.get('message', 'Unknown error')}
    except Exception as e:
        return {'error': str(e)}
    
    return {'error': 'Failed to get location'}


def test_location_detection():
    """Test IP-based location detection"""
    print("=" * 60)
    print("LOCATION DETECTION TEST")
    print("=" * 60)
    print()
    
    # Test 1: Get public IP
    print("Test 1: Getting Public IP Address")
    print("-" * 60)
    public_ip = get_public_ip()
    if public_ip:
        print(f"✓ Public IP: {public_ip}")
    else:
        print("✗ Failed to get public IP")
        return
    print()
    
    # Test 2: Get location from public IP
    print("Test 2: Getting Location from Public IP")
    print("-" * 60)
    location = get_location_from_ip(public_ip)
    if 'error' not in location:
        print(f"✓ City:      {location.get('city')}")
        print(f"✓ Region:    {location.get('region')}")
        print(f"✓ Country:   {location.get('country')}")
        print(f"✓ Latitude:  {location.get('latitude')}")
        print(f"✓ Longitude: {location.get('longitude')}")
        print()
        print(f"📍 Full Location: {location.get('city')}, {location.get('region')}, {location.get('country')}")
    else:
        print(f"✗ Error: {location.get('error')}")
    print()
    
    # Test 3: Test with some known IPs
    print("Test 3: Testing with Various IP Addresses")
    print("-" * 60)
    
    test_ips = {
        '8.8.8.8': 'Google DNS (US)',
        '1.1.1.1': 'Cloudflare DNS',
        '127.0.0.1': 'Localhost (should fail)',
        '192.168.1.1': 'Private IP (should fail)'
    }
    
    for ip, description in test_ips.items():
        print(f"\nTesting {ip} ({description}):")
        loc = get_location_from_ip(ip)
        if 'error' not in loc:
            print(f"  ✓ Location: {loc.get('city')}, {loc.get('region')}, {loc.get('country')}")
        else:
            print(f"  ✗ {loc.get('error')}")
    
    print()
    print("=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)


if __name__ == '__main__':
    test_location_detection()

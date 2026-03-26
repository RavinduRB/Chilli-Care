# Helper script to demonstrate IP-based location tracking
# This can be integrated into the main application

import requests

def get_location_from_ip(ip_address):
    """
    Get approximate location from IP address using ipapi.co
    Free tier: 1000 requests/day
    
    Args:
        ip_address: IP address to lookup
        
    Returns:
        Dict with location info or None
    """
    try:
        if ip_address in ['127.0.0.1', 'localhost', '::1']:
            return {
                'city': 'Local',
                'region': 'Local',
                'country': 'Local'
            }
        
        response = requests.get(f'https://ipapi.co/{ip_address}/json/', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'city': data.get('city', 'Unknown'),
                'region': data.get('region', 'Unknown'),
                'country': data.get('country_name', 'Unknown'),
                'latitude': data.get('latitude'),
                'longitude': data.get('longitude')
            }
    except Exception as e:
        print(f"Error getting location for {ip_address}: {e}")
    
    return None


# Alternative: Use ip-api.com (no API key required, 45 requests/minute)
def get_location_from_ip_alternative(ip_address):
    """
    Alternative location lookup using ip-api.com
    
    Args:
        ip_address: IP address to lookup
        
    Returns:
        Dict with location info or None
    """
    try:
        if ip_address in ['127.0.0.1', 'localhost', '::1']:
            return {
                'city': 'Local',
                'region': 'Local',
                'country': 'Local'
            }
        
        response = requests.get(f'http://ip-api.com/json/{ip_address}', timeout=5)
        
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
    except Exception as e:
        print(f"Error getting location for {ip_address}: {e}")
    
    return None

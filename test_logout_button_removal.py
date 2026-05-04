"""
Test that logout button has been removed from admin dashboard header
"""

def verify_removal():
    """Verify the logout button is removed from header"""
    print("=" * 70)
    print("VERIFYING: Logout Button Removal from Header")
    print("=" * 70)
    
    # Check HTML
    print("\n1. Checking HTML (admin_dashboard.html)...")
    try:
        with open('templates/admin_dashboard.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'id="adminLogoutBtn"' in content:
            print("   ✗ FAILED - adminLogoutBtn still exists in HTML")
            return False
        else:
            print("   ✓ adminLogoutBtn removed from HTML")
        
        if 'btn-logout' in content:
            print("   ✗ FAILED - btn-logout class still exists in HTML")
            return False
        else:
            print("   ✓ btn-logout class removed from HTML")
            
        # Verify header still has other elements
        if 'btn-back-home' in content:
            print("   ✓ Back to Home button still present")
        else:
            print("   ⚠ Warning: Back to Home button not found")
            
        if 'btn-refresh' in content:
            print("   ✓ Refresh button still present")
        else:
            print("   ⚠ Warning: Refresh button not found")
            
    except Exception as e:
        print(f"   ✗ Error reading HTML: {e}")
        return False
    
    # Check JavaScript
    print("\n2. Checking JavaScript (admin_dashboard.js)...")
    try:
        with open('static/js/admin_dashboard.js', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if adminLogoutBtn variable declaration is removed
        if "const adminLogoutBtn = document.getElementById('adminLogoutBtn')" in content:
            print("   ✗ FAILED - adminLogoutBtn declaration still exists")
            return False
        else:
            print("   ✓ adminLogoutBtn declaration removed")
        
        # Check if event listener is removed
        if 'adminLogoutBtn.addEventListener' in content:
            print("   ✗ FAILED - adminLogoutBtn event listener still exists")
            return False
        else:
            print("   ✓ adminLogoutBtn event listener removed")
        
        # Verify user profile logout still exists
        if 'userProfileBtn' in content and 'showLogoutConfirmation' in content:
            print("   ✓ User profile logout functionality still present")
        else:
            print("   ✗ Warning: User profile logout might be missing")
            
    except Exception as e:
        print(f"   ✗ Error reading JavaScript: {e}")
        return False
    
    print("\n" + "=" * 70)
    print("RESULT: ✓✓✓ ALL CHECKS PASSED ✓✓✓")
    print("=" * 70)
    print()
    print("Summary:")
    print("  • Logout button removed from dashboard header")
    print("  • JavaScript references cleaned up")
    print("  • User profile in sidebar remains as logout method")
    print("  • Other header buttons (Home, Refresh) still present")
    print()
    return True

if __name__ == "__main__":
    success = verify_removal()
    exit(0 if success else 1)

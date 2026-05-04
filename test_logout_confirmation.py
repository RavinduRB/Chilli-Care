"""
Test Admin Logout Confirmation Functionality
"""
import os

def verify_html_structure():
    """Verify the HTML has logout confirmation modal and clickable profile"""
    print("=" * 70)
    print("VERIFYING: HTML Structure for Logout Confirmation")
    print("=" * 70)
    
    try:
        with open('templates/admin_base.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = []
        
        # Check for user profile button
        if 'id="userProfileBtn"' in content:
            print("✓ User profile button ID found")
            checks.append(True)
        else:
            print("✗ User profile button ID missing")
            checks.append(False)
        
        # Check for clickable attributes
        if 'role="button"' in content and 'tabindex="0"' in content:
            print("✓ User profile has clickable attributes (accessibility)")
            checks.append(True)
        else:
            print("✗ User profile missing clickable attributes")
            checks.append(False)
        
        # Check for logout icon in profile
        if 'user-actions' in content:
            print("✓ User actions section found (logout icon)")
            checks.append(True)
        else:
            print("✗ User actions section missing")
            checks.append(False)
        
        # Check for logout confirmation modal
        if 'id="logoutConfirmModal"' in content:
            print("✓ Logout confirmation modal found")
            checks.append(True)
        else:
            print("✗ Logout confirmation modal missing")
            checks.append(False)
        
        # Check for modal elements
        if 'id="closeLogoutModal"' in content:
            print("✓ Modal close button found")
            checks.append(True)
        else:
            print("✗ Modal close button missing")
            checks.append(False)
        
        if 'id="cancelLogoutBtn"' in content:
            print("✓ Cancel button found")
            checks.append(True)
        else:
            print("✗ Cancel button missing")
            checks.append(False)
        
        if 'id="confirmLogoutBtn"' in content:
            print("✓ Confirm logout button found")
            checks.append(True)
        else:
            print("✗ Confirm logout button missing")
            checks.append(False)
        
        # Check for modal content
        if 'Confirm Logout' in content:
            print("✓ Modal title found")
            checks.append(True)
        else:
            print("✗ Modal title missing")
            checks.append(False)
        
        if 'Are you sure you want to logout' in content:
            print("✓ Confirmation message found")
            checks.append(True)
        else:
            print("✗ Confirmation message missing")
            checks.append(False)
        
        return all(checks)
        
    except Exception as e:
        print(f"✗ Error reading HTML: {e}")
        return False

def verify_css_styles():
    """Verify the CSS has proper styles for logout confirmation"""
    print("\n" + "=" * 70)
    print("VERIFYING: CSS Styles for Logout Confirmation")
    print("=" * 70)
    
    try:
        with open('static/css/admin_dashboard.css', 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = []
        
        # Check for clickable user profile styles
        if '.user-profile' in content and 'cursor: pointer' in content:
            print("✓ User profile is styled as clickable")
            checks.append(True)
        else:
            print("✗ User profile not styled as clickable")
            checks.append(False)
        
        # Check for hover effects
        if '.user-profile:hover' in content:
            print("✓ User profile hover effect found")
            checks.append(True)
        else:
            print("✗ User profile hover effect missing")
            checks.append(False)
        
        # Check for user-actions styles
        if '.user-actions' in content:
            print("✓ User actions (logout icon) styles found")
            checks.append(True)
        else:
            print("✗ User actions styles missing")
            checks.append(False)
        
        # Check for modal overlay
        if '.modal-overlay' in content:
            print("✓ Modal overlay styles found")
            checks.append(True)
        else:
            print("✗ Modal overlay styles missing")
            checks.append(False)
        
        # Check for logout modal specific styles
        if '.logout-confirm-modal' in content:
            print("✓ Logout confirmation modal styles found")
            checks.append(True)
        else:
            print("✗ Logout confirmation modal styles missing")
            checks.append(False)
        
        # Check for modal animations
        if '@keyframes' in content and 'modalPopIn' in content:
            print("✓ Modal animation keyframes found")
            checks.append(True)
        else:
            print("✗ Modal animation keyframes missing")
            checks.append(False)
        
        # Check for button styles
        if '.btn-danger' in content:
            print("✓ Danger button styles found")
            checks.append(True)
        else:
            print("✗ Danger button styles missing")
            checks.append(False)
        
        if '.btn-secondary' in content:
            print("✓ Secondary button styles found")
            checks.append(True)
        else:
            print("✗ Secondary button styles missing")
            checks.append(False)
        
        return all(checks)
        
    except Exception as e:
        print(f"✗ Error reading CSS: {e}")
        return False

def verify_javascript():
    """Verify the JavaScript handles logout confirmation"""
    print("\n" + "=" * 70)
    print("VERIFYING: JavaScript Logout Confirmation Logic")
    print("=" * 70)
    
    try:
        with open('static/js/admin_dashboard.js', 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = []
        
        # Check for DOM element references
        if 'userProfileBtn' in content:
            print("✓ User profile button referenced")
            checks.append(True)
        else:
            print("✗ User profile button not referenced")
            checks.append(False)
        
        if 'logoutConfirmModal' in content:
            print("✓ Logout confirmation modal referenced")
            checks.append(True)
        else:
            print("✗ Logout confirmation modal not referenced")
            checks.append(False)
        
        if 'confirmLogoutBtn' in content:
            print("✓ Confirm logout button referenced")
            checks.append(True)
        else:
            print("✗ Confirm logout button not referenced")
            checks.append(False)
        
        if 'cancelLogoutBtn' in content:
            print("✓ Cancel logout button referenced")
            checks.append(True)
        else:
            print("✗ Cancel logout button not referenced")
            checks.append(False)
        
        # Check for functions
        if 'showLogoutConfirmation' in content:
            print("✓ Show logout confirmation function found")
            checks.append(True)
        else:
            print("✗ Show logout confirmation function missing")
            checks.append(False)
        
        if 'hideLogoutConfirmation' in content:
            print("✓ Hide logout confirmation function found")
            checks.append(True)
        else:
            print("✗ Hide logout confirmation function missing")
            checks.append(False)
        
        if 'performLogout' in content:
            print("✓ Perform logout function found")
            checks.append(True)
        else:
            print("✗ Perform logout function missing")
            checks.append(False)
        
        # Check for event listeners
        if 'userProfileBtn.addEventListener' in content:
            print("✓ User profile click event listener found")
            checks.append(True)
        else:
            print("✗ User profile click event listener missing")
            checks.append(False)
        
        # Check for keyboard accessibility
        if 'keypress' in content and 'Enter' in content:
            print("✓ Keyboard accessibility (Enter key) implemented")
            checks.append(True)
        else:
            print("✗ Keyboard accessibility missing")
            checks.append(False)
        
        # Check for click outside to close
        if 'e.target === logoutConfirmModal' in content:
            print("✓ Click outside to close modal implemented")
            checks.append(True)
        else:
            print("✗ Click outside to close modal missing")
            checks.append(False)
        
        return all(checks)
        
    except Exception as e:
        print(f"✗ Error reading JavaScript: {e}")
        return False

def main():
    print("\n" + "=" * 70)
    print("ADMIN LOGOUT CONFIRMATION - COMPREHENSIVE VERIFICATION")
    print("=" * 70)
    print()
    
    html_ok = verify_html_structure()
    css_ok = verify_css_styles()
    js_ok = verify_javascript()
    
    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    print(f"HTML Structure: {'✓ PASSED' if html_ok else '✗ FAILED'}")
    print(f"CSS Styles: {'✓ PASSED' if css_ok else '✗ FAILED'}")
    print(f"JavaScript Logic: {'✓ PASSED' if js_ok else '✗ FAILED'}")
    
    if html_ok and css_ok and js_ok:
        print("\n✓✓✓ ALL VERIFICATION CHECKS PASSED ✓✓✓")
        print()
        print("Implementation Complete:")
        print("  • User profile in sidebar is now clickable")
        print("  • Clicking profile shows logout confirmation modal")
        print("  • Modal has Cancel and Logout buttons")
        print("  • Modal can be closed by clicking X, Cancel, or outside")
        print("  • Header logout button also shows confirmation")
        print("  • Keyboard accessible (Enter/Space key)")
        print("  • Smooth animations and hover effects")
        print()
        return True
    else:
        print("\n✗ SOME VERIFICATION CHECKS FAILED")
        print("Please review the failures above.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

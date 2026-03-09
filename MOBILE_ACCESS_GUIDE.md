# Mobile Access Guide - Chilli Care Admin Dashboard

## 🌐 **Accessing from Mobile Phone or Other Devices**

### ✅ **Prerequisites**
1. Your computer is running the Flask server (python app.py)
2. Your mobile device is connected to the **SAME WiFi network** as your computer
3. Windows Firewall allows connections on port 5000

---

## 📱 **Step-by-Step Access Instructions**

### **Step 1: Find Your Computer's IP Address**

Your current IP addresses are:
- **Primary Network IP**: `192.168.207.162` ← Use this one
- Virtual Adapter 1: `172.31.144.1`
- Virtual Adapter 2: `172.28.96.1`

To find your IP address anytime:
```bash
ipconfig | findstr "IPv4"
```

### **Step 2: Access from Mobile Device**

1. **Ensure mobile is on same WiFi** as your computer
2. **Open mobile browser** (Chrome, Safari, etc.)
3. **Enter the following URL:**
   ```
   http://192.168.207.162:5000
   ```

### **Step 3: Access Admin Dashboard**

1. **Login with admin credentials:**
   - Email: `admin@chillicare.com`
   - Password: `admin123`

2. **Navigate to dashboard:**
   ```
   http://192.168.207.162:5000/admin/dashboard
   ```
   
   or Click the **Dashboard** button in the profile dropdown

---

## 🔥 **Windows Firewall Configuration**

If you can't access from mobile device, Windows Firewall might be blocking it.

### **Option 1: Use the Automated Script (Recommended)**

1. **Right-click** on `setup_firewall.bat`
2. **Select** "Run as Administrator"
3. **Press any key** to continue
4. Firewall rules will be added automatically

### **Option 2: Manual Firewall Configuration**

1. **Open Windows Firewall**
   - Press `Win + R`
   - Type: `firewall.cpl`
   - Press Enter

2. **Click** "Advanced settings"

3. **Add Inbound Rule:**
   - Click "Inbound Rules" → "New Rule"
   - Select "Port" → Next
   - Select "TCP" → Enter port: `5000` → Next
   - Select "Allow the connection" → Next
   - Check all profiles (Domain, Private, Public) → Next
   - Name: "Flask Server - Chilli Care" → Finish

4. **Add Outbound Rule:**
   - Click "Outbound Rules" → "New Rule"
   - Follow same steps as above

---

## 🧪 **Testing the Connection**

### **Test 1: From Your Computer**
```
http://localhost:5000
http://127.0.0.1:5000
http://192.168.207.162:5000
```
All should work!

### **Test 2: From Mobile Device**
```
http://192.168.207.162:5000
```
Should show Chilli Care homepage

### **Test 3: Admin Dashboard**
```
http://192.168.207.162:5000/admin/dashboard
```
Should redirect to login if not authenticated

---

## 🎯 **Quick Access URLs (Bookmark These on Mobile)**

Replace `192.168.207.162` with your actual IP if different:

- **Homepage**: `http://192.168.207.162:5000`
- **Admin Dashboard**: `http://192.168.207.162:5000/admin/dashboard`
- **About Page**: `http://192.168.207.162:5000/about`

---

## 🔧 **Troubleshooting**

### **Problem: Cannot access from mobile**

**Solution 1: Check same WiFi network**
- Ensure computer and mobile are on the SAME WiFi network
- Not on mobile data or guest network

**Solution 2: Check firewall**
- Run `setup_firewall.bat` as Administrator
- Or manually add firewall rules (see above)

**Solution 3: Check server is running**
- Look for "Running on http://0.0.0.0:5000" in terminal
- Restart server if needed: `python app.py`

**Solution 4: Try different IP address**
- If `192.168.207.162` doesn't work, try other IP addresses from ipconfig
- Usually starts with `192.168.x.x`

### **Problem: Connection refused**

**Check:**
1. Is Flask server running?
2. Is firewall blocking connection?
3. Is port 5000 already in use?

**Solution:**
```bash
# Kill any existing Python processes
taskkill //F //IM python.exe

# Start server again
python app.py
```

### **Problem: Page loads but looks broken on mobile**

**Don't worry!** The dashboard is fully responsive and should work on all devices.

**Try:**
1. Clear browser cache
2. Try different browser (Chrome, Safari)
3. Force reload (Ctrl+F5 or Cmd+Shift+R)

---

## 📊 **Mobile Dashboard Features**

The admin dashboard is **fully responsive** and includes:

✅ **Mobile-optimized layout**
- Single-column stat cards
- Collapsible sidebar with hamburger menu
- Touch-friendly buttons (44x44px minimum)
- Responsive charts

✅ **Real-time updates**
- Auto-refresh every 30 seconds
- Manual refresh button
- Live update indicator

✅ **All features work on mobile:**
- View statistics
- Check recent activity
- Navigate all sections
- Logout functionality

---

## 🌍 **Accessing from Other Computers on Same Network**

Same steps apply for accessing from:
- Other laptops on same WiFi
- Tablets
- Any device on same network

Just use the URL:
```
http://192.168.207.162:5000
```

---

## 🔐 **Security Notice**

⚠️ **Important:**
- Server is only accessible on **local network** (not from internet)
- Change default admin password in production
- Use HTTPS in production environment
- Consider VPN for remote access

---

## 📞 **Need Help?**

If you still can't access:

1. **Check server is running:**
   ```bash
   python app.py
   ```
   Should see: "Running on http://0.0.0.0:5000"

2. **Verify your IP hasn't changed:**
   ```bash
   ipconfig | findstr "IPv4"
   ```

3. **Test on computer first:**
   ```
   http://192.168.207.162:5000
   ```
   If this works on computer, firewall is the issue

4. **Check Flask logs** for any errors in terminal

---

**Last Updated**: March 9, 2026  
**Your IP**: 192.168.207.162  
**Port**: 5000  
**Status**: ✅ Ready for mobile access

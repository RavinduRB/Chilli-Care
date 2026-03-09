@echo off
echo ================================================
echo Windows Firewall Configuration for Flask Server
echo ================================================
echo.
echo This script will add firewall rules to allow access to your Flask server
echo from other devices on your local network.
echo.
echo Press any key to continue or CTRL+C to cancel...
pause > nul

echo.
echo Adding inbound rule for Flask server (Port 5000)...
netsh advfirewall firewall add rule name="Flask Server - Chilli Care" dir=in action=allow protocol=TCP localport=5000

echo.
echo Adding outbound rule for Flask server (Port 5000)...
netsh advfirewall firewall add rule name="Flask Server - Chilli Care" dir=out action=allow protocol=TCP localport=5000

echo.
echo ================================================
echo Firewall rules added successfully!
echo ================================================
echo.
echo Your Flask server should now be accessible from other devices.
echo.
echo Access from mobile device:
echo   http://192.168.207.162:5000
echo.
echo Admin Dashboard:
echo   http://192.168.207.162:5000/admin/dashboard
echo.
echo Login credentials:
echo   Email: admin@chillicare.com
echo   Password: admin123
echo.
echo ================================================
pause

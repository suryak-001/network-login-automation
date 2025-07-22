# 🌐 Office Network Login Automation

This Python script automates the login process to a corporate network portal (such as captive portals in offices) by checking internet connectivity, verifying Wi-Fi availability, and using Selenium to submit the login form — all silently in the background.

---

## 🔧 Features

- Detects if internet is already active (ping, DNS, HTTP test)
- Checks if the office Wi-Fi SSID is nearby
- Uses Selenium (headless Chrome) to log in automatically
- Securely reads credentials from a local JSON file
- Logs execution details to `/tmp/network_login.log`
- Designed to run via `systemd` on system unlock or boot

---

## 📦 Requirements

- Python 3.x
- Google Chrome or Chromium
- Chromedriver (`/usr/bin/chromedriver`)
- Selenium
- Requests
- NetworkManager (for `nmcli`)

Install dependencies:

```bash
pip install selenium requests

#!/usr/bin/env python3
import json
import subprocess
import requests
import logging
from logging.handlers import RotatingFileHandler
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(
            '/tmp/network_login.log', 
            maxBytes=1_000_000, # 1 MB 
            backupCount=3       # Keep 3 backups
        ),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def check_internet_connection():
    """Check if the system has internet connectivity"""
    logger.info("\n" + "-"*30)
    logger.info("CHECKING INTERNET CONNECTIVITY")
    logger.info("-"*30)
    
    test_results = {
        'ping': False,
        'http': False,
        'dns': False
    }
    
    # Method 1: Ping Google DNS
    try:
        logger.info("Testing ping to Google DNS (8.8.8.8)...")
        result = subprocess.run(['ping', '-c', '3', '8.8.8.8'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            logger.info("✓ Ping to Google DNS successful!")
            test_results['ping'] = True
        else:
            logger.error("✗ Ping to Google DNS failed!")
    except Exception as e:
        logger.error(f"✗ Ping test failed: {e}")
    
    # Method 2: HTTP request to Google
    try:
        logger.info("Testing HTTP request to google.com...")
        response = requests.get('http://google.com', timeout=10)
        if response.status_code == 200:
            logger.info("✓ HTTP request to google.com successful!")
            test_results['http'] = True
        else:
            logger.error(f"✗ HTTP request failed with status code: {response.status_code}")
    except Exception as e:
        logger.error(f"✗ HTTP request failed: {e}")
    
    # Method 3: DNS resolution test
    try:
        logger.info("Testing DNS resolution...")
        result = subprocess.run(['nslookup', 'google.com'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and "Address:" in result.stdout:
            logger.info("✓ DNS resolution successful!")
            test_results['dns'] = True
        else:
            logger.error("✗ DNS resolution failed!")
    except Exception as e:
        logger.error(f"✗ DNS test failed: {e}")
    
    # Overall connectivity status
    logger.info("\n" + "-"*30)
    logger.info("CONNECTIVITY SUMMARY:")
    logger.info("-"*30)
    
    if all(test_results.values()):
        logger.info("🌐 INTERNET STATUS: ✅ FULLY CONNECTED")
        return True
    elif any(test_results.values()):
        logger.warning("🌐 INTERNET STATUS: ⚠️ PARTIALLY CONNECTED")
        return False
    else:
        logger.error("🌐 INTERNET STATUS: ❌ NO INTERNET CONNECTION")
        return False

def is_office_network_available(ssid="sample ssid"):
    """Check if the specified SSID is available in the nearby Wi-Fi scan list"""
    logger.info("\n" + "-"*30)
    logger.info(f"CHECKING FOR SSID: {ssid}")
    logger.info("-"*30)
    try:
        result = subprocess.run(['nmcli', '-t', '-f', 'SSID', 'dev', 'wifi'], 
                              capture_output=True, text=True, timeout=10)
        available_ssids = result.stdout.strip().split('\n')
        if ssid in available_ssids:
            logger.info(f"✓ SSID '{ssid}' is available.")
            return True
        else:
            logger.warning(f"✗ SSID '{ssid}' is not found in nearby Wi-Fi networks.")
            return False
    except Exception as e:
        logger.error(f"✗ Failed to scan Wi-Fi networks: {e}")
        return False

def main():
    logger.info("="*60)
    logger.info("OFFICE NETWORK LOGIN AUTOMATION")
    logger.info("="*60)

    if check_internet_connection():
        logger.info("\n🌐 Internet connection is already established. No login required.")
        logger.info("="*60)
        logger.info("SCRIPT EXECUTION COMPLETED")
        logger.info("="*60)
        return

    if not is_office_network_available():
        logger.warning("\n⚠️ Office network is not available. Please connect to the office Wi-Fi and try again.")
        logger.info("="*60)
        logger.info("SCRIPT EXECUTION COMPLETED")
        logger.info("="*60)
        return 1

    logger.info("\n🔍 Office network detected, proceeding with login...")

    # Load credentials
    try:
        with open('/path/to/login-credentials.json') as f:
            creds = json.load(f)
        logger.info("✓ Successfully loaded credentials")
    except Exception as e:
        logger.error(f"✗ Failed to load credentials: {e}")
        return 1

    # Setup Chrome options
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    options.add_argument("--disable-images")
    options.add_argument("--disable-javascript")
    options.add_argument("--disable-web-security")
    options.add_argument("--headless=new")

    driver = None
    login_successful = False

    try:
        service = Service(executable_path="/usr/bin/chromedriver")
        logger.info("Starting Chrome browser...")
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_window_size(1920, 1080)
        
        logger.info("Opening login page")
        driver.get("login url here")  # Replace with actual login URL

        logger.info("Waiting for login form to load...")
        username_field = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        
        logger.info("Filling username...")
        username_field.clear()
        username_field.send_keys(creds['username'])
        
        logger.info("Filling password...")
        password_field = driver.find_element(By.NAME, "password")
        password_field.clear()
        password_field.send_keys(creds['password'])
        
        logger.info("Clicking login button...")
        login_button = driver.find_element(By.ID, "loginbutton")
        login_button.click()
        
        logger.info("Waiting for login to complete...")
        sleep(7)
        
        try:
            signed_in_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'You are signed in as')]"))
            )
            signed_in_text = signed_in_element.text
            logger.info(f"✓ Found signed in message: {signed_in_text}")
            login_successful = True
        except Exception as e:
            logger.warning("✗ Did not find signed in confirmation message")
        
        logger.info("Login process completed!")
        
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        
    finally:
        if driver:
            logger.info("Closing browser...")
            driver.quit()
            logger.info("Browser closed successfully.")

    # Post-login verification
    if login_successful:
        logger.info("\n🔍 Login appeared successful, checking internet connectivity...")
        check_internet_connection()
    else:
        logger.warning("\n⚠️ Login status unclear, but checking internet connectivity anyway...")
        check_internet_connection()

    logger.info("\n" + "="*60)
    logger.info("SCRIPT EXECUTION COMPLETED")
    logger.info("="*60)

if __name__ == "__main__":
    main()
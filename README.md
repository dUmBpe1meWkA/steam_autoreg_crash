# Steam Account Auto-Registration Bot(!for educational purposes only!)

This project provides a Python-based automation tool to register Steam accounts at scale, with strong anti-detection features and support for manual CAPTCHA solving and email confirmation.

## 🚀 Features

- Full automation of Steam account registration
- Email confirmation via IMAP (supports custom domains, e.g., Mailu)
- CAPTCHA handling (manual or automated via services like CapMonster or 2Captcha)
- Anti-detect techniques using `undetected_chromedriver` and browser spoofing
- Proxy support (HTTP/SOCKS)
- Randomized mouse movement and human-like interactions
- Saves accounts (login/password) to `.txt` file

## 🛠 Technologies

- Python 3.10+
- `undetected_chromedriver`
- `selenium`
- `imaplib` / `email`
- Optional: CapMonster / 2Captcha
- Optional: GoLogin or other browser profiles

## 📁 Files Structure

- `register.py` – main script for account registration
- `email.txt` – list of email accounts (`login:password`)
- `proxy.txt` – list of proxies (`ip:port:login:password`)
- `spoof.js` – browser fingerprint spoofing
- `extensions/` – Chrome extensions for Canvas/WebRTC spoofing

## ⚙️ Requirements

- Python 3.10 or newer
- Google Chrome installed
- `pip install -r requirements.txt`
- Verified email accounts (e.g., via Mailu)
- CapMonster/2Captcha API key (if using auto-CAPTCHA)

## 📦 Installation

```bash
cd steam-auto-register
pip install -r requirements.txt

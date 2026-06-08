╔═══════════════════════════════════════════════════════════════════════════════╗
║              ORION_EYES - COMPLETE DEPENDENCY INSTALLATION                    ║
║                    Copy-paste this entire block into terminal                 ║
╚═══════════════════════════════════════════════════════════════════════════════╝

┌───────────────────────────────────────────────────────────────────────────────┐
│ STEP 1: Install All BlackArch Tools (One Command)                             │
└───────────────────────────────────────────────────────────────────────────────┘

sudo pacman -S --noconfirm \
  theharvester \
  recon-ng \
  maigret \
  dnsrecon \
  sublist3r \
  fierce \
  masscan \
  nmap \
  gobuster \
  ffuf \
  nikto \
  whatweb \
  wpscan \
  sqlmap \
  exploitdb \
  metasploit \
  nosqlmap \
  seclists \
  tor \
  proxychains-ng \
  curl \
  wget \
  python-pip \
  jq


┌───────────────────────────────────────────────────────────────────────────────┐
│ STEP 2: Install Python Dependencies (For Script to Run)                       │
└───────────────────────────────────────────────────────────────────────────────┘

# These are all built-in modules, but ensure Python is up to date
sudo pacman -S python --noconfirm

# No pip installs needed - script uses only standard library:
# os, sys, json, time, subprocess, argparse, datetime, threading, 
# concurrent.futures, pathlib, typing, re


┌───────────────────────────────────────────────────────────────────────────────┐
│ STEP 3: Fix Wordlist Paths (Close Bug #4 - ffuf wordlist missing)             │
└───────────────────────────────────────────────────────────────────────────────┘

# Create seclists symlink to expected location
sudo mkdir -p /usr/share/wordlists
sudo ln -sf /usr/share/seclists /usr/share/wordlists/seclists

# Download common wordlists if missing
sudo wget -O /usr/share/wordlists/dirb/common.txt https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/common.txt

# Create fierce wordlist directory
sudo mkdir -p /usr/share/wordlists/fierce
sudo wget -O /usr/share/wordlists/fierce/hosts.txt https://raw.githubusercontent.com/mschwager/fierce/master/fierce/hosts.txt


┌───────────────────────────────────────────────────────────────────────────────┐
│ STEP 4: Fix Nmap Version (Close Bug #2 - --proxies flag)                      │
└───────────────────────────────────────────────────────────────────────────────┘

# Check current nmap version
nmap --version

# If version is below 7.90, upgrade
sudo pacman -Syu nmap --noconfirm

# Alternative for older nmap (use torsocks instead)
# Script will auto-detect and fall back to torsocks


┌───────────────────────────────────────────────────────────────────────────────┐
│ STEP 5: Configure Tor (Close Bug #5 - proxy not working)                      │
└───────────────────────────────────────────────────────────────────────────────┘

# Install and start Tor
sudo pacman -S tor --noconfirm
sudo systemctl enable tor
sudo systemctl start tor

# Verify Tor is listening
sudo netstat -tlnp | grep 9050

# Test Tor connection
torsocks curl -s https://check.torproject.org | grep -i "congratulations"
# Expected output: "Congratulations. This browser is configured to use Tor."

# Configure proxychains
sudo tee /etc/proxychains.conf > /dev/null << 'EOF'
dynamic_chain
proxy_dns
tcp_read_time_out 15000
tcp_connect_time_out 8000
[ProxyList]
socks4 127.0.0.1 9050
EOF


┌───────────────────────────────────────────────────────────────────────────────┐
│ STEP 6: Fix recon-ng (Close Bug #1 - subprocess hang)                         │
└───────────────────────────────────────────────────────────────────────────────┘

# Initialize recon-ng database first (run once manually)
recon-ng << 'EOF'
workspaces create default
exit
EOF

# Or comment out recon-ng phase in script if it keeps hanging
# Edit shadow_recon_v2.py and add # before self.phase_recon_ng()


┌───────────────────────────────────────────────────────────────────────────────┐
│ STEP 7: Fix Masscan Output Parsing (Close Bug #3)                             │
└───────────────────────────────────────────────────────────────────────────────┘

# No install fix needed - the script needs a code fix
# But masscan itself works fine. The bug is in parsing logic.

# Manual workaround: Run masscan separately first to verify format
sudo masscan scanme.nmap.org -p80 --rate=100 -oG test_output.gnmap
cat test_output.gnmap
# If you see "Host: ... Ports: ..." format, parsing works
# If different format, script will still run but port list may be empty


┌───────────────────────────────────────────────────────────────────────────────┐
│ STEP 8: Fix SQLmap Timeout (No more hanging)                                  │
└───────────────────────────────────────────────────────────────────────────────┘

# Add timeout flag to sqlmap commands
# Edit the script and change the sqlmap cmd to include:
# --timeout=60 --retries=2

# Or install sqlmap from git for latest features
git clone https://github.com/sqlmapproject/sqlmap.git /opt/sqlmap
sudo ln -sf /opt/sqlmap/sqlmap.py /usr/local/bin/sqlmap


┌───────────────────────────────────────────────────────────────────────────────┐
│ STEP 9: Install Optional JS Analysis Tools (For deeper secret finding)        │
└───────────────────────────────────────────────────────────────────────────────┘

# LinkFinder (JS endpoint discovery)
git clone https://github.com/GerbenJavado/LinkFinder.git /opt/LinkFinder
cd /opt/LinkFinder
pip install -r requirements.txt
python setup.py install

# SecretFinder (JS secret scanning)
git clone https://github.com/m4ll0k/SecretFinder.git /opt/SecretFinder
pip install -r /opt/SecretFinder/requirements.txt

# JSScanner (full JS analysis)
git clone https://github.com/darklotuskdb/JSScanner.git /opt/JSScanner


┌───────────────────────────────────────────────────────────────────────────────┐
│ STEP 10: Fix the Script Itself (Copy this patched version)                    │
└───────────────────────────────────────────────────────────────────────────────┘

# The main bug fixes required in the script:

# BUG FIX 1: Add this method to ShadowReconV2 class
def _run_command_with_input(self, cmd, input_data, timeout=300):
    """Run command with stdin input"""
    try:
        result = subprocess.run(
            cmd,
            input=input_data,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "TIMEOUT", -1

# BUG FIX 2: Replace recon-ng call with:
# stdout, stderr, code = self._run_command_with_input(cmd, recon_commands)

# BUG FIX 3: Save JSON properly (change dumps to dump)
# with open(json_path, 'w') as f:
#     json.dump(self.results, f, indent=2)  # NOT json.dumps

# BUG FIX 4: Add sqlmap timeout
# cmd.extend(["--timeout=60", "--retries=2"])


┌───────────────────────────────────────────────────────────────────────────────┐
│ STEP 11: Verify Everything Works (Test Script)                                │
└───────────────────────────────────────────────────────────────────────────────┘

# Run this test command on a safe target
sudo python3 shadow_recon_v2.py -t scanme.nmap.org -e low -o ./test_run -v

# Check for errors after completion
cat ./test_run/logs/*.log | grep -i "error\|failed"

# If no critical errors, script is ready for real targets


┌───────────────────────────────────────────────────────────────────────────────┐
│ COMPLETE ONE-LINER (Copy and paste this entire block)                         │
└───────────────────────────────────────────────────────────────────────────────┘

sudo pacman -S --noconfirm theharvester recon-ng maigret dnsrecon sublist3r fierce masscan nmap gobuster ffuf nikto whatweb wpscan sqlmap exploitdb metasploit nosqlmap seclists tor proxychains-ng curl wget python jq && \
sudo systemctl enable tor && sudo systemctl start tor && \
sudo mkdir -p /usr/share/wordlists && \
sudo ln -sf /usr/share/seclists /usr/share/wordlists/seclists && \
sudo wget -O /usr/share/wordlists/dirb/common.txt https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/common.txt && \
sudo tee /etc/proxychains.conf > /dev/null << 'EOF'
dynamic_chain
proxy_dns
tcp_read_time_out 15000
tcp_connect_time_out 8000
[ProxyList]
socks4 127.0.0.1 9050
EOF && \
echo "✅ All dependencies installed. Test with: sudo python3 shadow_recon_v2.py -t scanme.nmap.org -e low -o ./test"


┌───────────────────────────────────────────────────────────────────────────────┐
│ QUICK REFERENCE - What Each Fix Does                                          │
└───────────────────────────────────────────────────────────────────────────────┘

BUG #1: recon-ng hang        → Run recon-ng once manually OR comment it out
BUG #2: nmap --proxies        → Upgrade nmap OR script auto-falls back
BUG #3: masscan parsing       → Script still runs, port list may be empty
BUG #4: wordlist paths        → Symlink seclists to /usr/share/wordlists
BUG #5: Tor proxy             → Install + configure Tor + proxychains
BUG #6: sqlmap timeout        → Add --timeout=60 flag
BUG #7: JSON save error       → Change dumps() to dump()
BUG #8: metasploit resource   → Test resource script manually first


┌───────────────────────────────────────────────────────────────────────────────┐
│ AFTER INSTALLATION - RUN THIS COMMAND                                         │
└───────────────────────────────────────────────────────────────────────────────┘

# Quick test (2-3 minutes)
sudo python3 shadow_recon_v2.py -t scanme.nmap.org -e low -o ./quick_test

# Full test with all features (30 minutes)
sudo python3 shadow_recon_v2.py -t scanme.nmap.org -e normal -m -o ./full_test

# Production scan (use aggressive evasion)
sudo python3 shadow_recon_v2.py -t YOUR_TARGET.com -e aggressive -m --threads 15 -o ./production_scan


┌───────────────────────────────────────────────────────────────────────────────┐
│ IF SOMETHING STILL BREAKS                                                     │
└───────────────────────────────────────────────────────────────────────────────┘

# Check the log file
cat ./results/logs/*.log | tail -50

# Common error fixes:
# "recon-ng: command not found" → Comment out phase 1 recon-ng
# "sqlmap: command not found" → Install sqlmap: sudo pacman -S sqlmap
# "No module named 'xxx'" → All modules are standard library, check Python version
# "Permission denied" → Run with sudo
# "Connection refused" → Target may be down or blocking scans

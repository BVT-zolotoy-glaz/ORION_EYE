╔═══════════════════════════════════════════════════════════════════════════════╗
║                         ORION_EYE - USAGE GUIDE                                ║
║                   Advanced BlackArch Reconnaissance Framework                  ║
╚═══════════════════════════════════════════════════════════════════════════════╝

┌───────────────────────────────────────────────────────────────────────────────┐
│ QUICK START                                                                   │
└───────────────────────────────────────────────────────────────────────────────┘

# Save the script as main.py
nano main.py
# (paste the full script)
chmod +x main.py

# Basic scan
sudo python3 main.py -t target.com -o ./results

# Done. Wait for report.


┌───────────────────────────────────────────────────────────────────────────────┐
│ ALL COMMAND OPTIONS                                                           │
└───────────────────────────────────────────────────────────────────────────────┘

REQUIRED:
  -t, --target    Target domain or IP address

OPTIONAL:
  -o, --output    Output directory (default: ./orion_results)
  -e, --evasion   Evasion level: none, low, normal, aggressive, paranoid (default: normal)
  -m, --metasploit  Enable Metasploit modules (opt-in)
  --threads       Number of threads (default: 10)
  -v, --verbose   Show detailed command output


┌───────────────────────────────────────────────────────────────────────────────┐
│ USAGE EXAMPLES                                                                │
└───────────────────────────────────────────────────────────────────────────────┘

# Minimal (normal evasion, no Metasploit)
sudo python3 main.py -t example.com

# Custom output directory
sudo python3 main.py -t example.com -o ./my_scan_results

# Aggressive evasion (stealthier, slower)
sudo python3 main.py -t example.com -e aggressive

# With Metasploit modules
sudo python3 main.py -t example.com -m

# Paranoid evasion + Tor (max stealth)
sudo systemctl start tor
sudo python3 main.py -t example.com -e paranoid --threads 5

# Verbose (see every command being run)
sudo python3 main.py -t example.com -v

# Full power (aggressive evasion + Metasploit + 20 threads)
sudo python3 main.py -t example.com -e aggressive -m --threads 20 -o ./deep_scan


┌───────────────────────────────────────────────────────────────────────────────┐
│ EVASION LEVELS EXPLAINED                                                      │
└───────────────────────────────────────────────────────────────────────────────┘

LEVEL       | SPEED  | STEALTH | USE CASE
------------|--------|---------|------------------------------------------
none        | Fast   | None    | Lab environments, testing
low         | Fast   | Minimal | Internal networks, low risk
normal      | Medium | Medium  | Default. Most external recon
aggressive  | Slow   | High    | Red team, targets with IDS
paranoid    | Very slow| Max   | Bug bounties, Tor required


┌───────────────────────────────────────────────────────────────────────────────┐
│ TOR SETUP FOR PARANOID MODE                                                   │
└───────────────────────────────────────────────────────────────────────────────┘

# Install Tor
sudo pacman -S tor

# Start Tor service
sudo systemctl start tor
sudo systemctl enable tor

# Verify Tor is running (listening on 127.0.0.1:9050)
sudo netstat -tlnp | grep 9050

# Run ORION_EYE with paranoid evasion
sudo python3 main.py -t target.com -e paranoid --proxy socks5://127.0.0.1:9050


┌───────────────────────────────────────────────────────────────────────────────┐
│ WHAT ORION_EYE DOES (9 PHASES)                                                │
└───────────────────────────────────────────────────────────────────────────────┘

Phase 1: OSINT          → Emails, usernames, public data
Phase 2: DNS Recon      → Subdomains, zone transfers
Phase 3: Port Scanning  → Masscan + Nmap with evasion
Phase 4: NSE Scripts    → Vulnerability detection
Phase 5: Web Enum       → Directories, tech stack
Phase 6: JS Analysis    → API keys, passwords in JavaScript
Phase 7: Vuln Scanning  → SQLmap, searchsploit
Phase 8: Harvesting     → Exposed config files, emails
Phase 9: Database       → DB port scans, NoSQLMap

Total time: 30-90 minutes depending on evasion level


┌───────────────────────────────────────────────────────────────────────────────┐
│ OUTPUT FILES                                                                  │
└───────────────────────────────────────────────────────────────────────────────┘

After scan completes, open the report:
firefox ./orion_results/reports/orion_report.html

All raw outputs saved in:
./orion_results/
├── osint/          # theHarvester, recon-ng, maigret
├── dns/            # Subdomains, zone transfer results
├── port_scanning/  # Masscan, Nmap scans
├── nse/            # NSE vulnerability findings
├── web_enum/       # Gobuster, nikto, whatweb
├── javascript/     # Downloaded JS files + secrets
├── vulnerabilities/# SQLmap, searchsploit
├── harvesting/     # Emails, exposed configs
├── database/       # DB port scans
├── metasploit/     # (if -m used)
├── reports/        # HTML report + JSON summary
└── logs/           # Full execution log


┌───────────────────────────────────────────────────────────────────────────────┐
│ INSTALL ALL DEPENDENCIES (One Command)                                        │
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
EOF


┌───────────────────────────────────────────────────────────────────────────────┐
│ TEST THE INSTALLATION                                                         │
└───────────────────────────────────────────────────────────────────────────────┘

# Quick test (2-3 minutes)
sudo python3 main.py -t scanme.nmap.org -e low -o ./quick_test

# Full test with all features (30 minutes)
sudo python3 main.py -t scanme.nmap.org -e normal -m -o ./full_test

# Production scan
sudo python3 main.py -t YOUR_TARGET.com -e aggressive -m --threads 15 -o ./production_scan


┌───────────────────────────────────────────────────────────────────────────────┐
│ TROUBLESHOOTING                                                               │
└───────────────────────────────────────────────────────────────────────────────┘

"Permission denied"           → Run with sudo
"Command not found: toolname" → Install missing tool: sudo pacman -S toolname
Script hangs on sqlmap        → Ctrl+C, results save up to that point
No open ports found           → Target may be down. Try -e none
Metasploit no output          → Script auto-skips if msfconsole missing

# Check the log file if something breaks
cat ./orion_results/logs/*.log | tail -50


┌───────────────────────────────────────────────────────────────────────────────┐
│ QUICK REFERENCE CARD                                                          │
└───────────────────────────────────────────────────────────────────────────────┘

# Fastest (least stealth)
sudo python3 main.py -t target.com -e none

# Standard (balanced)
sudo python3 main.py -t target.com

# Stealth (harder to detect)
sudo python3 main.py -t target.com -e aggressive -m

# Maximum stealth (very slow, use Tor)
sudo systemctl start tor
sudo python3 main.py -t target.com -e paranoid --threads 3

# Verbose debugging
sudo python3 main.py -t target.com -v -o ./debug_scan


┌───────────────────────────────────────────────────────────────────────────────┐
│ PROJECT STRUCTURE                                                             │
└───────────────────────────────────────────────────────────────────────────────┘

ORION_EYE/
├── main.py              # Main script
├── README.md            # Documentation
├── requirements.txt     # Dependencies list
└── /output_directory/   # Created per scan (default: orion_results)


┌───────────────────────────────────────────────────────────────────────────────┐
│ EXAMPLE OUTPUT                                                                │
└───────────────────────────────────────────────────────────────────────────────┘

$ sudo python3 main.py -t scanme.nmap.org -e normal -o ./scan_results

[11:15:32] [SUCCESS] 🔍 PHASE 1: OSINT RECONNAISSANCE
[11:15:35] [SUCCESS] ✓ theHarvester completed
[11:15:42] [SUCCESS] ✓ Found 3 subdomains
[11:16:10] [SUCCESS] ✓ Found 6 open ports
[11:18:45] [SUCCESS] ✓ NSE completed with 2 findings
[11:22:30] [SUCCESS] ✅ Report saved: ./scan_results/reports/orion_report.html

════════════════════════════════════════════════════════════
✅ ORION_EYE RECON COMPLETE! Report: ./scan_results/reports/orion_report.html
════════════════════════════════════════════════════════════

$ firefox ./scan_results/reports/orion_report.html

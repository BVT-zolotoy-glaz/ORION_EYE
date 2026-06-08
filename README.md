# ORION_EYE
SHΔDØW RECON V2 - BlackArch recon framework with NSE evasion, JS secret harvesting, and HTML reporting. Orchestrates 20+ tools. 9 phases. Configurable stealth. Saves everything. Optional Metasploit.


╔═══════════════════════════════════════════════════════════════════════════════╗
║                    SHΔDØW RECON V2 - USAGE GUIDE                              ║
║                      How to run the script, not the tools                     ║
╚═══════════════════════════════════════════════════════════════════════════════╝

┌───────────────────────────────────────────────────────────────────────────────┐
│ QUICK START                                                                   │
└───────────────────────────────────────────────────────────────────────────────┘

# Save the script
nano shadow_recon_v2.py
# (paste the full script)
chmod +x shadow_recon_v2.py

# Basic scan
sudo python3 shadow_recon_v2.py -t target.com -o ./results

# Done. Wait for report.


┌───────────────────────────────────────────────────────────────────────────────┐
│ ALL COMMAND OPTIONS                                                           │
└───────────────────────────────────────────────────────────────────────────────┘

REQUIRED:
  -t, --target    Target domain or IP address

OPTIONAL:
  -o, --output    Output directory (default: ./recon_results)
  -e, --evasion   Evasion level: none, low, normal, aggressive, paranoid (default: normal)
  -m, --metasploit  Enable Metasploit modules (opt-in)
  --threads       Number of threads (default: 10)
  -v, --verbose   Show detailed command output


┌───────────────────────────────────────────────────────────────────────────────┐
│ USAGE EXAMPLES                                                                │
└───────────────────────────────────────────────────────────────────────────────┘

# Minimal (normal evasion, no Metasploit)
sudo python3 shadow_recon_v2.py -t example.com

# Custom output directory
sudo python3 shadow_recon_v2.py -t example.com -o ./my_scan_results

# Aggressive evasion (stealthier, slower)
sudo python3 shadow_recon_v2.py -t example.com -e aggressive

# With Metasploit modules
sudo python3 shadow_recon_v2.py -t example.com -m

# Paranoid evasion + Tor (max stealth)
sudo systemctl start tor
sudo python3 shadow_recon_v2.py -t example.com -e paranoid --threads 5

# Verbose (see every command being run)
sudo python3 shadow_recon_v2.py -t example.com -v

# Full power (aggressive evasion + Metasploit + 20 threads)
sudo python3 shadow_recon_v2.py -t example.com -e aggressive -m --threads 20 -o ./deep_scan


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

# Run script with paranoid evasion
sudo python3 shadow_recon_v2.py -t target.com -e paranoid --proxy socks5://127.0.0.1:9050


┌───────────────────────────────────────────────────────────────────────────────┐
│ WHAT THE SCRIPT DOES (9 PHASES)                                               │
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
firefox ./results/reports/shadow_recon_report.html

All raw outputs saved in:
./results/
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
│ TROUBLESHOOTING                                                               │
└───────────────────────────────────────────────────────────────────────────────┘

"Permission denied"           → Run with sudo
"Command not found: toolname" → Install missing tool: sudo pacman -S toolname
Script hangs on sqlmap        → Ctrl+C, results save up to that point
No open ports found           → Target may be down. Try -e none
Metasploit no output          → Script auto-skips if msfconsole missing


┌───────────────────────────────────────────────────────────────────────────────┐
│ QUICK REFERENCE                                                               │
└───────────────────────────────────────────────────────────────────────────────┘

# Fastest (least stealth)
sudo python3 shadow_recon_v2.py -t target.com -e none

# Standard (balanced)
sudo python3 shadow_recon_v2.py -t target.com

# Stealth (harder to detect)
sudo python3 shadow_recon_v2.py -t target.com -e aggressive -m

# Maximum stealth (very slow, use Tor)
sudo systemctl start tor
sudo python3 shadow_recon_v2.py -t target.com -e paranoid --threads 3

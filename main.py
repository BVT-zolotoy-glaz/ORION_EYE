#!/usr/bin/env python3
"""
SHΔDØW RECON V2.0 - BlackArch Advanced Recon Framework
Changes: Advanced NSE with evasion, optional Metasploit, full result persistence
Author: ENI (for LO)
"""

import os
import sys
import json
import time
import subprocess
import argparse
import datetime
import concurrent.futures
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import re

# ============ CONFIGURATION ============
SCRIPT_VERSION = "2.0"
SCRIPT_NAME = "SHΔDØW RECON V2"

# Color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
PURPLE = '\033[95m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

class ShadowReconV2:
    """Advanced recon framework with NSE evasion and optional Metasploit"""
    
    def __init__(self, target: str, output_dir: str, evasion_level: str = "normal", 
                 proxy: str = None, threads: int = 10, verbose: bool = False,
                 enable_metasploit: bool = False):
        self.target = target
        self.output_dir = Path(output_dir)
        self.evasion_level = evasion_level
        self.proxy = proxy
        self.threads = threads
        self.verbose = verbose
        self.enable_metasploit = enable_metasploit
        self.start_time = datetime.datetime.now()
        self.results = {
            "metadata": {
                "target": target,
                "start_time": self.start_time.isoformat(),
                "evasion_level": evasion_level,
                "script_version": SCRIPT_VERSION,
                "metasploit_enabled": enable_metasploit
            },
            "osint": {},
            "dns": {},
            "port_scanning": {},
            "nse_results": {},
            "web_enum": {},
            "vulnerabilities": {},
            "javascript_secrets": {},
            "database_findings": {},
            "harvesting": {},
            "metasploit_results": {} if enable_metasploit else None
        }
        
        self._create_directories()
        
    def _create_directories(self):
        """Create organized output directory structure"""
        dirs = [
            "logs", "osint", "dns", "port_scanning", "nse", "web_enum",
            "vulnerabilities", "javascript", "database", "harvesting", "reports"
        ]
        if self.enable_metasploit:
            dirs.append("metasploit")
        
        for d in dirs:
            (self.output_dir / d).mkdir(parents=True, exist_ok=True)
            
        self.log_file = self.output_dir / "logs" / f"recon_{self.start_time.strftime('%Y%m%d_%H%M%S')}.log"
        
    def log(self, message: str, level: str = "INFO"):
        """Log messages with colors"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        
        if level == "ERROR":
            print(f"{RED}{log_entry}{RESET}")
        elif level == "SUCCESS":
            print(f"{GREEN}{log_entry}{RESET}")
        elif level == "WARNING":
            print(f"{YELLOW}{log_entry}{RESET}")
        elif level == "DEBUG" and self.verbose:
            print(f"{CYAN}{log_entry}{RESET}")
        else:
            print(f"{BLUE}{log_entry}{RESET}")
            
        with open(self.log_file, 'a') as f:
            f.write(log_entry + "\n")
    
    def _get_nmap_evasion_flags(self) -> List[str]:
        """Return Nmap evasion flags based on configured level"""
        base_flags = []
        
        if self.evasion_level == "low":
            base_flags = ["-T4", "--max-retries", "2"]
        elif self.evasion_level == "normal":
            base_flags = ["-T3", "-f", "--mtu", "24", "--data-length", "200", 
                         "--max-retries", "3", "--scan-delay", "1s", "--randomize-hosts"]
        elif self.evasion_level == "aggressive":
            base_flags = ["-T2", "-f", "--mtu", "16", "--data-length", "300", 
                         "--max-retries", "5", "--scan-delay", "2s", "--badsum", 
                         "--randomize-hosts", "--source-port", "53"]
        elif self.evasion_level == "paranoid":
            base_flags = ["-T1", "-f", "--mtu", "8", "--data-length", "500", 
                         "--max-retries", "10", "--scan-delay", "5s", "--badsum", 
                         "--randomize-hosts", "--source-port", "53"]
            if self.proxy:
                base_flags.extend(["--proxies", self.proxy])
        
        # Common stealth flags for all levels above none
        if self.evasion_level != "none":
            base_flags.extend(["--max-scan-delay", "100ms", "--min-parallelism", "1"])
        
        return base_flags
    
    def _run_command(self, cmd: List[str], timeout: int = 300, save_output: Optional[str] = None) -> Tuple[str, str, int]:
        """Execute command and optionally save output"""
        try:
            if self.verbose:
                self.log(f"Running: {' '.join(cmd)}", "DEBUG")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                env={**os.environ, "PYTHONUNBUFFERED": "1"}
            )
            
            if save_output:
                with open(save_output, 'w') as f:
                    f.write(result.stdout)
                    if result.stderr:
                        f.write("\n--- STDERR ---\n")
                        f.write(result.stderr)
            
            return result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired:
            self.log(f"Command timed out after {timeout}s", "WARNING")
            return "", f"TIMEOUT after {timeout}s", -1
        except Exception as e:
            self.log(f"Command failed: {e}", "ERROR")
            return "", str(e), -2
    
    def _save_json(self, data: dict, category: str, filename: str):
        """Save JSON data to category directory"""
        filepath = self.output_dir / category / filename
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return str(filepath)
    
    # ============ PHASE 1: OSINT ============
    def phase_osint(self):
        """Perform OSINT gathering"""
        self.log(f"{BOLD}🔍 PHASE 1: OSINT RECONNAISSANCE{RESET}", "SUCCESS")
        
        osint_results = {}
        
        # theHarvester
        self.log("Running theHarvester...")
        harv_output = self.output_dir / "osint" / "theharvester_output.txt"
        cmd = ["theHarvester", "-d", self.target, "-b", "all", "-f", str(harv_output)]
        stdout, stderr, code = self._run_command(cmd, timeout=180)
        if code == 0:
            with open(harv_output, 'r') as f:
                content = f.read()
            osint_results["theHarvester"] = content[:5000]
            self.log("✓ theHarvester completed", "SUCCESS")
        
        # recon-ng
        self.log("Running recon-ng...")
        recon_script = self.output_dir / "osint" / "recon_commands.rc"
        with open(recon_script, 'w') as f:
            f.write(f"""
workspaces create {self.target.replace('.', '_')}
workspaces select {self.target.replace('.', '_')}
modules load recon/domains-hosts/hackertarget
options set SOURCE {self.target}
run
modules load recon/domains-hosts/bing_domain_web
options set SOURCE {self.target}
run
exit
""")
        recon_output = self.output_dir / "osint" / "recon_ng_output.txt"
        cmd = ["recon-ng", "-r", str(recon_script)]
        stdout, stderr, code = self._run_command(cmd, timeout=180, save_output=str(recon_output))
        osint_results["recon_ng"] = "Completed" if code == 0 else "Failed"
        
        # maigret
        self.log("Running maigret...")
        maigret_output = self.output_dir / "osint" / "maigret_results.json"
        cmd = ["maigret", self.target, "--output", str(maigret_output)]
        stdout, stderr, code = self._run_command(cmd, timeout=120)
        if maigret_output.exists():
            with open(maigret_output, 'r') as f:
                osint_results["maigret"] = f.read()[:2000]
        
        self.results["osint"] = osint_results
        self._save_json(osint_results, "osint", "osint_summary.json")
        
    # ============ PHASE 2: DNS RECON ============
    def phase_dns_recon(self):
        """Perform DNS enumeration"""
        self.log(f"{BOLD}🌐 PHASE 2: DNS RECONNAISSANCE{RESET}", "SUCCESS")
        
        dns_results = {}
        
        # dnsrecon
        self.log("Running dnsrecon...")
        dnsrecon_output = self.output_dir / "dns" / "dnsrecon.json"
        cmd = ["dnsrecon", "-d", self.target, "-t", "std", "-j", str(dnsrecon_output)]
        stdout, stderr, code = self._run_command(cmd, timeout=180)
        if dnsrecon_output.exists():
            with open(dnsrecon_output, 'r') as f:
                dns_results["dnsrecon"] = f.read()[:3000]
        
        # sublist3r
        self.log("Running sublist3r...")
        sublist3r_output = self.output_dir / "dns" / "sublist3r_output.txt"
        cmd = ["sublist3r", "-d", self.target, "-o", str(sublist3r_output)]
        stdout, stderr, code = self._run_command(cmd, timeout=120)
        if sublist3r_output.exists():
            with open(sublist3r_output, 'r') as f:
                subdomains = f.read()
                dns_results["subdomains"] = subdomains
                sub_count = len([l for l in subdomains.split('\n') if l.strip()])
                self.log(f"✓ Found {sub_count} subdomains", "SUCCESS")
        
        # zone transfer test
        self.log("Testing for DNS zone transfers...")
        cmd = ["dnsrecon", "-d", self.target, "-t", "axfr"]
        stdout, stderr, code = self._run_command(cmd, timeout=60)
        if "SUCCESS" in stdout and "AXFR" in stdout:
            dns_results["zone_transfer"] = "VULNERABLE"
            self.log("⚠️ ZONE TRANSFER VULNERABLE!", "WARNING")
        else:
            dns_results["zone_transfer"] = "Not vulnerable"
        
        self.results["dns"] = dns_results
        self._save_json(dns_results, "dns", "dns_summary.json")
        
    # ============ PHASE 3: PORT SCANNING + ADVANCED NSE ============
    def phase_port_scanning_and_nse(self):
        """Advanced port scanning with NSE scripts and evasion"""
        self.log(f"{BOLD}🔌 PHASE 3: PORT SCANNING + NSE (EVASION: {self.evasion_level.upper()}){RESET}", "SUCCESS")
        
        scan_results = {}
        nse_results = {}
        
        # Masscan for fast port discovery
        self.log("Running masscan (fast port discovery)...")
        masscan_output = self.output_dir / "port_scanning" / "masscan_output.gnmap"
        cmd = ["masscan", self.target, "-p1-65535", "--rate=1000", "-oG", str(masscan_output)]
        stdout, stderr, code = self._run_command(cmd, timeout=300)
        
        # Parse open ports
        open_ports = []
        if masscan_output.exists():
            with open(masscan_output, 'r') as f:
                for line in f:
                    if "open" in line:
                        parts = line.split()
                        for part in parts:
                            if "/open/" in part:
                                port = part.split('/')[0]
                                open_ports.append(port)
        
        scan_results["masscan"] = {
            "open_ports_found": open_ports,
            "port_count": len(open_ports)
        }
        self.log(f"✓ Found {len(open_ports)} open ports", "SUCCESS")
        
        if not open_ports:
            self.log("No open ports found, skipping NSE", "WARNING")
            self.results["port_scanning"] = scan_results
            return []
        
        # Deep Nmap with service detection
        port_list = ",".join(open_ports[:100])
        nmap_flags = self._get_nmap_evasion_flags()
        
        self.log(f"Running detailed Nmap scan with {len(open_ports[:100])} ports...")
        nmap_output_base = self.output_dir / "port_scanning" / "nmap_detailed"
        cmd = ["nmap", "-sS", "-sV", "-sC", "-O", "-p", port_list, self.target,
               "-oA", str(nmap_output_base)]
        cmd.extend(nmap_flags)
        
        stdout, stderr, code = self._run_command(cmd, timeout=600)
        scan_results["nmap_detailed"] = "Completed" if (code == 0 or code == 1) else "Failed"
        
        # Parse services for NSE targeting
        services = []
        nse_services_output = self.output_dir / "port_scanning" / "nmap_services.txt"
        if nmap_output_base.with_suffix(".nmap").exists():
            with open(nmap_output_base.with_suffix(".nmap"), 'r') as f:
                content = f.read()
                for line in content.split('\n'):
                    if "/tcp" in line and "open" in line:
                        services.append(line.strip())
        
        scan_results["services_detected"] = services[:50]
        self.results["port_scanning"] = scan_results
        self._save_json(scan_results, "port_scanning", "port_scan_summary.json")
        
        # ============ ADVANCED NSE WITH EVASION ============
        self.log(f"{BOLD}📜 PHASE 3B: ADVANCED NSE SCRIPT EXECUTION{RESET}", "SUCCESS")
        
        # Categorize NSE scripts to run based on open ports
        nse_categories = {
            "vuln": ["vuln", "exploit"],
            "discovery": ["smb-enum-shares", "smb-os-discovery", "http-enum", "dns-zone-transfer"],
            "brute": ["ssh-brute", "http-brute", "mysql-brute", "ftp-brute"],
            "malware": ["http-malware-host", "clamav-exec"],
            "dos": ["smb-flood", "http-slowloris-check"],
        }
        
        # Select scripts based on open ports
        selected_scripts = []
        port_str = ",".join(open_ports[:50])
        
        # Check for common service ports
        if any(p in ["80", "443", "8080", "8443"] for p in open_ports):
            selected_scripts.extend(["http-vuln-*", "http-sql-injection", "http-xss", 
                                     "http-csrf", "http-enum", "http-headers"])
        if any(p in ["22"] for p in open_ports):
            selected_scripts.extend(["ssh-auth-methods", "ssh-hostkey", "ssh2-enum-algos"])
        if any(p in ["445", "139"] for p in open_ports):
            selected_scripts.extend(["smb-vuln-*", "smb-enum-shares", "smb-os-discovery"])
        if any(p in ["3306"] for p in open_ports):
            selected_scripts.extend(["mysql-enum", "mysql-vuln-cve2012-2122"])
        if any(p in ["5432"] for p in open_ports):
            selected_scripts.extend(["pgsql-brute"])
        if any(p in ["27017"] for p in open_ports):
            selected_scripts.extend(["mongodb-databases", "mongodb-info"])
        if any(p in ["6379"] for p in open_ports):
            selected_scripts.extend(["redis-info"])
        
        # Always run general vulnerability scripts
        selected_scripts.append("vuln")
        
        # Build NSE command with evasion
        script_arg = ",".join(selected_scripts[:15])  # Limit to 15 to avoid timeout
        
        # Evasion techniques for NSE:
        # - --script-trace for debugging (disabled unless verbose)
        # - --max-parallelism 1 to avoid flooding
        # - --script-args http.useragent="random" to blend in
        nse_evasion_args = [
            "--script", script_arg,
            "--script-args", "http.useragent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',unsafe=1",
            "--max-parallelism", "1",
            "--min-hostgroup", "1"
        ]
        
        if self.evasion_level in ["aggressive", "paranoid"]:
            nse_evasion_args.extend(["--script-timeout", "60s", "--host-timeout", "120s"])
        
        nse_output = self.output_dir / "nse" / "nse_results.nmap"
        cmd = ["nmap", "-p", port_str, self.target] + nse_evasion_args + ["-oN", str(nse_output)]
        cmd.extend(self._get_nmap_evasion_flags())
        
        self.log(f"Running NSE scripts: {script_arg[:100]}...")
        stdout, stderr, code = self._run_command(cmd, timeout=900)  # 15 minutes for NSE
        
        # Parse NSE results
        if nse_output.exists():
            with open(nse_output, 'r') as f:
                nse_content = f.read()
            
            # Extract vulnerabilities
            vuln_patterns = [
                (r"VULNERABLE", "Generic vulnerability"),
                (r"SQL injection", "SQL injection possible"),
                (r"XSS", "Cross-site scripting"),
                (r"CSRF", "Cross-site request forgery"),
                (r"Remote code execution", "RCE possible"),
                (r"Buffer overflow", "Buffer overflow"),
                (r"Authentication bypass", "Auth bypass"),
                (r"Default credentials", "Default creds found"),
            ]
            
            extracted_vulns = []
            for pattern, desc in vuln_patterns:
                if re.search(pattern, nse_content, re.IGNORECASE):
                    extracted_vulns.append(desc)
                    self.log(f"⚠️ NSE found: {desc}", "WARNING")
            
            nse_results = {
                "scripts_executed": selected_scripts[:15],
                "output_summary": nse_content[:10000],
                "vulnerabilities_found": extracted_vulns,
                "full_output_file": str(nse_output)
            }
            
            # Save parsed results
            self._save_json(nse_results, "nse", "nse_parsed.json")
            self.log(f"✓ NSE completed with {len(extracted_vulns)} findings", "SUCCESS")
        
        self.results["nse_results"] = nse_results
        return open_ports
    
    # ============ PHASE 4: WEB ENUMERATION ============
    def phase_web_enumeration(self):
        """Enumerate web applications"""
        self.log(f"{BOLD}🌊 PHASE 4: WEB ENUMERATION{RESET}", "SUCCESS")
        
        web_results = {}
        urls = [f"http://{self.target}", f"https://{self.target}"]
        
        # Gobuster
        self.log("Running gobuster...")
        for url in urls:
            output_file = self.output_dir / "web_enum" / f"gobuster_{url.split('://')[1]}.txt"
            cmd = ["gobuster", "dir", "-u", url, "-w", "/usr/share/wordlists/dirb/common.txt",
                   "-o", str(output_file), "-t", str(self.threads)]
            if self.evasion_level in ["aggressive", "paranoid"]:
                cmd.extend(["--delay", "500ms", "--random-user-agent", "--no-error"])
            stdout, stderr, code = self._run_command(cmd, timeout=300)
            if output_file.exists():
                with open(output_file, 'r') as f:
                    web_results[f"gobuster_{url}"] = f.read()[:5000]
        
        # Nikto
        self.log("Running nikto...")
        nikto_output = self.output_dir / "web_enum" / "nikto_report.html"
        cmd = ["nikto", "-h", f"https://{self.target}", "-Format", "html", "-o", str(nikto_output)]
        stdout, stderr, code = self._run_command(cmd, timeout=300)
        web_results["nikto"] = "Report generated" if code == 0 else "Failed"
        
        # WhatWeb
        self.log("Running whatweb...")
        whatweb_output = self.output_dir / "web_enum" / "whatweb_output.txt"
        cmd = ["whatweb", f"https://{self.target}", "--log-verbose", str(whatweb_output)]
        stdout, stderr, code = self._run_command(cmd, timeout=60)
        if whatweb_output.exists():
            with open(whatweb_output, 'r') as f:
                web_results["technologies"] = f.read()[:2000]
        
        self.results["web_enum"] = web_results
        self._save_json(web_results, "web_enum", "web_enum_summary.json")
        
    # ============ PHASE 5: JAVASCRIPT DEEP ANALYSIS ============
    def phase_javascript_analysis(self):
        """Extract and analyze JS files for secrets"""
        self.log(f"{BOLD}📜 PHASE 5: JAVASCRIPT SECRETS{RESET}", "SUCCESS")
        
        js_results = {"files_found": [], "secrets": []}
        
        # Find JS files via crawling
        self.log("Discovering JavaScript files...")
        wget_log = self.output_dir / "javascript" / "wget_spider.log"
        cmd = ["wget", "--spider", "--force-html", "-r", "-l", "2", f"https://{self.target}",
               "-o", str(wget_log), "--no-verbose"]
        stdout, stderr, code = self._run_command(cmd, timeout=180)
        
        js_urls = []
        if wget_log.exists():
            with open(wget_log, 'r') as f:
                for line in f:
                    if '.js' in line and 'https://' in line:
                        js_url = line.split(' ')[-1].strip()
                        if js_url not in js_urls:
                            js_urls.append(js_url)
        
        js_results["files_found"] = js_urls
        self.log(f"✓ Found {len(js_urls)} JS files", "SUCCESS")
        
        # Secret patterns
        patterns = {
            "API_KEY": r'[A-Za-z0-9]{32,}',
            "GOOGLE_API": r'AIza[0-9A-Za-z\-_]{35}',
            "OPENAI_KEY": r'sk-[A-Za-z0-9]{48}',
            "AWS_KEY": r'AKIA[0-9A-Z]{16}',
            "PRIVATE_KEY": r'-----BEGIN RSA PRIVATE KEY-----',
            "PASSWORD": r'password["\']?\s*[:=]\s*["\'][^\'"]+',
            "TOKEN": r'token["\']?\s*[:=]\s*["\'][A-Za-z0-9]+',
            "SECRET": r'secret["\']?\s*[:=]\s*["\'][^\'"]+',
        }
        
        secrets_found = []
        for js_url in js_urls[:20]:
            js_file = self.output_dir / "javascript" / f"js_{abs(hash(js_url))}.js"
            cmd = ["curl", "-s", js_url, "-o", str(js_file)]
            self._run_command(cmd, timeout=30)
            
            if js_file.exists():
                content = js_file.read_text()
                for name, pattern in patterns.items():
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        if len(match) > 8:
                            secrets_found.append({
                                "file": js_url,
                                "type": name,
                                "match": match[:100]
                            })
        
        js_results["secrets"] = secrets_found
        self.results["javascript_secrets"] = js_results
        self._save_json(js_results, "javascript", "js_secrets.json")
        
        if secrets_found:
            self.log(f"⚠️ Found {len(secrets_found)} potential secrets!", "WARNING")
        
    # ============ PHASE 6: VULNERABILITY SCANNING ============
    def phase_vulnerability_scanning(self):
        """SQLMap and other vuln scanners"""
        self.log(f"{BOLD}💣 PHASE 6: VULNERABILITY SCANNING{RESET}", "SUCCESS")
        
        vuln_results = {}
        
        # SQLMap
        self.log("Running sqlmap...")
        sqlmap_output = self.output_dir / "vulnerabilities" / "sqlmap_output.txt"
        cmd = ["sqlmap", "-u", f"https://{self.target}", "--batch", "--crawl=2",
               "--output-dir", str(self.output_dir / "vulnerabilities" / "sqlmap")]
        
        if self.evasion_level in ["aggressive", "paranoid"]:
            cmd.extend(["--random-agent", "--delay=2", "--time-sec=3", "--flush-session"])
        if self.evasion_level == "paranoid":
            cmd.extend(["--tor", "--tor-type=SOCKS5", "--check-tor"])
        
        stdout, stderr, code = self._run_command(cmd, timeout=600, save_output=str(sqlmap_output))
        
        if sqlmap_output.exists():
            with open(sqlmap_output, 'r') as f:
                content = f.read()
                vuln_results["sqlmap"] = content[:5000]
                if "vulnerable" in content.lower():
                    vuln_results["sql_injection"] = True
                    self.log("⚠️ SQL INJECTION DETECTED!", "WARNING")
        
        # Searchsploit
        self.log("Running searchsploit...")
        services = self.results.get("port_scanning", {}).get("services_detected", [])
        exploit_results = {}
        
        for service in services[:10]:
            parts = service.split()
            if len(parts) > 2:
                svc_name = parts[2].split('/')[0] if '/' in parts[2] else parts[2]
                svc_output = self.output_dir / "vulnerabilities" / f"exploits_{svc_name}.txt"
                cmd = ["searchsploit", svc_name, "--json"]
                stdout, stderr, code = self._run_command(cmd, timeout=30, save_output=str(svc_output))
                if stdout:
                    exploit_results[svc_name] = stdout[:1000]
        
        vuln_results["exploits"] = exploit_results
        self.results["vulnerabilities"] = vuln_results
        self._save_json(vuln_results, "vulnerabilities", "vulnerability_summary.json")
        
    # ============ PHASE 7: METASPLOIT (OPTIONAL - ONLY IF SAVING WORKS) ============
    def phase_metasploit(self):
        """Optional Metasploit recon - only runs if results saving is confirmed"""
        if not self.enable_metasploit:
            self.log("Metasploit phase disabled (use -m to enable)", "INFO")
            return
        
        self.log(f"{BOLD}🎯 PHASE 7: METASPLOIT RECON (OPTIONAL){RESET}", "SUCCESS")
        
        # These aux modules save results reliably via the -o flag
        reliable_modules = [
            ("auxiliary/scanner/portscan/tcp", "portscan"),
            ("auxiliary/scanner/http/dir_scanner", "http_dir"),
            ("auxiliary/scanner/http/options", "http_options"),
            ("auxiliary/scanner/smb/smb_version", "smb_version"),
            ("auxiliary/scanner/ssh/ssh_version", "ssh_version"),
        ]
        
        msf_results = {}
        
        for module, name in reliable_modules:
            self.log(f"Running Metasploit module: {module}")
            rc_script = self.output_dir / "metasploit" / f"{name}.rc"
            output_file = self.output_dir / "metasploit" / f"{name}_output.txt"
            
            with open(rc_script, 'w') as f:
                f.write(f"""
use {module}
set RHOSTS {self.target}
set VERBOSE false
run
exit -y
""")
            
            cmd = ["msfconsole", "-q", "-r", str(rc_script), "-o", str(output_file)]
            stdout, stderr, code = self._run_command(cmd, timeout=180)
            
            if output_file.exists() and output_file.stat().st_size > 100:
                with open(output_file, 'r') as f:
                    content = f.read()
                    msf_results[name] = content[:2000] if "[*]" in content else "No findings"
                self.log(f"✓ {name} completed", "SUCCESS")
            else:
                msf_results[name] = "No output generated"
        
        self.results["metasploit_results"] = msf_results
        self._save_json(msf_results, "metasploit", "metasploit_summary.json")
        
    # ============ PHASE 8: DEEP HARVESTING ============
    def phase_deep_harvesting(self):
        """Email and exposed file harvesting"""
        self.log(f"{BOLD}🌾 PHASE 8: DEEP HARVESTING{RESET}", "SUCCESS")
        
        harvest_results = {"emails": [], "exposed_files": []}
        
        # Email harvesting
        self.log("Harvesting emails...")
        cmd = ["theHarvester", "-d", self.target, "-b", "google,bing", "-l", "300"]
        stdout, stderr, code = self._run_command(cmd, timeout=180)
        
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', stdout)
        harvest_results["emails"] = list(set(emails))
        self.log(f"✓ Found {len(harvest_results['emails'])} unique emails", "SUCCESS")
        
        # Check for exposed config files
        common_paths = [
            "/.env", "/.git/config", "/wp-config.php", "/config.php",
            "/application/configs/database.ini", "/.aws/credentials",
            "/backup.sql", "/dump.sql", "/phpinfo.php", "/robots.txt"
        ]
        
        self.log("Checking for exposed files...")
        for path in common_paths:
            for proto in ["https", "http"]:
                url = f"{proto}://{self.target}{path}"
                cmd = ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", url, "--max-time", "5"]
                stdout, stderr, code = self._run_command(cmd, timeout=10)
                if stdout.strip() == "200":
                    harvest_results["exposed_files"].append(url)
                    self.log(f"⚠️ EXPOSED: {url}", "WARNING")
                    
                    # Download the exposed file
                    dl_file = self.output_dir / "harvesting" / f"exposed_{path.replace('/', '_')}.txt"
                    cmd = ["curl", "-s", url, "-o", str(dl_file), "--max-time", "10"]
                    self._run_command(cmd, timeout=15)
        
        self.results["harvesting"] = harvest_results
        self._save_json(harvest_results, "harvesting", "harvesting_summary.json")
        
    # ============ PHASE 9: DATABASE TESTING ============
    def phase_database_testing(self):
        """Test database exposure"""
        self.log(f"{BOLD}🗄️ PHASE 9: DATABASE TESTING{RESET}", "SUCCESS")
        
        db_results = {}
        db_ports = {"MySQL": 3306, "PostgreSQL": 5432, "MongoDB": 27017, "Redis": 6379}
        
        # Check DB ports
        port_list = ",".join(str(p) for p in db_ports.values())
        db_output = self.output_dir / "database" / "db_port_scan.txt"
        cmd = ["nmap", "-p", port_list, self.target, "-sV", "-oN", str(db_output)]
        stdout, stderr, code = self._run_command(cmd, timeout=120)
        
        open_dbs = []
        if db_output.exists():
            with open(db_output, 'r') as f:
                content = f.read()
                for db_name, port in db_ports.items():
                    if f"{port}/open" in content:
                        open_dbs.append(db_name)
                        self.log(f"⚠️ Exposed: {db_name} on port {port}", "WARNING")
        
        db_results["exposed_databases"] = open_dbs
        
        # NoSQLMap if MongoDB exposed
        if "MongoDB" in open_dbs:
            self.log("Running NoSQLMap...")
            nosql_output = self.output_dir / "database" / "nosqlmap_results.txt"
            cmd = ["nosqlmap", "--host", self.target, "--port", "27017", "--output", str(nosql_output)]
            stdout, stderr, code = self._run_command(cmd, timeout=180)
            if nosql_output.exists():
                with open(nosql_output, 'r') as f:
                    db_results["nosqlmap"] = f.read()[:2000]
        
        self.results["database_findings"] = db_results
        self._save_json(db_results, "database", "database_summary.json")
        
    # ============ FINAL: HTML REPORT ============
    def generate_html_report(self):
        """Generate comprehensive HTML report"""
        self.log(f"{BOLD}📊 FINAL PHASE: GENERATING HTML REPORT{RESET}", "SUCCESS")
        
        # Compile critical findings
        critical = []
        warnings = []
        
        if self.results.get("dns", {}).get("zone_transfer") == "VULNERABLE":
            critical.append("DNS zone transfer vulnerability")
        if self.results.get("vulnerabilities", {}).get("sql_injection"):
            critical.append("SQL injection vulnerability")
        if self.results.get("nse_results", {}).get("vulnerabilities_found"):
            critical.extend(self.results["nse_results"]["vulnerabilities_found"])
        if self.results.get("harvesting", {}).get("exposed_files"):
            warnings.extend(self.results["harvesting"]["exposed_files"])
        if self.results.get("javascript_secrets", {}).get("secrets"):
            warnings.append(f"{len(self.results['javascript_secrets']['secrets'])} secrets in JS files")
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SHΔDØW RECON V2 - Security Report</title>
    <style>
        body {{ font-family: 'Courier New', monospace; background: #0a0a0a; color: #e0e0e0; padding: 20px; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: #111; border: 1px solid #2a2a2a; border-radius: 8px; }}
        .header {{ background: linear-gradient(135deg, #1a1a2e, #16213e); padding: 40px; text-align: center; border-bottom: 2px solid #ff3366; }}
        .header h1 {{ color: #ff3366; font-size: 2.5rem; }}
        .scan-info {{ background: #1a1a1a; padding: 20px 40px; display: flex; gap: 40px; flex-wrap: wrap; }}
        .section {{ padding: 30px 40px; border-bottom: 1px solid #2a2a2a; }}
        .section h2 {{ color: #ff3366; border-left: 4px solid #ff3366; padding-left: 15px; margin-bottom: 20px; }}
        .finding-critical {{ background: #1a0000; border-left: 3px solid #ff0000; padding: 15px; margin: 10px 0; }}
        .finding-warning {{ background: #1a1a00; border-left: 3px solid #ffaa00; padding: 15px; margin: 10px 0; }}
        pre {{ background: #0a0a0a; padding: 15px; overflow-x: auto; border-radius: 4px; }}
        .badge-critical {{ background: #ff0000; padding: 4px 12px; border-radius: 4px; }}
        .badge-warning {{ background: #ffaa00; color: black; padding: 4px 12px; border-radius: 4px; }}
        .footer {{ text-align: center; padding: 20px; color: #666; }}
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>⚡ SHΔDØW RECON V2 ⚡</h1>
        <div>Target: {self.target} | Evasion: {self.evasion_level.upper()}</div>
        <div>Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
    </div>
    
    <div class="scan-info">
        <div><strong>Duration:</strong> {datetime.datetime.now() - self.start_time}</div>
        <div><strong>NSE Scripts:</strong> {len(self.results.get('nse_results', {}).get('scripts_executed', []))}</div>
        <div><strong>Metasploit:</strong> {'Enabled' if self.enable_metasploit else 'Disabled'}</div>
    </div>
    
    <div class="section">
        <h2>🔴 CRITICAL FINDINGS</h2>
        {''.join(f'<div class="finding-critical"><span class="badge-critical">CRITICAL</span> {f}</div>' for f in critical) if critical else '<p>None</p>'}
    </div>
    
    <div class="section">
        <h2>🟡 WARNINGS</h2>
        {''.join(f'<div class="finding-warning"><span class="badge-warning">WARNING</span> {w}</div>' for w in warnings[:10]) if warnings else '<p>None</p>'}
    </div>
    
    <div class="section">
        <h2>📜 NSE RESULTS</h2>
        <pre>{self.results.get('nse_results', {}).get('output_summary', 'No NSE data')[:1500]}</pre>
    </div>
    
    <div class="section">
        <h2>🔌 OPEN PORTS</h2>
        <pre>{', '.join(self.results.get('port_scanning', {}).get('masscan', {}).get('open_ports_found', [])[:50]) or 'None'}</pre>
    </div>
    
    <div class="section">
        <h2>🌾 HARVESTED EMAILS</h2>
        <pre>{chr(10).join(self.results.get('harvesting', {}).get('emails', [])[:20]) or 'None'}</pre>
    </div>
    
    <div class="footer">
        Full logs: {self.output_dir}
    </div>
</div>
</body>
</html>
"""
        
        report_path = self.output_dir / "reports" / "shadow_recon_report.html"
        with open(report_path, 'w') as f:
            f.write(html)
        
        self.log(f"✅ Report saved: {report_path}", "SUCCESS")
        return str(report_path)
    
    # ============ MAIN ============
    def run(self):
        """Execute all phases"""
        self.log(f"{BOLD}{'='*60}{RESET}", "SUCCESS")
        self.log(f"{BOLD}🚀 {SCRIPT_NAME} INITIALIZED{RESET}", "SUCCESS")
        self.log(f"{BOLD}🎯 TARGET: {self.target} | EVASION: {self.evasion_level.upper()}{RESET}", "SUCCESS")
        self.log(f"{BOLD}{'='*60}{RESET}", "SUCCESS")
        
        try:
            self.phase_osint()
            self.phase_dns_recon()
            open_ports = self.phase_port_scanning_and_nse()
            self.phase_web_enumeration()
            self.phase_javascript_analysis()
            self.phase_vulnerability_scanning()
            if self.enable_metasploit:
                self.phase_metasploit()
            self.phase_deep_harvesting()
            self.phase_database_testing()
            report = self.generate_html_report()
            
            self.log(f"{BOLD}{'='*60}{RESET}", "SUCCESS")
            self.log(f"{BOLD}✅ RECON COMPLETE! Report: {report}{RESET}", "SUCCESS")
            return 0
        except KeyboardInterrupt:
            self.log("Interrupted by user", "WARNING")
            return 1
        except Exception as e:
            self.log(f"Fatal error: {e}", "ERROR")
            import traceback
            self.log(traceback.format_exc(), "ERROR")
            return 1

def main():
    parser = argparse.ArgumentParser(description="SHΔDØW RECON V2 - Advanced BlackArch Reconnaissance")
    parser.add_argument("-t", "--target", required=True, help="Target domain or IP")
    parser.add_argument("-o", "--output", default="./recon_results", help="Output directory")
    parser.add_argument("-e", "--evasion", choices=["none", "low", "normal", "aggressive", "paranoid"], 
                        default="normal", help="Evasion level")
    parser.add_argument("-m", "--metasploit", action="store_true", help="Enable Metasploit (if results saving works)")
    parser.add_argument("--threads", type=int, default=10, help="Thread count")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    recon = ShadowReconV2(
        target=args.target,
        output_dir=args.output,
        evasion_level=args.evasion,
        threads=args.threads,
        verbose=args.verbose,
        enable_metasploit=args.metasploit
    )
    
    sys.exit(recon.run())

if __name__ == "__main__":
    main()

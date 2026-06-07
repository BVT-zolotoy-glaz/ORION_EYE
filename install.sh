# Full recon with NSE evasion, no Metasploit
sudo python3 shadow_recon_v2.py -t target.com -e aggressive -o ./results

# Same but with Metasploit (only if you want it)
sudo python3 shadow_recon_v2.py -t target.com -e aggressive -m -o ./results

# Paranoid stealth mode
sudo python3 shadow_recon_v2.py -t target.com -e paranoid --threads 5

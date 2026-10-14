from typing import List, Dict, Any
from firewall.packet import Packet


def generate_enterprise_100_scenario() -> List[Packet]:
    """
    Generates a rich, realistic stream of exactly 100 synthetic packets (PKT-001 through PKT-100).
    Demonstrates:
      - Legitimate outbound HTTPS/HTTP sessions with stateful replies
      - DNS queries and replies (UDP)
      - External unsolicited scans (SSH, RDP, SMB, Telnet)
      - Specific block rules (compromised host, banned telnet, rogue host)
      - Malformed packets & validation failures
      - Pseudo-replies to blocked attempts (showing no state created)
      - Highlighting clear differences between Stateless and Stateful firewalls
    """
    packets = []
    seq = 1

    # 1. Outbound HTTPS flow from Client 1 (192.168.1.10) to Web Server 1 (198.51.100.10:443)
    # Packets 1-8: Outbound SYN, Inbound SYN-ACK, Outbound ACK, Inbound Data, Outbound Data, Inbound Reply, Inbound Data, Outbound Close
    packets.append(Packet(
        source_ip="192.168.1.10", destination_ip="198.51.100.10", port=443, protocol="TCP",
        source_port=51001, packet_id=f"PKT-{seq:03d}", sequence=seq,
        purpose="Client HTTPS Initial Handshake (SYN)",
        explanation="Internal client initiating secure TLS session to external web server",
        flow_id="FLOW-HTTPS-01", direction="OUTBOUND", tcp_flags="SYN",
        payload_summary="TLS ClientHello (SNI: secure-portal.org, TLSv1.3)"
    ))
    seq += 1

    packets.append(Packet(
        source_ip="198.51.100.10", destination_ip="192.168.1.10", port=51001, protocol="TCP",
        source_port=443, packet_id=f"PKT-{seq:03d}", sequence=seq,
        purpose="Server HTTPS Handshake Reply (SYN-ACK)",
        explanation="External server replying to Client 1 ephemeral port. Stateful firewall accepts; Stateless blocks unless inbound allowed.",
        flow_id="FLOW-HTTPS-01", direction="REPLY", tcp_flags="SYN,ACK",
        payload_summary="TLS ServerHello, Certificate, KeyExchange"
    ))
    seq += 1

    packets.append(Packet(
        source_ip="192.168.1.10", destination_ip="198.51.100.10", port=443, protocol="TCP",
        source_port=51001, packet_id=f"PKT-{seq:03d}", sequence=seq,
        purpose="Client HTTPS Handshake Completion (ACK)",
        explanation="Client completing 3-way handshake with ACK",
        flow_id="FLOW-HTTPS-01", direction="OUTBOUND", tcp_flags="ACK",
        payload_summary="TCP ACK, Handshake Complete"
    ))
    seq += 1

    packets.append(Packet(
        source_ip="192.168.1.10", destination_ip="198.51.100.10", port=443, protocol="TCP",
        source_port=51001, packet_id=f"PKT-{seq:03d}", sequence=seq,
        purpose="Client HTTPS Application Data Request",
        explanation="Encrypted HTTP GET request over established TLS connection",
        flow_id="FLOW-HTTPS-01", direction="OUTBOUND", tcp_flags="PSH,ACK",
        payload_summary="Encrypted Application Data (1420 bytes)"
    ))
    seq += 1

    packets.append(Packet(
        source_ip="198.51.100.10", destination_ip="192.168.1.10", port=51001, protocol="TCP",
        source_port=443, packet_id=f"PKT-{seq:03d}", sequence=seq,
        purpose="Server HTTPS Response Fragment 1",
        explanation="Server streaming encrypted web page response back to client",
        flow_id="FLOW-HTTPS-01", direction="REPLY", tcp_flags="ACK",
        payload_summary="Encrypted Application Data (1420 bytes)"
    ))
    seq += 1

    packets.append(Packet(
        source_ip="198.51.100.10", destination_ip="192.168.1.10", port=51001, protocol="TCP",
        source_port=443, packet_id=f"PKT-{seq:03d}", sequence=seq,
        purpose="Server HTTPS Response Fragment 2",
        explanation="Subsequent server reply packet recognized by connection state table",
        flow_id="FLOW-HTTPS-01", direction="REPLY", tcp_flags="PSH,ACK",
        payload_summary="Encrypted Application Data (890 bytes)"
    ))
    seq += 1

    # 2. Outbound HTTP Web session from Client 1 (192.168.1.10) to Web Server 2 (198.51.100.20:80)
    # Allowed by Rule #2 (Allow Web HTTP)
    packets.append(Packet(
        source_ip="192.168.1.10", destination_ip="198.51.100.20", port=80, protocol="TCP",
        source_port=52002, packet_id=f"PKT-{seq:03d}", sequence=seq,
        purpose="Client HTTP Connection (SYN)",
        explanation="Client 192.168.1.10 browsing HTTP server (matches Rule 2: ALLOW)",
        flow_id="FLOW-HTTP-01", direction="OUTBOUND", tcp_flags="SYN",
        payload_summary="GET /index.html HTTP/1.1 (Host: docs.example.org)"
    ))
    seq += 1

    packets.append(Packet(
        source_ip="198.51.100.20", destination_ip="192.168.1.10", port=52002, protocol="TCP",
        source_port=80, packet_id=f"PKT-{seq:03d}", sequence=seq,
        purpose="Web Server HTTP Reply (SYN-ACK)",
        explanation="HTTP Server response. Stateful ALLOWS as ESTABLISHED; Stateless BLOCKS.",
        flow_id="FLOW-HTTP-01", direction="REPLY", tcp_flags="SYN,ACK",
        payload_summary="HTTP/1.1 200 OK (Content-Type: text/html)"
    ))
    seq += 1

    packets.append(Packet(
        source_ip="192.168.1.10", destination_ip="198.51.100.20", port=80, protocol="TCP",
        source_port=52002, packet_id=f"PKT-{seq:03d}", sequence=seq,
        purpose="Client HTTP Response ACK",
        explanation="Client acknowledgment of server HTTP payload",
        flow_id="FLOW-HTTP-01", direction="OUTBOUND", tcp_flags="ACK",
        payload_summary="TCP ACK [Seq=150 Ack=1460]"
    ))
    seq += 1

    packets.append(Packet(
        source_ip="198.51.100.20", destination_ip="192.168.1.10", port=52002, protocol="TCP",
        source_port=80, packet_id=f"PKT-{seq:03d}", sequence=seq,
        purpose="Web Server HTTP Connection FIN",
        explanation="Server initiates graceful connection close",
        flow_id="FLOW-HTTP-01", direction="REPLY", tcp_flags="FIN,ACK",
        payload_summary="TCP Connection Teardown"
    ))
    seq += 1

    # 3. Client 2 (192.168.1.15) concurrent HTTPS session to API Gateway (203.0.113.80:443)
    for i in range(10):
        is_reply = (i % 2 == 1)
        src = "203.0.113.80" if is_reply else "192.168.1.15"
        dst = "192.168.1.15" if is_reply else "203.0.113.80"
        dport = 53010 if is_reply else 443
        sport = 443 if is_reply else 53010
        packets.append(Packet(
            source_ip=src, destination_ip=dst, port=dport, protocol="TCP",
            source_port=sport, packet_id=f"PKT-{seq:03d}", sequence=seq,
            purpose=f"API Gateway TLS Data ({'Inbound Reply' if is_reply else 'Outbound Request'})",
            explanation=f"Client 2 REST API call to external cloud service (Step {i+1}/10)",
            flow_id="FLOW-API-01", direction="REPLY" if is_reply else "OUTBOUND",
            tcp_flags="ACK" if i > 1 else ("SYN,ACK" if is_reply else "SYN"),
            payload_summary=f"JSON API payload chunk #{i+1} (OAuth Token Exchange)"
        ))
        seq += 1

    # 4. UDP DNS Resolution Flow (Packets 21-32)
    # Allowed by Rule 5 (Allow DNS Queries)
    dns_queries = [
        ("api.google.com", 54001),
        ("github.com", 54002),
        ("cdn.cloudflare.net", 54003),
        ("update.microsoft.com", 54004),
        ("internal-intranet.local", 54005),
        ("time.nist.gov", 54006)
    ]
    for domain, sport in dns_queries:
        # Outbound query
        packets.append(Packet(
            source_ip="192.168.1.10", destination_ip="8.8.8.8", port=53, protocol="UDP",
            source_port=sport, packet_id=f"PKT-{seq:03d}", sequence=seq,
            purpose=f"DNS Query for {domain}",
            explanation=f"Client resolving domain {domain} via external Google DNS 8.8.8.8",
            flow_id=f"FLOW-DNS-{sport}", direction="OUTBOUND",
            payload_summary=f"Standard query 0x{sport:04x} A {domain}"
        ))
        seq += 1
        # Inbound reply
        packets.append(Packet(
            source_ip="8.8.8.8", destination_ip="192.168.1.10", port=sport, protocol="UDP",
            source_port=53, packet_id=f"PKT-{seq:03d}", sequence=seq,
            purpose=f"DNS Response for {domain}",
            explanation=f"DNS server 8.8.8.8 returning A record IP address for {domain}",
            flow_id=f"FLOW-DNS-{sport}", direction="REPLY",
            payload_summary=f"Standard response 0x{sport:04x} A {domain} -> 142.250.190.46"
        ))
        seq += 1

    # 5. External Unsolicited Inbound Scans (Packets 33-50)
    # External attacker 203.0.113.199 probing internal hosts.
    # No prior outbound state exists, and no inbound rule allows these -> DEFAULT_BLOCK!
    scan_ports = [
        (22, "SSH Remote Shell Probe"),
        (23, "Telnet Insecure Login Probe"),
        (21, "FTP Control Port Probe"),
        (25, "SMTP Mail Relay Probe"),
        (3389, "RDP Remote Desktop Scan"),
        (445, "SMB / EternalBlue Vulnerability Probe"),
        (1433, "Microsoft SQL Server Scan"),
        (3306, "MySQL Database Port Scan"),
        (5900, "VNC Remote Display Probe"),
        (8080, "HTTP Alt Proxy Scan"),
        (8443, "HTTPS Alt Management Scan"),
        (2323, "Mirai Botnet Telnet Alternate"),
        (5060, "SIP VoIP Service Scan"),
        (161, "SNMP Public Community Probe"),
        (137, "NetBIOS Name Service Scan"),
        (139, "NetBIOS Session Service Scan"),
        (4444, "Metasploit Default Listener Probe"),
        (9001, "Tor Relay Inbound Probe")
    ]
    for port, label in scan_ports:
        packets.append(Packet(
            source_ip="203.0.113.199", destination_ip="192.168.1.100", port=port, protocol="TCP",
            source_port=49000 + (port % 1000), packet_id=f"PKT-{seq:03d}", sequence=seq,
            purpose=f"Unsolicited Scan: {label}",
            explanation=f"External adversary probing port {port}. No connection state exists -> Default BLOCK.",
            flow_id="FLOW-ATTACK-SCAN", direction="INBOUND", tcp_flags="SYN",
            payload_summary=f"TCP SYN stealth port scan ({port})"
        ))
        seq += 1

    # 6. Specific Block Rules & Policy Violations (Packets 51-65)
    # Packets 51-55: Compromised Host 192.168.1.50 -> port 80 (Blocked by RULE-1)
    for i in range(5):
        packets.append(Packet(
            source_ip="192.168.1.50", destination_ip="198.51.100.50", port=80, protocol="TCP",
            source_port=55000 + i, packet_id=f"PKT-{seq:03d}", sequence=seq,
            purpose=f"Malware C2 Communication Attempt #{i+1}",
            explanation="Compromised host 192.168.1.50 attempting outbound HTTP -> Blocked by Rule 1",
            flow_id="FLOW-MALWARE-01", direction="OUTBOUND", tcp_flags="SYN",
            payload_summary="POST /beacon/heartbeat HTTP/1.1 (Bot ID: Trojan.Gen)"
        ))
        seq += 1

    # Packets 56-60: Banned Telnet Attempt from 192.168.1.20 (Blocked by RULE-2 / RULE-3)
    for i in range(5):
        packets.append(Packet(
            source_ip="192.168.1.20", destination_ip="198.51.100.99", port=23, protocol="TCP",
            source_port=56000 + i, packet_id=f"PKT-{seq:03d}", sequence=seq,
            purpose=f"Forbidden Telnet Session Attempt #{i+1}",
            explanation="Internal user attempting insecure unencrypted Telnet port 23 -> Blocked by Rule",
            flow_id="FLOW-TELNET-DENY", direction="OUTBOUND", tcp_flags="SYN",
            payload_summary="Telnet IAC WILL ECHO Option Negotiation"
        ))
        seq += 1

    # Packets 61-65: Rogue Host 10.0.0.5 traffic (Blocked by RULE-4 / RULE-6)
    for i in range(5):
        packets.append(Packet(
            source_ip="10.0.0.5", destination_ip="198.51.100.1", port=100 + i, protocol="TCP",
            source_port=57000 + i, packet_id=f"PKT-{seq:03d}", sequence=seq,
            purpose=f"Rogue Host Unauthorized Exfiltration #{i+1}",
            explanation="Unauthorized subnet host 10.0.0.5 attempting external network hop -> Blocked by Rule",
            flow_id="FLOW-ROGUE-HOST", direction="OUTBOUND", tcp_flags="SYN",
            payload_summary="Raw socket unauthorized packet"
        ))
        seq += 1

    # 7. Malformed Packets & Input Validation Failures (Packets 66-75)
    # Tests engine input validation: invalid IP, out-of-range ports, unsupported protocol
    invalid_specs = [
        ("999.999.999.999", "192.168.1.10", 80, "TCP", 50000, "Bogus Source IPv4 Octets"),
        ("192.168.1.10", "300.1.2.3", 443, "TCP", 50001, "Invalid Destination IP Address"),
        ("192.168.1.10", "198.51.100.1", 70000, "TCP", 50002, "Destination Port > 65535 Out of Range"),
        ("192.168.1.10", "198.51.100.1", -5, "TCP", 50003, "Negative Destination Port"),
        ("192.168.1.10", "198.51.100.1", 80, "TCP", 80000, "Source Port > 65535 Out of Range"),
        ("192.168.1.10", "198.51.100.1", 80, "GRE", 50004, "Unsupported Protocol (GRE / Generic Routing Encapsulation)"),
        ("192.168.1.10", "198.51.100.1", 80, "IGMP", 50005, "Unsupported Protocol (IGMP Multicast)"),
        ("bad-ip-string", "198.51.100.1", 443, "TCP", 50006, "Non-numeric Corrupted IP Header"),
        ("192.168.1.10", "198.51.100.1", 80, "OSPF", 50007, "Unsupported Routing Protocol (OSPF)"),
        ("256.0.0.1", "198.51.100.1", 443, "TCP", 50008, "Out-of-range Class A IP Format")
    ]
    for sip, dip, dport, proto, sport, label in invalid_specs:
        packets.append(Packet(
            source_ip=sip, destination_ip=dip, port=dport, protocol=proto,
            source_port=sport, packet_id=f"PKT-{seq:03d}", sequence=seq,
            purpose=f"Malformed Packet: {label}",
            explanation=f"Malformed packet headers. Engine input validator safely rejects without crashing.",
            flow_id="FLOW-CORRUPTED", direction="INVALID",
            payload_summary="Malformed / Corrupted Header Bytes"
        ))
        seq += 1

    # 8. First-Match-Wins Rule Shadowing & Ordering Tests (Packets 76-85)
    # Client 192.168.1.10 accessing allowed HTTPS port 443 vs client attempting unlisted port
    for i in range(10):
        target_port = 443 if i % 2 == 0 else (8080 + i)
        is_allowed = (target_port == 443)
        packets.append(Packet(
            source_ip="192.168.1.10", destination_ip="198.51.100.77", port=target_port, protocol="TCP",
            source_port=58000 + i, packet_id=f"PKT-{seq:03d}", sequence=seq,
            purpose=f"Rule Policy Verification (Port {target_port})",
            explanation=f"Testing rule order precedence. Port 443 matches Rule 3 (ALLOW); Port {target_port} falls through to Default BLOCK.",
            flow_id="FLOW-ORDER-TEST", direction="OUTBOUND", tcp_flags="SYN",
            payload_summary=f"TCP Connection Probe to Port {target_port}"
        ))
        seq += 1

    # 9. Pseudo-Replies to Previously Blocked Connection Attempts (Packets 86-94)
    # External attacker attempting to spoof replies to the blocked malware beacons or scans
    for i in range(9):
        packets.append(Packet(
            source_ip="198.51.100.50", destination_ip="192.168.1.50", port=55000 + (i % 5), protocol="TCP",
            source_port=80, packet_id=f"PKT-{seq:03d}", sequence=seq,
            purpose=f"Spoofed Inbound Reply for Blocked Session #{i+1}",
            explanation="External packet claiming to be a reply, but initial outbound packet was blocked so NO connection state exists -> Default BLOCK.",
            flow_id="FLOW-SPOOFED-REPLY", direction="REPLY", tcp_flags="ACK",
            payload_summary="Inbound packet with ACK flag matching no active state table entry"
        ))
        seq += 1

    # 10. ICMP Diagnostics (Packets 95-100)
    # Ping echo requests and replies
    icmp_tests = [
        ("192.168.1.10", "198.51.100.1", 0, "OUTBOUND", "Echo Request (Ping)", "Internal host pinging gateway"),
        ("198.51.100.1", "192.168.1.10", 0, "REPLY", "Echo Reply (Pong)", "Gateway replying to ping request"),
        ("192.168.1.15", "8.8.8.8", 0, "OUTBOUND", "Echo Request (Ping)", "Client pinging public DNS"),
        ("8.8.8.8", "192.168.1.15", 0, "REPLY", "Echo Reply (Pong)", "Public DNS answering ICMP echo"),
        ("203.0.113.199", "192.168.1.100", 0, "INBOUND", "Unsolicited ICMP Ping Probe", "External host ping sweep probe"),
        ("192.168.1.10", "198.51.100.254", 0, "OUTBOUND", "ICMP TraceRoute Hop", "Diagnostic traceroute probe")
    ]
    for sip, dip, port_val, dir_str, label, expl in icmp_tests:
        packets.append(Packet(
            source_ip=sip, destination_ip=dip, port=port_val, protocol="ICMP",
            source_port=None, packet_id=f"PKT-{seq:03d}", sequence=seq,
            purpose=f"ICMP {label}",
            explanation=f"{expl}. ICMP has no ports and is evaluated against general rule policy.",
            flow_id="FLOW-ICMP-DIAG", direction=dir_str,
            payload_summary="ICMP Echo payload (32 bytes data: 'abcdefghijklmnopqrstuvw')"
        ))
        seq += 1

    return packets


def generate_scan_defense_100_scenario() -> List[Packet]:
    """
    Second 100-packet preset: Heavy adversarial scanning, DDoS wave, and unauthorized exfiltration attempts.
    """
    packets = []
    seq = 1
    # 20 background legitimate web packets
    for i in range(20):
        is_reply = (i % 2 == 1)
        packets.append(Packet(
            source_ip="198.51.100.10" if is_reply else "192.168.1.10",
            destination_ip="192.168.1.10" if is_reply else "198.51.100.10",
            port=50000 if is_reply else 443,
            protocol="TCP",
            source_port=443 if is_reply else 50000,
            packet_id=f"PKT-{seq:03d}", sequence=seq,
            purpose="Legitimate Business Web Session",
            explanation="Normal background user browsing while network is under attack",
            flow_id="FLOW-LEGIT-01", direction="REPLY" if is_reply else "OUTBOUND",
            payload_summary="Standard HTTPS encrypted packet"
        ))
        seq += 1

    # 60 rapid attack packets probing random internal ports
    attacker_ips = ["203.0.113.44", "203.0.113.88", "198.51.100.222"]
    ports = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 993, 1433, 1521, 3306, 3389, 5432, 5900, 8080]
    for i in range(60):
        src = attacker_ips[i % len(attacker_ips)]
        tgt_port = ports[i % len(ports)]
        packets.append(Packet(
            source_ip=src, destination_ip="192.168.1.100", port=tgt_port, protocol="TCP",
            source_port=40000 + i, packet_id=f"PKT-{seq:03d}", sequence=seq,
            purpose=f"SYN Flood / Port Scan (Port {tgt_port})",
            explanation="High-velocity port sweep from external botnet IP -> Default BLOCK.",
            flow_id=f"FLOW-SWEEP-{tgt_port}", direction="INBOUND", tcp_flags="SYN",
            payload_summary=f"Automated exploit scanner probe targeting port {tgt_port}"
        ))
        seq += 1

    # 20 malformed flood packets
    for i in range(20):
        packets.append(Packet(
            source_ip="999.888.777.666", destination_ip="192.168.1.100", port=80, protocol="TCP",
            source_port=60000 + i, packet_id=f"PKT-{seq:03d}", sequence=seq,
            purpose="Spoofed IP Flood Attack",
            explanation="Volumetric attack with forged non-routable source IP addresses",
            flow_id="FLOW-SPOOF-FLOOD", direction="INVALID",
            payload_summary="Forged IP header packet"
        ))
        seq += 1

    return packets


def generate_rule_order_100_scenario() -> List[Packet]:
    """
    Third 100-packet preset: Focused on policy rule order, shadowing, and specific vs broad exceptions.
    """
    packets = []
    seq = 1
    # 100 packets alternating between specific client 192.168.1.50 and general clients
    for i in range(100):
        client = "192.168.1.50" if i % 2 == 0 else f"192.168.1.{10 + (i % 30)}"
        target_port = 80 if i % 3 == 0 else (443 if i % 3 == 1 else 23)
        proto = "TCP"
        packets.append(Packet(
            source_ip=client, destination_ip="198.51.100.100", port=target_port, protocol=proto,
            source_port=50000 + i, packet_id=f"PKT-{seq:03d}", sequence=seq,
            purpose=f"Policy Precedence Test #{i+1} ({client} : {target_port})",
            explanation=f"Verifying first-match-wins rule execution order for {client} accessing port {target_port}",
            flow_id=f"FLOW-PRECEDENCE-{i+1}", direction="OUTBOUND", tcp_flags="SYN",
            payload_summary=f"HTTP/HTTPS/Telnet request from {client} to port {target_port}"
        ))
        seq += 1

    return packets


SCENARIOS = {
    "enterprise_100": {
        "id": "enterprise_100",
        "name": "Enterprise Web & Multi-Service Stream (100 Packets)",
        "description": "Comprehensive 100-packet stream with outbound web sessions, stateful server replies, DNS lookups, unsolicited inbound port scans, policy violations, malformed packets, and ICMP diagnostics.",
        "packet_count": 100,
        "recommended": True,
        "generator": generate_enterprise_100_scenario
    },
    "scan_defense_100": {
        "id": "scan_defense_100",
        "name": "Attack Wave & Inbound Defense (100 Packets)",
        "description": "High-intensity 100-packet security audit featuring reconnaissance port sweeps, syn floods, and spoofed address attacks against internal servers.",
        "packet_count": 100,
        "recommended": False,
        "generator": generate_scan_defense_100_scenario
    },
    "rule_order_100": {
        "id": "rule_order_100",
        "name": "Rule-Order & Policy Precedence Lab (100 Packets)",
        "description": "Systematic 100-packet test suite exploring first-match-wins rule ordering, shadow rules, and specific deny versus broad allow configurations.",
        "packet_count": 100,
        "recommended": False,
        "generator": generate_rule_order_100_scenario
    }
}


def get_scenario_packets(scenario_id: str) -> List[Packet]:
    """
    Returns the packet list for the given scenario ID, defaulting to enterprise_100.
    """
    scenario = SCENARIOS.get(scenario_id, SCENARIOS["enterprise_100"])
    return scenario["generator"]()

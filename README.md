# NetFort — Web Firewall Simulator & Traffic Access Control System

[![CI](https://github.com/USERNAME/NetFort/actions/workflows/ci.yml/badge.svg)](https://github.com/USERNAME/NetFort/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.129%2B-009688.svg)
![React](https://img.shields.io/badge/React-18-61DAFB.svg)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-38B2AC.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

NetFort is a browser-based **educational firewall simulator and network access control testing platform**. It allows presenters, students, and engineers to explore how **stateless packet filtering** and **stateful inspection** handle the exact same network traffic stream.

Operating strictly within a safe, simulated sandbox, NetFort evaluates synthetic packets without touching the host operating system's firewall rules or capturing real network traffic.

---

## What's New in NetFort v2.0

* **100-Packet Synthetic Traffic Stream**: Generates a realistic, deterministic 100-packet stream (`PKT-001` through `PKT-100`) containing legitimate HTTP/HTTPS web sessions, stateful server responses, DNS queries, unsolicited scans (SSH, RDP, Telnet, SMB), policy violations, malformed headers, and ICMP diagnostics.
* **Double-Click Raw Packet Inspection**: Double-clicking on **any packet** across the application opens the original wire disassembly in Wireshark / tcpdump text format with IP headers and a raw hex/ASCII frame preview.
* **Live Step-by-Step Simulation**: Pacing controls (2.0s presentation default, 1.0s, 0.5s, 0.1s, and manual step), 3-stage traffic flow canvas (Queue → Engine Checklist → Allowed/Blocked Decision Lanes), and real-time plain-English reasoning ("Why?").
* **Compare Firewalls**: Parallel dual-column side-by-side execution comparing Stateless vs Stateful firewalls over the identical 100-packet stream, with difference detection (16 divergent packets, 84 matching).
* **Firewall Rules Editor**: Ordered rule table with priority drag/reordering, inline IP/CIDR and port validation, preset switcher (`Balanced`, `Strict`, `Order Shadow`), and instant persistence.
* **Metrics & Analytics**: Vivid data visualizations powered by Recharts (outcome distribution donut, side-by-side grouped bar chart), divergence breakdown, and an interactive plain-English metric glossary.
* **Filterable Packet Log**: Searchable table across 100 packets with verdict filters, pagination, inspection drawer, and one-click CSV export.

---

## Table of Contents

* [Overview](#overview)
* [Quick Start](#quick-start)
* [Core Concepts](#core-concepts)
* [System Architecture](#system-architecture)
* [Project Structure](#project-structure)
* [Features](#features)
* [Running NetFort](#running-netfort)
* [Running Automated Tests](#running-automated-tests)
* [Practical Demonstration Flow](#practical-demonstration-flow)
* [Security Concepts Demonstrated](#security-concepts-demonstrated)
* [Technology Stack](#technology-stack)
* [Safety & Ethical Boundaries](#safety--ethical-boundaries)

---

# Overview

A firewall is a network security mechanism that controls network traffic according to a defined set of security rules.

NetFort demonstrates this concept by representing a network packet using four primary attributes:

* Source IP address
* Destination IP address
* Port
* Protocol

The packet is then passed to the firewall engine.

The engine compares the packet against the configured firewall rules from top to bottom.

The first matching rule determines the action:

```text
Packet
   |
   v
Firewall Rules
   |
   v
Rule Matching
   |
   +---- Match ----> ALLOW / BLOCK
   |
   +---- No Match -> Default Policy
```

NetFort uses a default policy of **BLOCK**, meaning that traffic which does not match any explicit rule is rejected.

---

# Objectives

The main objectives of NetFort are:

1. Demonstrate the working principle of a firewall.
2. Implement packet filtering using source IP, destination IP, port and protocol.
3. Provide configurable firewall rules.
4. Demonstrate ALLOW and BLOCK access-control decisions.
5. Implement rule priority.
6. Demonstrate a default-deny security policy.
7. Maintain firewall activity logs.
8. Display packet statistics.
9. Provide simulated network traffic for testing.
10. Demonstrate the basic concept of a stateful firewall.

---

# Core Concepts

NetFort primarily focuses on the following Network Security concepts.

## 1. Firewall

A firewall controls network traffic between systems or network segments based on predefined security rules.

In NetFort, the firewall is represented as a software engine that evaluates simulated packets.

The basic decision is:

```text
ALLOW
```

or

```text
BLOCK
```

---

## 2. Packet Filtering

Packet filtering is the primary firewall technique implemented by NetFort.

The firewall examines attributes of a packet such as:

```text
Source IP
Destination IP
Port
Protocol
```

and compares them with firewall rules.

For example:

```text
Rule:

Source IP      : 192.168.1.20
Destination IP : *
Port           : 23
Protocol       : TCP
Action         : BLOCK
```

A packet such as:

```text
Source IP      : 192.168.1.20
Destination IP : 192.168.1.100
Port           : 23
Protocol       : TCP
```

matches the rule and is therefore blocked.

---

## 3. Access Control

Firewall rules act as access-control policies.

A rule can explicitly specify whether matching traffic should be allowed or denied.

Example:

```text
192.168.1.10 → Port 80 → TCP → ALLOW
```

This allows matching HTTP traffic.

Another example:

```text
192.168.1.20 → Port 23 → TCP → BLOCK
```

This blocks matching Telnet traffic.

---

## 4. Wildcard Matching

NetFort supports the wildcard:

```text
*
```

The wildcard represents "any value".

For example:

```text
Source IP      : *
Destination IP : *
Port           : 443
Protocol       : TCP
Action         : ALLOW
```

This means:

> Allow TCP traffic on port 443 regardless of the source or destination IP.

The protocol can also use:

```text
ANY
```

to match any supported protocol.

---

## 5. Rule Priority

Rules are evaluated from top to bottom.

The **first matching rule wins**.

For example:

```text
Rule 1:
192.168.1.50 → * → 80 → TCP → BLOCK

Rule 2:
* → * → 80 → TCP → ALLOW
```

A packet from:

```text
192.168.1.50
```

to port:

```text
80
```

matches both rules.

However, Rule 1 is evaluated first, so the packet is:

```text
BLOCKED
```

This demonstrates the importance of firewall rule ordering.

---

## 6. Default Policy

If a packet does not match any configured rule, NetFort applies its default policy.

The default policy is:

```text
BLOCK
```

Therefore:

```text
Packet
   |
   v
Check Rule 1
   |
   v
Check Rule 2
   |
   v
Check Rule 3
   |
   v
No Rule Matches
   |
   v
DEFAULT = BLOCK
```

This follows a default-deny/allow-list approach where traffic must have an applicable allow rule to be accepted.

---

## 7. Stateful Firewall Concept

NetFort also contains a basic stateful-firewall simulation.

A stateless packet filter evaluates packets individually.

A stateful firewall additionally keeps track of active connections.

For example:

```text
Client                         Server

192.168.1.10:5000
        |
        | TCP Request
        v
                     192.168.1.100:80
```

The connection can be recorded as:

```text
192.168.1.10:5000
        |
        v
192.168.1.100:80

State: ESTABLISHED
```

If the server sends a response back through the reverse direction, the stateful component can recognize it as belonging to the existing connection.

The stateful component is intended as an educational simulation rather than a production firewall implementation.

---

# How NetFort Works

The complete processing flow is:

```text
                  USER
                    |
                    v
             Packet Simulator
                    |
                    v
              Create Packet
                    |
                    v
            Validate Packet
                    |
                    v
             Firewall Engine
                    |
                    v
             Load Firewall Rules
                    |
                    v
          Compare Rules Sequentially
                    |
             +------+------+
             |             |
           MATCH        NO MATCH
             |             |
             v             v
       Rule Action    Default Policy
             |             |
             +------+------+
                    |
                    v
              ALLOW / BLOCK
                    |
          +---------+---------+
          |                   |
          v                   v
       Firewall Log       Statistics
```

---

# System Architecture

NetFort follows a modular architecture.

```text
+-------------------------------------------------------+
|                    NETFORT GUI                        |
|                  Tkinter Interface                   |
+---------------------------+---------------------------+
                            |
                            v
+-------------------------------------------------------+
|                  PACKET MODULE                        |
|       Packet Creation & Input Validation             |
+---------------------------+---------------------------+
                            |
                            v
+-------------------------------------------------------+
|                FIREWALL ENGINE                       |
|       Packet Evaluation & Decision Making             |
+---------------------------+---------------------------+
                            |
                            v
+-------------------------------------------------------+
|                  RULE MANAGER                         |
|       Create / Delete / Load / Save Rules             |
+---------------------------+---------------------------+
                            |
                            v
+-------------------------------------------------------+
|                   rules.json                          |
|              Persistent Firewall Rules                |
+-------------------------------------------------------+

                            |
                            v
+-------------------------------------------------------+
|                    LOGGING                            |
|                firewall.log                          |
+-------------------------------------------------------+

                            |
                            v
+-------------------------------------------------------+
|                  STATISTICS                           |
|      Total / Allowed / Blocked / Block Rate           |
+-------------------------------------------------------+
```

---

# Architecture Components

## 1. GUI Layer

File:

```text
gui/interface.py
```

The GUI provides the user interface for interacting with NetFort.

It allows users to:

* Enter packet information.
* Check packets.
* Generate random packets.
* Add firewall rules.
* Delete firewall rules.
* Change rule priority.
* View firewall logs.
* View packet statistics.
* Simulate multiple packets.

---

## 2. Packet Module

File:

```text
firewall/packet.py
```

The packet module represents a simulated network packet.

A packet contains:

```text
source_ip
destination_ip
port
protocol
```

The module also validates packet information before it is evaluated.

---

## 3. Rule Manager

File:

```text
firewall/rules.py
```

The Rule Manager is responsible for:

* Creating firewall rules.
* Validating rules.
* Loading rules.
* Saving rules.
* Deleting rules.
* Changing rule priority.

Rules are stored persistently in:

```text
data/rules.json
```

---

## 4. Firewall Engine

File:

```text
firewall/engine.py
```

The firewall engine is the main decision-making component.

It:

1. Receives a packet.
2. Validates it.
3. Iterates through firewall rules.
4. Finds the first matching rule.
5. Applies ALLOW or BLOCK.
6. Applies the default BLOCK policy if no rule matches.
7. Updates statistics.
8. Returns the decision and reason.

---

## 5. Stateful Firewall Module

File:

```text
firewall/state.py
```

This module provides a basic simulation of connection tracking.

It stores information about connections and can identify packets belonging to an existing connection.

---

## 6. Logging

File:

```text
logs/firewall.log
```

Every evaluated packet can be recorded in the firewall log.

A typical entry looks like:

```text
2026-09-15 19:32:05 |
SRC=192.168.1.20 |
DST=192.168.1.100 |
PORT=23 |
PROTO=TCP |
ACTION=BLOCK |
RULE#2
```

The log provides an audit trail of firewall activity.

---

## 7. Statistics

NetFort maintains:

```text
Total Packets
Allowed Packets
Blocked Packets
Block Rate
```

Block rate is calculated as:

```text
Block Rate =
(Blocked Packets / Total Packets) × 100
```

---

# Firewall Rule Processing

Consider the following rules:

```text
Rule 1:
192.168.1.10 | * | 80 | TCP | ALLOW

Rule 2:
192.168.1.20 | * | 23 | TCP | BLOCK

Rule 3:
* | * | 443 | TCP | ALLOW
```

And this packet:

```text
Source IP      : 192.168.1.20
Destination IP : 192.168.1.100
Port           : 23
Protocol       : TCP
```

Processing:

```text
Check Rule 1
       |
       X
No Match

Check Rule 2
       |
       ✓
Match

Action = BLOCK
```

Result:

```text
PACKET BLOCKED
```

---

# Project Structure

```text
NetFort/
│
├── .github/
│   └── workflows/
│       └── ci.yml               # Automated CI for backend tests & frontend build
│
├── backend/
│   └── app/
│       ├── main.py              # FastAPI application & SPA fallback handler
│       ├── scenarios.py         # 100-packet synthetic traffic generators
│       ├── api/
│       │   └── endpoints.py     # REST endpoints (rules, simulations, comparisons)
│       ├── schemas/
│       │   └── models.py        # Pydantic data models
│       └── services/
│           ├── simulation_service.py # Step-by-step simulator engine
│           ├── comparison_service.py # Dual-model comparison engine
│           └── metrics_service.py    # Analytics & KPI formulas
│
├── firewall/
│   ├── packet.py                # Packet model, wire format generator, validation
│   ├── rules.py                 # RuleManager, FirewallRule, presets, CIDR matching
│   ├── engine.py                # Core evaluation engine & structured reasons
│   └── state.py                 # Stateful 4-tuple conntrack & session timeouts
│
├── frontend/
│   ├── src/
│   │   ├── components/          # AppShell, OutcomeBadge, PacketInspectorModal
│   │   ├── context/             # Global double-click PacketModalContext
│   │   ├── pages/               # Dashboard, LiveSim, Compare, Rules, Metrics, PacketLog
│   │   ├── App.jsx              # Routing & providers
│   │   └── main.jsx
│   ├── package.json             # Vite, React 18, Tailwind, Lucide, Recharts
│   └── tailwind.config.js       # Color palette design tokens
│
├── data/
│   └── rules.json               # Persistent demo firewall rules
│
├── logs/
│   └── firewall.log             # Simulation execution audit log
│
├── tests/
│   ├── test_firewall.py         # Core packet filtering tests
│   ├── test_stateful.py         # Stateful connection tracking tests
│   └── test_api.py              # Backend REST API & 100-packet scenario tests
│
├── .env.example                 # Environment variables template
├── .gitignore                   # Comprehensive ignores (node_modules, dist, logs, venv)
├── main.py                      # Application launcher (Web server or legacy GUI)
├── requirements.txt             # Python backend dependencies
└── README.md
```

---

# Features

### Packet Simulation

Simulate packets without generating real network traffic.

### Firewall Rules

Configure rules based on:

* Source IP
* Destination IP
* Port
* Protocol
* Action

### Wildcard Rules

Use `*` for any IP or port and `ANY` for any supported protocol.

### Rule Priority

Move rules up or down to control which matching rule gets applied first.

### Default Deny

Unmatched packets are blocked.

### Packet Validation

Invalid IP addresses, ports and protocols are rejected.

### Logging

Firewall decisions are recorded in the log.

### Statistics

View total, allowed and blocked packet counts.

### Random Packet Generation

Generate random packets for testing.

### Bulk Simulation

Simulate 20 packets at once.

### Stateful Firewall Simulation

Demonstrate basic connection tracking.

### Automated Tests

Test the firewall engine using Python's built-in `unittest` framework.

---

# Requirements

## Hardware

A normal laptop or desktop computer is sufficient.

Recommended:

* 4 GB RAM or more
* Windows, Linux or macOS
* No dedicated networking hardware required

## Software

* Python 3.x
* Tkinter
* Git
* GitHub

No cloud service, database, Raspberry Pi, Arduino or dedicated firewall hardware is required.

---

# Installation

## Method 1 — Download ZIP from GitHub

If you downloaded NetFort as a ZIP file:

### Step 1

Download the repository from GitHub.

Click:

```text
Code → Download ZIP
```

### Step 2

Extract the ZIP file.

You should get a folder similar to:

```text
NetFort-main
```

### Step 3

Open the extracted folder.

Make sure you can see:

```text
main.py
firewall/
gui/
data/
logs/
tests/
```

---

# Method 2 — Clone using Git

If Git is installed, open PowerShell or Command Prompt and run:

```powershell
git clone <YOUR-GITHUB-REPOSITORY-URL>
```

For example:

```powershell
git clone https://github.com/USERNAME/NetFort.git
```

Then enter the project directory:

```powershell
cd NetFort
```

---

# Checking Python

Open PowerShell inside the NetFort directory.

Run:

```powershell
python --version
```

You should get:

```text
Python 3.x.x
```

Also verify pip:

```powershell
pip --version
```

NetFort primarily uses Python's standard library, so no large dependency installation is required.

---

# Running NetFort

### 1. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 2. Launch the Web Simulator (Default)

From the root `NetFort` directory, execute:

```powershell
python main.py
```

Then open your browser to:
👉 **`http://127.0.0.1:8000`**

### 3. Frontend Development Server (Optional)

If you wish to modify the React frontend with Vite hot-module replacement (HMR):

```powershell
cd frontend
npm install
npm run dev
```

The frontend will run on `http://localhost:5173` and automatically proxy API calls to the backend on port `8000`.

### 4. Legacy Desktop GUI (Optional)

If you need the legacy desktop Tkinter GUI:

```powershell
python main.py --gui
```

---

# Running Automated Tests

Run the full Python test suite (all 27 tests covering firewall engine, stateful conntrack, and REST API):

```powershell
python -m unittest discover tests
```

To test the frontend build:

```powershell
cd frontend
npm run build
```

---

## Step 2 — View Firewall Rules

The default rules are loaded from:

```text
data/rules.json
```

Example:

```text
Rule  Source IP       Destination  Port  Protocol  Action

1     192.168.1.10    *             80    TCP       ALLOW
2     192.168.1.20    *             23    TCP       BLOCK
3     *               *             443   TCP       ALLOW
4     10.0.0.5        *             *     ANY       BLOCK
```

---

## Step 3 — Enter a Packet

In the Packet Simulator section enter:

```text
Source IP:
192.168.1.10

Destination IP:
192.168.1.100

Port:
80

Protocol:
TCP
```

Click:

```text
CHECK PACKET
```

The result should be:

```text
PACKET ALLOWED
```

because it matches Rule #1.

---

# Adding Firewall Rules

Click:

```text
ADD RULE
```

Enter:

```text
Source IP:
192.168.1.50

Destination IP:
*

Port:
8080

Protocol:
TCP

Action:
BLOCK
```

Click:

```text
SAVE RULE
```

The rule will be added to the firewall and saved to:

```text
data/rules.json
```

---

# Changing Rule Priority

Select a rule and use:

```text
↑
```

or:

```text
↓
```

to change its position.

The firewall evaluates rules from top to bottom.

Therefore, moving a rule upward increases its priority relative to rules below it.

---

# Testing Packets

## Test 1 — Allowed HTTP

```text
Source:      192.168.1.10
Destination: 192.168.1.100
Port:        80
Protocol:    TCP
```

Expected:

```text
ALLOWED
```

---

## Test 2 — Blocked Telnet

```text
Source:      192.168.1.20
Destination: 192.168.1.100
Port:        23
Protocol:    TCP
```

Expected:

```text
BLOCKED
```

---

## Test 3 — Allowed HTTPS

```text
Source:      192.168.1.50
Destination: 192.168.1.100
Port:        443
Protocol:    TCP
```

Expected:

```text
ALLOWED
```

---

## Test 4 — Default Block

```text
Source:      192.168.1.50
Destination: 192.168.1.100
Port:        5555
Protocol:    TCP
```

If no rule matches:

```text
BLOCKED
```

Reason:

```text
No matching rule.
Default policy is BLOCK.
```

---

# Packet Simulation

NetFort can generate random packets.

Click:

```text
GENERATE RANDOM PACKET
```

The system will populate the packet fields automatically.

You can then click:

```text
CHECK PACKET
```

to evaluate the generated packet.

---

# Bulk Packet Simulation

Click:

```text
SIMULATE 20 PACKETS
```

NetFort generates and evaluates 20 simulated packets.

The statistics will update automatically.

For example:

```text
TOTAL PACKETS     20
ALLOWED            13
BLOCKED             7
BLOCK RATE         35%
```

This is useful for demonstrating the firewall's behavior under multiple simulated traffic conditions.

---

# Logs and Statistics

## Firewall Logs

Firewall activity is stored in:

```text
logs/firewall.log
```

Each entry contains information such as:

```text
Timestamp
Source IP
Destination IP
Port
Protocol
Action
Matched Rule
```

The GUI also displays recent log entries.

---

## Statistics

NetFort tracks:

```text
Total Packets
Allowed Packets
Blocked Packets
Block Rate
```

These statistics provide a quick overview of the firewall's activity.

---

# Running Automated Tests

NetFort includes automated tests.

From the root project directory, run:

```powershell
python -m unittest discover -s tests -v
```

The tests verify functionality such as:

* Allowed packets
* Blocked packets
* Default blocking
* Wildcard matching
* Rule priority
* Invalid IP handling
* HTTPS rule matching

A successful test run should end with:

```text
OK
```

---

# Practical Demonstration

A recommended demonstration sequence is:

## 1. Show the firewall rules

Explain:

> "The firewall evaluates traffic according to rules containing source IP, destination IP, port, protocol and action."

## 2. Demonstrate allowed traffic

Send:

```text
192.168.1.10 → Port 80 → TCP
```

Result:

```text
ALLOWED
```

## 3. Demonstrate blocked traffic

Send:

```text
192.168.1.20 → Port 23 → TCP
```

Result:

```text
BLOCKED
```

## 4. Demonstrate default policy

Send traffic to an unused port:

```text
Port 5555
```

Result:

```text
BLOCKED
```

because no rule matches.

## 5. Modify a rule

Create:

```text
8080 → BLOCK
```

Test it.

Then change it to:

```text
8080 → ALLOW
```

Test the same packet again.

The result should change accordingly.

## 6. Demonstrate rule priority

Create:

```text
192.168.1.50 → Port 80 → BLOCK
```

above:

```text
* → Port 80 → ALLOW
```

The packet should be blocked.

Move the specific blocking rule below the general allow rule.

The same packet should now be allowed.

## 7. Run bulk simulation

Click:

```text
SIMULATE 20 PACKETS
```

Then show the updated statistics and firewall logs.

---

# Example Scenarios

| Scenario            | Packet                             | Expected Result |
| ------------------- | ---------------------------------- | --------------- |
| HTTP allowed        | `192.168.1.10 : 80 TCP`            | ALLOW           |
| Telnet blocked      | `192.168.1.20 : 23 TCP`            | BLOCK           |
| HTTPS allowed       | `Any : 443 TCP`                    | ALLOW           |
| Unknown traffic     | `Any : 5555 TCP`                   | BLOCK           |
| Specific IP blocked | `10.0.0.5 : Any`                   | BLOCK           |
| Invalid IP          | `999.999.1.1`                      | BLOCK           |
| Priority rule       | Specific BLOCK above general ALLOW | BLOCK           |

---

# Security Concepts Demonstrated

NetFort demonstrates the following concepts:

```text
Firewall Principles
        ↓
Packet Filtering
        ↓
Firewall Rules
        ↓
Access Control
        ↓
Allow / Block Decisions
        ↓
Default Policy
        ↓
Rule Priority
        ↓
Logging
        ↓
Stateful Firewall Concept
```

The primary implementation is packet filtering.

Other firewall architectures such as proxy firewalls and next-generation firewalls are concepts that can be discussed as extensions, but they are not implemented as full production systems in NetFort.

---

# Why Simulated Packets Are Used

NetFort intentionally uses simulated packets instead of capturing or modifying real network traffic.

This provides several advantages:

* Safe to run on a personal computer.
* Does not modify the operating system firewall.
* Does not interfere with internet connectivity.
* Easy to reproduce test cases.
* Easy to demonstrate during a practical examination.
* Independent of network hardware.
* Deterministic and easier to debug.

NetFort is therefore an educational firewall simulator rather than a replacement for a production firewall.

---

# Limitations

NetFort is designed for educational demonstration and has several limitations.

### 1. No real packet interception

The system does not inspect actual packets travelling through the computer's network interface.

### 2. No OS firewall integration

NetFort does not modify Windows Firewall, Linux `iptables`/`nftables`, or any other host firewall.

### 3. Limited state tracking

The stateful firewall component is a simplified educational implementation.

### 4. No deep packet inspection

The system evaluates packet metadata rather than packet payload contents.

### 5. No production-grade threat detection

NetFort does not attempt to replace commercial firewalls, IDS/IPS systems or enterprise network-security platforms.

---

# Future Enhancements

Possible future versions could include:

* Real packet capture using a controlled test environment.
* CIDR/subnet-based rules.
* MAC-address filtering.
* ICMP-specific filtering.
* Time-based firewall rules.
* User authentication.
* Role-based access control.
* Advanced connection tracking.
* Intrusion detection features.
* Port-scan detection.
* Suspicious traffic detection.
* Rule import/export.
* Database-backed rule management.
* Advanced analytics.
* Network topology visualization.
* Proxy firewall simulation.
* Next-Generation Firewall feature simulation.

These features should be considered extensions rather than requirements for the core project.

---

# Technology Stack

| Technology              | Purpose                   |
| ----------------------- | ------------------------- |
| Python                  | Core programming language |
| Tkinter                 | Graphical user interface  |
| JSON                    | Firewall rule persistence |
| Python Logging/File I/O | Firewall logs             |
| unittest                | Automated testing         |
| Git                     | Version control           |
| GitHub                  | Source-code hosting       |

---

# Safety Notice

NetFort is an educational network-security simulator.

It does not:

* Modify the computer's firewall.
* Disable network security controls.
* Intercept real traffic.
* Inject packets into a network.
* Perform attacks against external systems.

All traffic used by the core simulator is generated and evaluated internally by the application.

Only use any future real-network extensions in systems and networks for which you have explicit authorization.

---

# Conclusion

NetFort provides a practical way to understand fundamental firewall and network-security concepts through simulation.

The project combines:

```text
Packet Representation
        +
Firewall Rules
        +
Packet Filtering
        +
Access Control
        +
Rule Priority
        +
Default Deny
        +
Logging
        +
Statistics
        +
Stateful Firewall Simulation
```

into a single desktop application.

The main principle can be summarized as:

```text
             PACKET
                |
                v
        ┌───────────────┐
        │ FIREWALL      │
        │ RULE MATCHING │
        └───────┬───────┘
                |
       ┌────────┴────────┐
       |                 |
     MATCH            NO MATCH
       |                 |
       v                 v
 RULE ACTION        DEFAULT BLOCK
       |                 |
       └────────┬────────┘
                |
                v
          ALLOW / BLOCK
                |
        ┌───────┴───────┐
        v               v
       LOG          STATISTICS
```

**NetFort's primary goal is not to build a production firewall, but to provide a clear, safe and practical demonstration of how firewall-based network traffic control works.**

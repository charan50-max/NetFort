import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import random
import os

from firewall.packet import Packet
from firewall.rules import FirewallRule, RuleManager
from firewall.engine import FirewallEngine


class FirewallGUI:

    def __init__(self):

        self.root = tk.Tk()

        self.root.title(
            "NetFort - Network Traffic Security & Access Control"
        )

        self.root.geometry("1200x820")
        self.root.minsize(1000, 740)

        self.root.configure(bg="#0f172a")

        # Backend
        self.rule_manager = RuleManager(
            "data/rules.json"
        )

        self.engine = FirewallEngine(
            self.rule_manager
        )

        self.setup_style()
        self.create_variables()
        self.create_gui()

        self.refresh_rules()
        self.update_statistics()
        self.refresh_connections()

        # Refresh once per second so connection timers count down
        self.root.after(1000, self.tick)

    # =========================================================
    # STYLE
    # =========================================================

    def setup_style(self):

        style = ttk.Style()

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "TButton",
            font=("Segoe UI", 10, "bold"),
            padding=8
        )

        style.configure(
            "TLabel",
            background="#0f172a",
            foreground="#e2e8f0",
            font=("Segoe UI", 10)
        )

        style.configure(
            "Treeview",
            background="#1e293b",
            foreground="#e2e8f0",
            fieldbackground="#1e293b",
            rowheight=28,
            font=("Segoe UI", 9)
        )

        style.configure(
            "Treeview.Heading",
            background="#334155",
            foreground="white",
            font=("Segoe UI", 9, "bold")
        )

    # =========================================================
    # VARIABLES
    # =========================================================

    def create_variables(self):

        self.source_ip_var = tk.StringVar(
            value="192.168.1.20"
        )

        self.destination_ip_var = tk.StringVar(
            value="192.168.1.100"
        )

        self.port_var = tk.StringVar(
            value="23"
        )

        # Optional. Empty = stateless packet (no connection tracking)
        self.source_port_var = tk.StringVar(
            value=""
        )

        self.stateful_var = tk.BooleanVar(
            value=True
        )

        self.protocol_var = tk.StringVar(
            value="TCP"
        )

        self.rule_source_var = tk.StringVar(
            value="*"
        )

        self.rule_destination_var = tk.StringVar(
            value="*"
        )

        self.rule_port_var = tk.StringVar(
            value="*"
        )

        self.rule_protocol_var = tk.StringVar(
            value="TCP"
        )

        self.rule_action_var = tk.StringVar(
            value="BLOCK"
        )

        self.status_var = tk.StringVar(
            value="FIREWALL ACTIVE"
        )

    # =========================================================
    # MAIN GUI
    # =========================================================

    def create_gui(self):

        # ---------------- HEADER ----------------

        header = tk.Frame(
            self.root,
            bg="#111827",
            height=75
        )

        header.pack(
            fill="x"
        )

        title = tk.Label(
            header,
            text="NETFORT",
            bg="#111827",
            fg="#38bdf8",
            font=("Segoe UI", 24, "bold")
        )

        title.pack(
            side="left",
            padx=25,
            pady=15
        )

        subtitle = tk.Label(
            header,
            text="Network Traffic Security & Access Control Simulator",
            bg="#111827",
            fg="#94a3b8",
            font=("Segoe UI", 10)
        )

        subtitle.pack(
            side="left",
            padx=10
        )

        status = tk.Label(
            header,
            textvariable=self.status_var,
            bg="#14532d",
            fg="#bbf7d0",
            font=("Segoe UI", 9, "bold"),
            padx=12,
            pady=6
        )

        status.pack(
            side="right",
            padx=20
        )

        # ---------------- MAIN CONTAINER ----------------

        main = tk.Frame(
            self.root,
            bg="#0f172a"
        )

        main.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15
        )

        # Left panel
        left = tk.Frame(
            main,
            bg="#1e293b"
        )

        left.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 8)
        )

        # Right panel
        right = tk.Frame(
            main,
            bg="#1e293b"
        )

        right.pack(
            side="right",
            fill="both",
            expand=True,
            padx=(8, 0)
        )

        self.create_packet_panel(left)
        self.create_statistics_panel(left)
        self.create_rule_panel(right)
        self.create_connection_panel(right)
        self.create_log_panel(right)

    # =========================================================
    # PACKET PANEL
    # =========================================================

    def create_packet_panel(self, parent):

        frame = tk.LabelFrame(
            parent,
            text="  PACKET SIMULATOR  ",
            bg="#1e293b",
            fg="#38bdf8",
            font=("Segoe UI", 12, "bold"),
            padx=12,
            pady=8
        )

        frame.pack(
            fill="x",
            padx=12,
            pady=12
        )

        self.add_entry(
            frame,
            "Source IP",
            self.source_ip_var,
            0
        )

        self.add_entry(
            frame,
            "Destination IP",
            self.destination_ip_var,
            1
        )

        self.add_entry(
            frame,
            "Destination Port",
            self.port_var,
            2
        )

        self.add_entry(
            frame,
            "Source Port (optional)",
            self.source_port_var,
            3
        )

        tk.Label(
            frame,
            text="Protocol",
            bg="#1e293b",
            fg="#cbd5e1"
        ).grid(
            row=4,
            column=0,
            sticky="w",
            pady=4
        )

        protocol_combo = ttk.Combobox(
            frame,
            textvariable=self.protocol_var,
            values=["TCP", "UDP", "ICMP"],
            state="readonly",
            width=25
        )

        protocol_combo.grid(
            row=4,
            column=1,
            sticky="ew",
            pady=4
        )

        check_button = tk.Button(
            frame,
            text="CHECK PACKET",
            command=self.check_packet,
            bg="#0284c7",
            fg="white",
            activebackground="#0369a1",
            activeforeground="white",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            cursor="hand2",
            pady=8
        )

        check_button.grid(
            row=5,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(10, 4)
        )

        generate_button = tk.Button(
            frame,
            text="GENERATE RANDOM PACKET",
            command=self.generate_random_packet,
            bg="#475569",
            fg="white",
            activebackground="#334155",
            relief="flat",
            cursor="hand2",
            pady=8
        )

        generate_button.grid(
            row=6,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=5
        )

        reply_button = tk.Button(
            frame,
            text="SWAP TO REPLY PACKET",
            command=self.swap_to_reply,
            bg="#0f766e",
            fg="white",
            activebackground="#115e59",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            pady=8
        )

        reply_button.grid(
            row=7,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=5
        )

        self.result_label = tk.Label(
            frame,
            text="READY",
            bg="#334155",
            fg="#e2e8f0",
            font=("Segoe UI", 16, "bold"),
            pady=10
        )

        self.result_label.grid(
            row=8,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(10, 0)
        )

        self.reason_label = tk.Label(
            frame,
            text="Enter packet information and click CHECK PACKET.",
            bg="#1e293b",
            fg="#94a3b8",
            wraplength=400,
            justify="center"
        )

        self.reason_label.grid(
            row=9,
            column=0,
            columnspan=2,
            pady=6
        )

        frame.columnconfigure(
            1,
            weight=1
        )

    def add_entry(
        self,
        parent,
        label_text,
        variable,
        row
    ):

        tk.Label(
            parent,
            text=label_text,
            bg="#1e293b",
            fg="#cbd5e1"
        ).grid(
            row=row,
            column=0,
            sticky="w",
            pady=4
        )

        entry = tk.Entry(
            parent,
            textvariable=variable,
            bg="#0f172a",
            fg="#e2e8f0",
            insertbackground="white",
            relief="flat",
            font=("Consolas", 10)
        )

        entry.grid(
            row=row,
            column=1,
            sticky="ew",
            pady=7,
            ipady=4
        )

    # =========================================================
    # STATISTICS
    # =========================================================

    def create_statistics_panel(self, parent):

        frame = tk.LabelFrame(
            parent,
            text="  FIREWALL STATISTICS  ",
            bg="#1e293b",
            fg="#38bdf8",
            font=("Segoe UI", 12, "bold"),
            padx=10,
            pady=10
        )

        frame.pack(
            fill="x",
            padx=12,
            pady=12
        )

        self.total_label = self.create_stat(
            frame,
            "TOTAL",
            0
        )

        self.allowed_label = self.create_stat(
            frame,
            "ALLOWED",
            1
        )

        self.blocked_label = self.create_stat(
            frame,
            "BLOCKED",
            2
        )

        self.rate_label = self.create_stat(
            frame,
            "BLOCK RATE",
            3
        )

        self.connections_label = self.create_stat(
            frame,
            "CONNECTIONS",
            4
        )

    def create_stat(
        self,
        parent,
        title,
        column
    ):

        frame = tk.Frame(
            parent,
            bg="#0f172a",
            padx=10,
            pady=8
        )

        frame.grid(
            row=0,
            column=column,
            sticky="ew",
            padx=4
        )

        tk.Label(
            frame,
            text=title,
            bg="#0f172a",
            fg="#94a3b8",
            font=("Segoe UI", 8, "bold")
        ).pack()

        value = tk.Label(
            frame,
            text="0",
            bg="#0f172a",
            fg="#e2e8f0",
            font=("Segoe UI", 16, "bold")
        )

        value.pack()

        parent.columnconfigure(
            column,
            weight=1
        )

        return value

    # =========================================================
    # CONNECTION PANEL (STATEFUL FIREWALL)
    # =========================================================

    def create_connection_panel(self, parent):

        frame = tk.LabelFrame(
            parent,
            text="  TRACKED CONNECTIONS  ",
            bg="#1e293b",
            fg="#38bdf8",
            font=("Segoe UI", 12, "bold"),
            padx=10,
            pady=10
        )

        frame.pack(
            fill="x",
            padx=12,
            pady=(0, 12)
        )

        columns = (
            "initiator",
            "responder",
            "protocol",
            "state",
            "expires",
            "packets"
        )

        self.connection_tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
            height=3
        )

        headings = {
            "initiator": "INITIATOR",
            "responder": "RESPONDER",
            "protocol": "PROTO",
            "state": "STATE",
            "expires": "EXPIRES",
            "packets": "PKTS F/R"
        }

        widths = {
            "initiator": 135,
            "responder": 135,
            "protocol": 45,
            "state": 88,
            "expires": 62,
            "packets": 70
        }

        for column in columns:

            self.connection_tree.heading(
                column,
                text=headings[column]
            )

            self.connection_tree.column(
                column,
                width=widths[column],
                anchor="center"
            )

        self.connection_tree.pack(
            fill="x"
        )

        button_frame = tk.Frame(
            frame,
            bg="#1e293b"
        )

        button_frame.pack(
            fill="x",
            pady=(8, 0)
        )

        tk.Checkbutton(
            button_frame,
            text="Stateful tracking enabled",
            variable=self.stateful_var,
            command=self.toggle_stateful,
            bg="#1e293b",
            fg="#e2e8f0",
            selectcolor="#0f172a",
            activebackground="#1e293b",
            activeforeground="#e2e8f0"
        ).pack(
            side="left"
        )

        tk.Button(
            button_frame,
            text="CLEAR CONNECTIONS",
            command=self.clear_connections_clicked,
            bg="#475569",
            fg="white",
            relief="flat",
            padx=12,
            pady=6
        ).pack(
            side="right"
        )

    def refresh_connections(self):

        for item in self.connection_tree.get_children():

            self.connection_tree.delete(item)

        stateful = self.engine.stateful

        for connection in stateful.get_connections():

            remaining = max(
                0,
                int(stateful.seconds_remaining(connection))
            )

            self.connection_tree.insert(
                "",
                "end",
                values=(
                    f"{connection.source_ip}:{connection.source_port}",
                    f"{connection.destination_ip}:{connection.destination_port}",
                    connection.protocol,
                    connection.state,
                    f"{remaining}s",
                    f"{connection.forward_packets} / "
                    f"{connection.reply_packets}"
                )
            )

    def tick(self):

        self.update_statistics()
        self.refresh_connections()

        self.root.after(1000, self.tick)

    def toggle_stateful(self):

        enabled = self.stateful_var.get()

        self.engine.stateful_enabled = enabled

        if not enabled:
            # Do not let old connections come back to life later
            self.engine.reset_connections()

        self.status_var.set(
            "FIREWALL ACTIVE"
            if enabled
            else "FIREWALL ACTIVE (STATELESS)"
        )

        self.refresh_connections()
        self.update_statistics()

    def clear_connections_clicked(self):

        self.engine.reset_connections()

        self.refresh_connections()
        self.update_statistics()

    def rules_changed(self):
        """
        Called after a rule is added, deleted or moved.
        Forget tracked connections so old connections cannot
        outlive the rules that originally allowed them.
        """

        self.refresh_rules()

        self.engine.reset_connections()

        self.refresh_connections()
        self.update_statistics()

    def swap_to_reply(self):
        """
        Turn the packet in the form into its reply:
        source and destination swap places, ports too.
        """

        source_port = self.source_port_var.get().strip()

        if not source_port:

            messagebox.showinfo(
                "Source Port Needed",
                "Enter a source port first. A reply can only be "
                "built for a packet that has one."
            )

            return

        source_ip = self.source_ip_var.get()
        destination_ip = self.destination_ip_var.get()
        port = self.port_var.get()

        self.source_ip_var.set(destination_ip)
        self.destination_ip_var.set(source_ip)

        self.port_var.set(source_port)
        self.source_port_var.set(port)

    def build_packet(self):
        """
        Build a Packet from the form fields.
        Returns None (after showing an error) if input is bad.
        """

        try:
            port = int(
                self.port_var.get().strip()
            )

        except ValueError:

            messagebox.showerror(
                "Invalid Port",
                "Destination port must be a number."
            )

            return None

        source_port_text = self.source_port_var.get().strip()

        source_port = None

        if source_port_text:

            try:
                source_port = int(source_port_text)

            except ValueError:

                messagebox.showerror(
                    "Invalid Source Port",
                    "Source port must be a number "
                    "(or leave it empty)."
                )

                return None

        return Packet(
            source_ip=self.source_ip_var.get(),
            destination_ip=self.destination_ip_var.get(),
            port=port,
            protocol=self.protocol_var.get(),
            source_port=source_port
        )

    # =========================================================
    # RULE PANEL
    # =========================================================

    def create_rule_panel(self, parent):

        frame = tk.LabelFrame(
            parent,
            text="  FIREWALL RULES  ",
            bg="#1e293b",
            fg="#38bdf8",
            font=("Segoe UI", 12, "bold"),
            padx=10,
            pady=10
        )

        frame.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=12
        )

        columns = (
            "id",
            "source",
            "destination",
            "port",
            "protocol",
            "action"
        )

        self.rule_tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
            height=5
        )

        headings = {
            "id": "#",
            "source": "SOURCE IP",
            "destination": "DESTINATION",
            "port": "PORT",
            "protocol": "PROTOCOL",
            "action": "ACTION"
        }

        widths = {
            "id": 35,
            "source": 115,
            "destination": 115,
            "port": 60,
            "protocol": 75,
            "action": 75
        }

        for column in columns:

            self.rule_tree.heading(
                column,
                text=headings[column]
            )

            self.rule_tree.column(
                column,
                width=widths[column],
                anchor="center"
            )

        self.rule_tree.pack(
            fill="both",
            expand=True
        )

        # Buttons

        button_frame = tk.Frame(
            frame,
            bg="#1e293b"
        )

        button_frame.pack(
            fill="x",
            pady=10
        )

        tk.Button(
            button_frame,
            text="ADD RULE",
            command=self.add_rule_dialog,
            bg="#16a34a",
            fg="white",
            relief="flat",
            padx=12,
            pady=7
        ).pack(
            side="left",
            padx=3
        )

        tk.Button(
            button_frame,
            text="DELETE RULE",
            command=self.delete_selected_rule,
            bg="#dc2626",
            fg="white",
            relief="flat",
            padx=12,
            pady=7
        ).pack(
            side="left",
            padx=3
        )

        tk.Button(
            button_frame,
            text="↑",
            command=self.move_rule_up,
            bg="#475569",
            fg="white",
            relief="flat",
            padx=12,
            pady=7
        ).pack(
            side="left",
            padx=3
        )

        tk.Button(
            button_frame,
            text="↓",
            command=self.move_rule_down,
            bg="#475569",
            fg="white",
            relief="flat",
            padx=12,
            pady=7
        ).pack(
            side="left",
            padx=3
        )

    # =========================================================
    # LOG PANEL
    # =========================================================

    def create_log_panel(self, parent):

        frame = tk.LabelFrame(
            parent,
            text="  FIREWALL LOG  ",
            bg="#1e293b",
            fg="#38bdf8",
            font=("Segoe UI", 12, "bold"),
            padx=10,
            pady=10
        )

        frame.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=(0, 12)
        )

        self.log_text = tk.Text(
            frame,
            height=7,
            bg="#020617",
            fg="#cbd5e1",
            insertbackground="white",
            font=("Consolas", 9),
            relief="flat",
            state="disabled"
        )

        self.log_text.pack(
            fill="both",
            expand=True
        )

        button_frame = tk.Frame(
            frame,
            bg="#1e293b"
        )

        button_frame.pack(
            fill="x",
            pady=8
        )

        tk.Button(
            button_frame,
            text="CLEAR LOG",
            command=self.clear_log,
            bg="#475569",
            fg="white",
            relief="flat",
            padx=15,
            pady=6
        ).pack(
            side="left"
        )

        tk.Button(
            button_frame,
            text="SIMULATE 20 PACKETS",
            command=self.simulate_packets,
            bg="#7c3aed",
            fg="white",
            relief="flat",
            padx=15,
            pady=6
        ).pack(
            side="right"
        )

    # =========================================================
    # PACKET CHECKING
    # =========================================================

    def check_packet(self):

        packet = self.build_packet()

        if packet is None:
            return

        result = self.engine.evaluate(packet)

        self.display_result(
            packet,
            result
        )

        self.write_log(
            packet,
            result
        )

        self.update_statistics()
        self.refresh_connections()

    # =========================================================
    # DISPLAY RESULT
    # =========================================================

    def display_result(
        self,
        packet,
        result
    ):

        action = result["action"]
        state = result.get("connection_state")

        if action == "ALLOW":

            self.result_label.config(
                text="\u2713 PACKET ALLOWED",
                bg="#166534",
                fg="#dcfce7"
            )

        else:

            self.result_label.config(
                text="\u2717 PACKET BLOCKED",
                bg="#991b1b",
                fg="#fee2e2"
            )

        rule = result["matched_rule"]

        if rule:
            rule_text = (
                f"Matched Rule: #{rule}"
            )

        elif state == "ESTABLISHED":
            rule_text = (
                "Matched Rule: None "
                "(allowed by connection tracking)"
            )

        else:
            rule_text = (
                "Matched Rule: None"
            )

        lines = [
            rule_text,
            f"Reason: {result['reason']}"
        ]

        if state == "NEW":
            lines.append(
                "Connection: NEW - replies to this packet "
                "will now be allowed"
            )

        elif state == "ESTABLISHED":
            lines.append(
                "Connection: ESTABLISHED"
            )

        self.reason_label.config(
            text="\n".join(lines)
        )

    # =========================================================
    # RANDOM PACKET
    # =========================================================

    def generate_random_packet(self):

        source_ips = [
            "192.168.1.10",
            "192.168.1.20",
            "192.168.1.50",
            "192.168.1.77",
            "10.0.0.5",
            "10.0.0.25"
        ]

        destination_ips = [
            "192.168.1.100",
            "192.168.1.200",
            "10.0.0.100"
        ]

        ports = [
            21,
            22,
            23,
            53,
            80,
            443,
            8080,
            3389,
            5555
        ]

        protocols = [
            "TCP",
            "UDP",
            "ICMP"
        ]

        self.source_ip_var.set(
            random.choice(source_ips)
        )

        self.destination_ip_var.set(
            random.choice(destination_ips)
        )

        self.port_var.set(
            str(random.choice(ports))
        )

        protocol = random.choice(protocols)

        self.protocol_var.set(protocol)

        if protocol == "ICMP":
            self.source_port_var.set("")
        else:
            self.source_port_var.set(
                str(random.randint(1024, 65535))
            )

    # =========================================================
    # SIMULATE MULTIPLE PACKETS
    # =========================================================

    def simulate_packets(self):

        for _ in range(20):

            source_ips = [
                "192.168.1.10",
                "192.168.1.20",
                "192.168.1.50",
                "192.168.1.70",
                "10.0.0.5",
                "10.0.0.20"
            ]

            destinations = [
                "192.168.1.100",
                "192.168.1.200"
            ]

            ports = [
                21,
                22,
                23,
                53,
                80,
                443,
                8080,
                3389,
                5555
            ]

            protocols = [
                "TCP",
                "UDP",
                "ICMP"
            ]

            existing = self.engine.stateful.get_connections()

            if existing and random.random() < 0.3:

                # Send the REPLY of a connection that is already
                # tracked, to show stateful matching in action
                connection = random.choice(existing)

                packet = Packet(
                    source_ip=connection.destination_ip,
                    destination_ip=connection.source_ip,
                    port=connection.source_port,
                    protocol=connection.protocol,
                    source_port=connection.destination_port
                )

            else:

                protocol = random.choice(protocols)

                packet = Packet(
                    source_ip=random.choice(source_ips),
                    destination_ip=random.choice(destinations),
                    port=random.choice(ports),
                    protocol=protocol,
                    source_port=(
                        None
                        if protocol == "ICMP"
                        else random.randint(1024, 65535)
                    )
                )

            result = self.engine.evaluate(
                packet
            )

            self.write_log(
                packet,
                result
            )

        self.update_statistics()
        self.refresh_connections()

        messagebox.showinfo(
            "Simulation Complete",
            "20 simulated packets were processed."
        )

    # =========================================================
    # RULE REFRESH
    # =========================================================

    def refresh_rules(self):

        for item in self.rule_tree.get_children():

            self.rule_tree.delete(item)

        for index, rule in enumerate(
            self.rule_manager.rules,
            start=1
        ):

            self.rule_tree.insert(
                "",
                "end",
                values=(
                    index,
                    rule.source_ip,
                    rule.destination_ip,
                    rule.port,
                    rule.protocol,
                    rule.action
                )
            )

    # =========================================================
    # ADD RULE
    # =========================================================

    def add_rule_dialog(self):

        dialog = tk.Toplevel(
            self.root
        )

        dialog.title(
            "Add Firewall Rule"
        )

        dialog.geometry(
            "420x420"
        )

        dialog.configure(
            bg="#1e293b"
        )

        dialog.transient(
            self.root
        )

        dialog.grab_set()

        variables = {
            "source": tk.StringVar(value="*"),
            "destination": tk.StringVar(value="*"),
            "port": tk.StringVar(value="*"),
            "protocol": tk.StringVar(value="TCP"),
            "action": tk.StringVar(value="BLOCK")
        }

        fields = [
            ("Source IP", "source"),
            ("Destination IP", "destination"),
            ("Port", "port")
        ]

        for row, (label, key) in enumerate(fields):

            tk.Label(
                dialog,
                text=label,
                bg="#1e293b",
                fg="#cbd5e1"
            ).grid(
                row=row,
                column=0,
                padx=20,
                pady=12,
                sticky="w"
            )

            tk.Entry(
                dialog,
                textvariable=variables[key],
                bg="#0f172a",
                fg="white",
                insertbackground="white",
                relief="flat"
            ).grid(
                row=row,
                column=1,
                padx=20,
                pady=12,
                ipady=6
            )

        # Protocol

        tk.Label(
            dialog,
            text="Protocol",
            bg="#1e293b",
            fg="#cbd5e1"
        ).grid(
            row=3,
            column=0,
            padx=20,
            pady=12,
            sticky="w"
        )

        ttk.Combobox(
            dialog,
            textvariable=variables["protocol"],
            values=["TCP", "UDP", "ICMP", "ANY"],
            state="readonly"
        ).grid(
            row=3,
            column=1,
            padx=20,
            pady=12
        )

        # Action

        tk.Label(
            dialog,
            text="Action",
            bg="#1e293b",
            fg="#cbd5e1"
        ).grid(
            row=4,
            column=0,
            padx=20,
            pady=12,
            sticky="w"
        )

        ttk.Combobox(
            dialog,
            textvariable=variables["action"],
            values=["ALLOW", "BLOCK"],
            state="readonly"
        ).grid(
            row=4,
            column=1,
            padx=20,
            pady=12
        )

        def save_rule():

            rule = FirewallRule(
                source_ip=variables["source"].get(),
                destination_ip=variables["destination"].get(),
                port=variables["port"].get(),
                protocol=variables["protocol"].get(),
                action=variables["action"].get()
            )

            success, message = (
                self.rule_manager.add_rule(rule)
            )

            if success:

                self.rules_changed()

                dialog.destroy()

                messagebox.showinfo(
                    "Success",
                    message
                )

            else:

                messagebox.showerror(
                    "Invalid Rule",
                    message
                )

        tk.Button(
            dialog,
            text="SAVE RULE",
            command=save_rule,
            bg="#16a34a",
            fg="white",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=20,
            pady=8
        ).grid(
            row=5,
            column=0,
            columnspan=2,
            pady=20
        )

    # =========================================================
    # DELETE RULE
    # =========================================================

    def delete_selected_rule(self):

        selected = self.rule_tree.selection()

        if not selected:

            messagebox.showwarning(
                "No Selection",
                "Select a rule first."
            )

            return

        item = selected[0]

        values = self.rule_tree.item(
            item,
            "values"
        )

        rule_number = int(
            values[0]
        )

        confirm = messagebox.askyesno(
            "Delete Rule",
            f"Delete Rule #{rule_number}?"
        )

        if not confirm:
            return

        success, message = (
            self.rule_manager.delete_rule(
                rule_number - 1
            )
        )

        if success:

            self.rules_changed()

            messagebox.showinfo(
                "Deleted",
                message
            )

    # =========================================================
    # MOVE RULE UP
    # =========================================================

    def move_rule_up(self):

        selected = self.rule_tree.selection()

        if not selected:
            return

        item = selected[0]

        values = self.rule_tree.item(
            item,
            "values"
        )

        index = int(values[0]) - 1

        if self.rule_manager.move_rule_up(index):

            self.rules_changed()

    # =========================================================
    # MOVE RULE DOWN
    # =========================================================

    def move_rule_down(self):

        selected = self.rule_tree.selection()

        if not selected:
            return

        item = selected[0]

        values = self.rule_tree.item(
            item,
            "values"
        )

        index = int(values[0]) - 1

        if self.rule_manager.move_rule_down(index):

            self.rules_changed()

    # =========================================================
    # LOGGING
    # =========================================================

    def write_log(
        self,
        packet,
        result
    ):

        os.makedirs(
            "logs",
            exist_ok=True
        )

        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        rule = result["matched_rule"]
        state = result.get("connection_state")

        if rule:
            rule_text = f"RULE#{rule}"
        elif state == "ESTABLISHED":
            rule_text = "STATE"
        else:
            rule_text = "DEFAULT"

        sport_text = (
            "-"
            if packet.source_port is None
            else str(packet.source_port)
        )

        line = (
            f"{timestamp} | "
            f"SRC={packet.source_ip} | "
            f"SPORT={sport_text} | "
            f"DST={packet.destination_ip} | "
            f"PORT={packet.port} | "
            f"PROTO={packet.protocol} | "
            f"ACTION={result['action']} | "
            f"{rule_text}"
            + (f" | CONN={state}" if state else "")
            + "\n"
        )

        with open(
            "logs/firewall.log",
            "a",
            encoding="utf-8"
        ) as file:

            file.write(line)

        self.log_text.config(
            state="normal"
        )

        self.log_text.insert(
            "end",
            line
        )

        self.log_text.see(
            "end"
        )

        self.log_text.config(
            state="disabled"
        )

    # =========================================================
    # CLEAR LOG
    # =========================================================

    def clear_log(self):

        self.log_text.config(
            state="normal"
        )

        self.log_text.delete(
            "1.0",
            "end"
        )

        self.log_text.config(
            state="disabled"
        )

    # =========================================================
    # STATISTICS UPDATE
    # =========================================================

    def update_statistics(self):

        stats = (
            self.engine.get_statistics()
        )

        self.total_label.config(
            text=str(stats["total"])
        )

        self.allowed_label.config(
            text=str(stats["allowed"])
        )

        self.blocked_label.config(
            text=str(stats["blocked"])
        )

        self.rate_label.config(
            text=f"{stats['block_rate']:.1f}%"
        )

        self.connections_label.config(
            text=str(stats["active_connections"])
        )

    # =========================================================
    # RUN
    # =========================================================

    def run(self):

        self.root.mainloop()
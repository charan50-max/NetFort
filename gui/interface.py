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

        self.root.geometry("1200x780")
        self.root.minsize(1000, 700)

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
            padx=15,
            pady=15
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
            "Port",
            self.port_var,
            2
        )

        tk.Label(
            frame,
            text="Protocol",
            bg="#1e293b",
            fg="#cbd5e1"
        ).grid(
            row=3,
            column=0,
            sticky="w",
            pady=7
        )

        protocol_combo = ttk.Combobox(
            frame,
            textvariable=self.protocol_var,
            values=["TCP", "UDP", "ICMP"],
            state="readonly",
            width=25
        )

        protocol_combo.grid(
            row=3,
            column=1,
            sticky="ew",
            pady=7
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
            pady=10
        )

        check_button.grid(
            row=4,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(15, 5)
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
            row=5,
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
            pady=15
        )

        self.result_label.grid(
            row=6,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(15, 0)
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
            row=7,
            column=0,
            columnspan=2,
            pady=10
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
            pady=7
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
            ipady=7
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
            height=10
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
            height=10,
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

        try:
            port = int(
                self.port_var.get().strip()
            )

        except ValueError:
            messagebox.showerror(
                "Invalid Port",
                "Port must be a number."
            )

            return

        packet = Packet(
            source_ip=self.source_ip_var.get(),
            destination_ip=self.destination_ip_var.get(),
            port=port,
            protocol=self.protocol_var.get()
        )

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

    # =========================================================
    # DISPLAY RESULT
    # =========================================================

    def display_result(
        self,
        packet,
        result
    ):

        action = result["action"]

        if action == "ALLOW":

            self.result_label.config(
                text="✓ PACKET ALLOWED",
                bg="#166534",
                fg="#dcfce7"
            )

        else:

            self.result_label.config(
                text="✗ PACKET BLOCKED",
                bg="#991b1b",
                fg="#fee2e2"
            )

        rule = result["matched_rule"]

        if rule:
            rule_text = (
                f"Matched Rule: #{rule}"
            )

        else:
            rule_text = (
                "Matched Rule: None"
            )

        self.reason_label.config(
            text=(
                f"{rule_text}\n"
                f"Reason: {result['reason']}"
            )
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

        self.protocol_var.set(
            random.choice(protocols)
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

            packet = Packet(
                source_ip=random.choice(source_ips),
                destination_ip=random.choice(destinations),
                port=random.choice(ports),
                protocol=random.choice(protocols)
            )

            result = self.engine.evaluate(
                packet
            )

            self.write_log(
                packet,
                result
            )

        self.update_statistics()

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

                self.refresh_rules()

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

            self.refresh_rules()

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

            self.refresh_rules()

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

            self.refresh_rules()

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

        rule_text = (
            f"RULE#{rule}"
            if rule
            else "DEFAULT"
        )

        line = (
            f"{timestamp} | "
            f"SRC={packet.source_ip} | "
            f"DST={packet.destination_ip} | "
            f"PORT={packet.port} | "
            f"PROTO={packet.protocol} | "
            f"ACTION={result['action']} | "
            f"{rule_text}\n"
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

    # =========================================================
    # RUN
    # =========================================================

    def run(self):

        self.root.mainloop()
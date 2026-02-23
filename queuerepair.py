import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
from pathlib import Path
import csv
from collections import Counter

class QueueRepairApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QueueRepair - IT Repair Tracker")
        self.root.geometry("1000x700")
        self.root.configure(bg="#d4d0c8")
        
        # Data setup
        self.data_dir = Path("QueueRepairData")
        self.data_file = self.data_dir / "repair_data.json"
        self.data_dir.mkdir(exist_ok=True)
        
        self.devices = self.load_data()
        self.create_widgets()
        self.setup_keyboard_shortcuts()
        self.create_context_menu()

    def load_data(self):
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except json.JSONDecodeError:
            messagebox.showwarning("Warning", "Data file is corrupted. Starting with empty data.")
            return []
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")
            return []

    def save_data(self):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.devices, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {str(e)}")

    def setup_keyboard_shortcuts(self):
        self.root.bind('<Control-n>', lambda e: self.add_device())
        self.root.bind('<Control-f>', lambda e: self.search_entry.focus())
        self.root.bind('<Delete>', lambda e: self.delete_device())
        self.root.bind('<Control-e>', lambda e: self.export_to_csv())
        self.root.bind('<Control-d>', lambda e: self.show_dashboard())
        self.root.bind('<Escape>', lambda e: self.search_entry.delete(0, tk.END) or self.filter_devices())

    def create_context_menu(self):
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="Mark Repaired", command=self.mark_repaired)
        self.context_menu.add_command(label="Cancel Repair", command=self.cancel_repair)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Copy Details", command=self.copy_details)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Delete", command=self.delete_device)
        
        self.tree.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def copy_details(self):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            values = item['values']
            details = f"ID: {values[0]}\nDevice: {values[1]}\nSerial: {values[2]}\nIssue: {values[3]}\nStatus: {values[6]}"
            self.root.clipboard_clear()
            self.root.clipboard_append(details)
            self.status_var.set("Details copied to clipboard")

    def create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self.root, bd=1, relief="sunken", bg="#d4d0c8")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_frame = tk.Frame(main_frame, bg="#d4d0c8")
        title_frame.pack(fill=tk.X, pady=(10, 5))
        
        tk.Label(title_frame, text="QueueRepair - IT Repair Tracker", 
                font=("Arial", 16, "bold"), bg="#d4d0c8").pack(side=tk.LEFT, padx=10)
        
        # Dashboard button
        self.dashboard_btn = ttk.Button(title_frame, text="Dashboard", command=self.show_dashboard)
        self.dashboard_btn.pack(side=tk.RIGHT, padx=10)
        
        # Search frame
        search_frame = tk.Frame(main_frame, bg="#d4d0c8")
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(search_frame, text="Search:", bg="#d4d0c8", font=("Arial", 10)).pack(side=tk.LEFT)
        self.search_entry = tk.Entry(search_frame, width=40, relief="sunken", font=("Arial", 10))
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<KeyRelease>", self.filter_devices)
        
        dash_export_frame = tk.Frame(main_frame, bg="#d4d0c8")
        dash_export_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(dash_export_frame, bg="#d4d0c8")

        # Export button
        self.export_btn = ttk.Button(title_frame, text="Export CSV", command=self.export_to_csv)
        self.export_btn.pack(side=tk.RIGHT, padx=10)
        
        # Form frame
        form_frame = tk.Frame(main_frame, bg="#d4d0c8")
        form_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Form fields
        tk.Label(form_frame, text="Device Name:", bg="#d4d0c8", font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.device_entry = tk.Entry(form_frame, width=30, relief="sunken", font=("Arial", 10))
        self.device_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(form_frame, text="Serial Number:", bg="#d4d0c8", font=("Arial", 10)).grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.serial_entry = tk.Entry(form_frame, width=20, relief="sunken", font=("Arial", 10))
        self.serial_entry.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(form_frame, text="Issue Description:", bg="#d4d0c8", font=("Arial", 10)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.issue_entry = tk.Entry(form_frame, width=30, relief="sunken", font=("Arial", 10))
        self.issue_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(form_frame, text="Submitted By:", bg="#d4d0c8", font=("Arial", 10)).grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.submitted_entry = tk.Entry(form_frame, width=20, relief="sunken", font=("Arial", 10))
        self.submitted_entry.grid(row=1, column=3, padx=5, pady=5)
        
        tk.Label(form_frame, text="Contact Info:", bg="#d4d0c8", font=("Arial", 10)).grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.contact_entry = tk.Entry(form_frame, width=30, relief="sunken", font=("Arial", 10))
        self.contact_entry.grid(row=2, column=1, padx=5, pady=5, columnspan=3, sticky="ew")
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg="#d4d0c8")
        button_frame.pack(pady=10)
        
        style = ttk.Style()
        style.configure("TButton", padding=6, relief="raised", background="#d4d0c8", font=("Arial", 9))
        
        buttons = [
            ("Add New Device", self.add_device),
            ("Mark Repaired", self.mark_repaired),
            ("Cancel Repair", self.cancel_repair),
            ("Delete Selected", self.delete_device)
        ]
        
        for text, command in buttons:
            btn = ttk.Button(button_frame, text=text, command=command)
            btn.pack(side=tk.LEFT, padx=5)
        
        # Treeview frame with counter
        tree_container = tk.Frame(main_frame, bg="#d4d0c8")
        tree_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Counter label
        self.counter_label = tk.Label(tree_container, text="", bg="#d4d0c8", font=("Arial", 9))
        self.counter_label.pack(anchor="w")
        
        # Treeview
        tree_frame = tk.Frame(tree_container, bg="#d4d0c8")
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("id", "device", "serial", "issue", "submitted", "contact", "status", "date_repaired")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        col_configs = [
            ("id", "ID", 40, "center"),
            ("device", "Device Name", 120, "w"),
            ("serial", "Serial Number", 100, "w"),
            ("issue", "Issue Description", 150, "w"),
            ("submitted", "Submitted By", 100, "w"),
            ("contact", "Contact Info", 120, "w"),
            ("status", "Status", 100, "center"),
            ("date_repaired", "Date Repaired", 100, "w")
        ]
        
        for col, heading, width, anchor in col_configs:
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=width, anchor=anchor)
        
        # Add sorting
        for col in columns:
            self.tree.heading(col, command=lambda c=col: self.sort_treeview(c))
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        self.load_treeview()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready • Ctrl+N: New • Ctrl+F: Search • Ctrl+D: Dashboard")
        tk.Label(self.root, textvariable=self.status_var, bd=1, 
                relief="sunken", anchor="w", bg="#d4d0c8").pack(side=tk.BOTTOM, fill=tk.X)

    def filter_devices(self, event=None):
        search_term = self.search_entry.get().lower()
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        filtered_count = 0
        for device in self.devices:
            if (search_term in device['device'].lower() or 
                search_term in device['serial'].lower() or 
                search_term in device['issue'].lower() or
                search_term in device['submitted'].lower()):
                
                values = (
                    device['id'],
                    device['device'],
                    device['serial'],
                    device['issue'],
                    device['submitted'],
                    device['contact'],
                    device['status'],
                    device['date_repaired']
                )
                self.tree.insert("", "end", values=values)
                filtered_count += 1
        
        self.counter_label.config(text=f"Showing {filtered_count} of {len(self.devices)} devices")

    def sort_treeview(self, col):
        items = [(self.tree.set(item, col), item) for item in self.tree.get_children('')]
        items.sort()
        
        for index, (val, item) in enumerate(items):
            self.tree.move(item, '', index)

    def export_to_csv(self):
        try:
            filename = f"QueueRepair_Export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Device', 'Serial', 'Issue', 'Submitted By', 'Contact', 'Status', 'Date Repaired', 'Date Submitted'])
                
                for device in self.devices:
                    writer.writerow([
                        device['id'],
                        device['device'],
                        device['serial'],
                        device['issue'],
                        device['submitted'],
                        device['contact'],
                        device['status'],
                        device['date_repaired'],
                        device.get('date_submitted', '')
                    ])
            
            self.status_var.set(f"Exported to {filename}")
            messagebox.showinfo("Export Successful", f"Data exported to:\n{os.path.abspath(filename)}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {str(e)}")

    def show_dashboard(self):
        # Simple dashboard without matplotlib
        dashboard = tk.Toplevel(self.root)
        dashboard.title("QueueRepair - Dashboard")
        dashboard.geometry("600x500")
        dashboard.configure(bg="#d4d0c8")
        
        # Statistics
        total = len(self.devices)
        pending = len([d for d in self.devices if d['status'] == 'Pending'])
        repaired = len([d for d in self.devices if d['status'] == 'Repaired'])
        canceled = len([d for d in self.devices if d['status'] == 'Canceled'])
        
        # Title
        tk.Label(dashboard, text="Dashboard", font=("Arial", 18, "bold"), 
                bg="#d4d0c8").pack(pady=10)
        
        # Stats frame
        stats_frame = tk.Frame(dashboard, bg="#d4d0c8", relief="raised", bd=2)
        stats_frame.pack(fill=tk.X, padx=20, pady=10)
        
        stats = [
            ("Total Tickets", total, "#333333"),
            ("Pending", pending, "#b8860b"),
            ("Repaired", repaired, "#006400"),
            ("Canceled", canceled, "#8b0000")
        ]
        
        for i, (label, value, color) in enumerate(stats):
            frame = tk.Frame(stats_frame, bg="#d4d0c8")
            frame.grid(row=0, column=i, padx=20, pady=10)
            tk.Label(frame, text=label, bg="#d4d0c8", font=("Arial", 10)).pack()
            tk.Label(frame, text=str(value), bg="#d4d0c8", font=("Arial", 20, "bold"), fg=color).pack()
        
        # Status distribution section
        dist_frame = tk.Frame(dashboard, bg="#d4d0c8", relief="raised", bd=2)
        dist_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(dist_frame, text="Status Distribution", font=("Arial", 14, "bold"), 
                bg="#d4d0c8").pack(pady=10)
        
        if total > 0:
            # Create simple progress bars
            bar_container = tk.Frame(dist_frame, bg="#d4d0c8")
            bar_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            statuses = [
                ("Pending", pending, "#b8860b"),
                ("Repaired", repaired, "#006400"),
                ("Canceled", canceled, "#8b0000")
            ]
            
            for status, count, color in statuses:
                if count > 0:
                    percentage = (count / total) * 100
                    frame = tk.Frame(bar_container, bg="#d4d0c8")
                    frame.pack(fill=tk.X, pady=5)
                    
                    tk.Label(frame, text=f"{status}:", bg="#d4d0c8", width=10, anchor="w").pack(side=tk.LEFT)
                    
                    # Progress bar
                    bar = tk.Frame(frame, bg=color, height=20, width=int(percentage * 3))
                    bar.pack(side=tk.LEFT, padx=5)
                    
                    tk.Label(frame, text=f"{count} ({percentage:.1f}%)", bg="#d4d0c8").pack(side=tk.LEFT)
        else:
            tk.Label(dist_frame, text="No data available", bg="#d4d0c8", 
                    font=("Arial", 12)).pack(pady=20)
        
        # Recent activity
        recent_frame = tk.Frame(dashboard, bg="#d4d0c8", relief="raised", bd=2)
        recent_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(recent_frame, text="Recent Activity", font=("Arial", 12, "bold"), 
                bg="#d4d0c8").pack(pady=5)
        
        recent_list = tk.Listbox(recent_frame, height=5)
        recent_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Show last 10 repairs
        for device in sorted(self.devices, key=lambda x: x.get('date_submitted', ''), reverse=True)[:10]:
            recent_list.insert(tk.END, f"[{device['status']}] {device['device']} - {device['issue'][:30]}...")
        
        # Close button
        ttk.Button(dashboard, text="Close", command=dashboard.destroy).pack(pady=10)

    def add_device(self):
        device = self.device_entry.get().strip()
        serial = self.serial_entry.get().strip()
        issue = self.issue_entry.get().strip()
        submitted = self.submitted_entry.get().strip()
        contact = self.contact_entry.get().strip()
        
        if not device or not issue:
            messagebox.showwarning("Input Error", "Device name and issue description are required!")
            return
            
        new_id = max([d['id'] for d in self.devices], default=0) + 1
        new_device = {
            "id": new_id,
            "device": device,
            "serial": serial,
            "issue": issue,
            "submitted": submitted if submitted else "Unknown",
            "contact": contact,
            "status": "Pending",
            "date_submitted": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "date_repaired": ""
        }
        
        self.devices.append(new_device)
        self.save_data()
        self.filter_devices()
        
        # Clear form
        self.device_entry.delete(0, tk.END)
        self.serial_entry.delete(0, tk.END)
        self.issue_entry.delete(0, tk.END)
        self.submitted_entry.delete(0, tk.END)
        self.contact_entry.delete(0, tk.END)
        
        self.status_var.set(f"Device '{device}' added for repair")

    def mark_repaired(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a device to mark as repaired")
            return
            
        item = self.tree.item(selected[0])
        device_id = item['values'][0]
        
        for device in self.devices:
            if device['id'] == device_id:
                if device['status'] == "Repaired":
                    messagebox.showinfo("Info", "This device is already marked as repaired")
                    return
                    
                device['status'] = "Repaired"
                device['date_repaired'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                self.save_data()
                self.filter_devices()
                self.status_var.set(f"Device '{device['device']}' marked as repaired")
                return

    def cancel_repair(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a device to cancel repair")
            return
            
        item = self.tree.item(selected[0])
        device_id = item['values'][0]
        
        for device in self.devices:
            if device['id'] == device_id:
                if device['status'] == "Canceled":
                    messagebox.showinfo("Info", "This repair is already canceled")
                    return
                    
                device['status'] = "Canceled"
                device['date_repaired'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                self.save_data()
                self.filter_devices()
                self.status_var.set(f"Repair for '{device['device']}' has been canceled")
                return

    def delete_device(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a device to delete")
            return
            
        item = self.tree.item(selected[0])
        device_id = item['values'][0]
        device_name = item['values'][1]
        
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{device_name}'?"):
            return
        
        for device in self.devices:
            if device['id'] == device_id:
                self.devices.remove(device)
                self.save_data()
                self.filter_devices()
                self.status_var.set(f"🗑️ Device '{device_name}' has been deleted")
                return

    def load_treeview(self):
        self.filter_devices()

if __name__ == "__main__":
    root = tk.Tk()
    app = QueueRepairApp(root)
    root.mainloop()

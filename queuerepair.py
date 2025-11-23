import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

class QueueRepairApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QueueRepair - IT Repair Tracker")
        self.root.geometry("900x600")
        self.root.configure(bg="#d4d0c8")
        
        # Data setup
        self.data_dir = Path("QueueRepairData")
        self.data_file = self.data_dir / "repair_data.json"
        self.data_dir.mkdir(exist_ok=True)
        
        self.devices = self.load_data()
        self.create_widgets()
        self.schedule_cleanup()

    def load_data(self):
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r') as f:
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
            with open(self.data_file, 'w') as f:
                json.dump(self.devices, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {str(e)}")

    def create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self.root, bd=1, relief="sunken", bg="#d4d0c8")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, text="QueueRepair - IT Repair Tracker", 
                              font=("Arial", 16, "bold"), bg="#d4d0c8")
        title_label.pack(pady=(10, 20))
        
        # Form frame
        form_frame = tk.Frame(main_frame, bg="#d4d0c8")
        form_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Form fields
        tk.Label(form_frame, text="Device Name:", bg="#d4d0c8").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.device_entry = tk.Entry(form_frame, width=30, relief="sunken")
        self.device_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(form_frame, text="Serial Number:", bg="#d4d0c8").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.serial_entry = tk.Entry(form_frame, width=20, relief="sunken")
        self.serial_entry.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(form_frame, text="Issue Description:", bg="#d4d0c8").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.issue_entry = tk.Entry(form_frame, width=30, relief="sunken")
        self.issue_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(form_frame, text="Submitted By:", bg="#d4d0c8").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.submitted_entry = tk.Entry(form_frame, width=20, relief="sunken")
        self.submitted_entry.grid(row=1, column=3, padx=5, pady=5)
        
        tk.Label(form_frame, text="Contact Info:", bg="#d4d0c8").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.contact_entry = tk.Entry(form_frame, width=30, relief="sunken")
        self.contact_entry.grid(row=2, column=1, padx=5, pady=5, columnspan=3, sticky="ew")
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg="#d4d0c8")
        button_frame.pack(pady=10)
        
        style = ttk.Style()
        style.configure("TButton", padding=6, relief="raised", background="#d4d0c8")
        
        buttons = [
            ("Add New Device", self.add_device),
            ("Mark as Repaired", self.mark_repaired),
            ("Cancel Repair", self.cancel_repair),
            ("Delete Selected", self.delete_device)
        ]
        
        for text, command in buttons:
            btn = ttk.Button(button_frame, text=text, command=command)
            btn.pack(side=tk.LEFT, padx=5)
        
        # Treeview
        tree_frame = tk.Frame(main_frame, bg="#d4d0c8")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
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
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        self.load_treeview()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        tk.Label(self.root, textvariable=self.status_var, bd=1, 
                relief="sunken", anchor="w").pack(side=tk.BOTTOM, fill=tk.X)

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
            "submitted": submitted,
            "contact": contact,
            "status": "Pending",
            "date_submitted": datetime.now().strftime("%Y-%m-%d"),
            "date_repaired": ""
        }
        
        self.devices.append(new_device)
        self.save_data()
        self.load_treeview()
        
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
                device['date_repaired'] = datetime.now().strftime("%Y-%m-%d")
                self.save_data()
                self.load_treeview()
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
                device['date_repaired'] = datetime.now().strftime("%Y-%m-%d")
                self.save_data()
                self.load_treeview()
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
                self.load_treeview()
                self.status_var.set(f"Device '{device_name}' has been deleted")
                return

    def load_treeview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for device in self.devices:
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
            
            # Color coding
            if device['status'] == "Repaired":
                self.tree.item(self.tree.get_children()[-1], tags=('repaired',))
            elif device['status'] == "Canceled":
                self.tree.item(self.tree.get_children()[-1], tags=('canceled',))
                
        self.tree.tag_configure('repaired', background='#d0f0d0')
        self.tree.tag_configure('canceled', background='#f0d0d0')

    def schedule_cleanup(self):
        self.cleanup_old_repaired()
        self.root.after(86400000, self.schedule_cleanup)  # 24 hours

    def cleanup_old_repaired(self):
        today = datetime.now()
        removed = False
        
        devices_copy = self.devices.copy()
        for device in devices_copy:
            if device['status'] == "Repaired" and device['date_repaired']:
                repair_date = datetime.strptime(device['date_repaired'], "%Y-%m-%d")
                if (today - repair_date).days >= 10:
                    self.devices.remove(device)
                    removed = True
        
        if removed:
            self.save_data()
            self.load_treeview()
            self.status_var.set("Old repaired devices have been removed")

if __name__ == "__main__":
    root = tk.Tk()
    app = QueueRepairApp(root)
    root.mainloop()
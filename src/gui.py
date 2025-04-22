import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from ems_client import EMSClient

client = EMSClient("http://127.0.0.1:5000/api/")  # Update if your API runs elsewhere

class EMSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Event Management System")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(padx=10, pady=10, expand=True, fill='both')

        self.create_user_tab()
        self.create_event_tab()
        self.view_events_tab()

    def create_user_tab(self):
        user_tab = ttk.Frame(self.notebook)
        self.notebook.add(user_tab, text="User")

        ttk.Label(user_tab, text="Name").grid(row=0, column=0)
        self.user_name = ttk.Entry(user_tab)
        self.user_name.grid(row=0, column=1)

        ttk.Label(user_tab, text="Email").grid(row=1, column=0)
        self.user_email = ttk.Entry(user_tab)
        self.user_email.grid(row=1, column=1)

        ttk.Label(user_tab, text="Phone").grid(row=2, column=0)
        self.user_phone = ttk.Entry(user_tab)
        self.user_phone.grid(row=2, column=1)

        create_btn = ttk.Button(user_tab, text="Create User", command=self.create_user)
        create_btn.grid(row=3, columnspan=2, pady=10)

    def create_event_tab(self):
        event_tab = ttk.Frame(self.notebook)
        self.notebook.add(event_tab, text="Create Event")

        ttk.Label(event_tab, text="Event Name").grid(row=0, column=0)
        self.event_name = ttk.Entry(event_tab)
        self.event_name.grid(row=0, column=1)

        ttk.Label(event_tab, text="Location").grid(row=1, column=0)
        self.event_location = ttk.Entry(event_tab)
        self.event_location.grid(row=1, column=1)

        ttk.Label(event_tab, text="Description").grid(row=2, column=0)
        self.event_desc = ttk.Entry(event_tab)
        self.event_desc.grid(row=2, column=1)

        ttk.Label(event_tab, text="Category (comma-separated)").grid(row=3, column=0)
        self.event_category = ttk.Entry(event_tab)
        self.event_category.grid(row=3, column=1)

        ttk.Label(event_tab, text="Tags (comma-separated)").grid(row=4, column=0)
        self.event_tags = ttk.Entry(event_tab)
        self.event_tags.grid(row=4, column=1)

        ttk.Button(event_tab, text="Create Event", command=self.create_event).grid(row=5, columnspan=2, pady=10)

    def view_events_tab(self):
        view_tab = ttk.Frame(self.notebook)
        self.notebook.add(view_tab, text="My Events")

        ttk.Button(view_tab, text="Load My Events", command=self.load_events).pack(pady=10)

        self.events_output = tk.Text(view_tab, height=15, width=60)
        self.events_output.pack()

    def create_user(self):
        name = self.user_name.get()
        email = self.user_email.get()
        phone = self.user_phone.get()

        if not name or not email:
            messagebox.showerror("Missing Fields", "Name and Email are required.")
            return

        if client.create_user(name, email, phone):
            messagebox.showinfo("Success", f"User {name} created.")
        else:
            messagebox.showerror("Error", "Failed to create user.")

    def create_event(self):
        name = self.event_name.get()
        location = self.event_location.get()
        desc = self.event_desc.get()
        category = self.event_category.get().split(",") if self.event_category.get() else []
        tags = self.event_tags.get().split(",") if self.event_tags.get() else []

        if not name or not location:
            messagebox.showerror("Missing Fields", "Event name and location are required.")
            return

        time = datetime.now() + timedelta(hours=1)

        if client.create_event(name, location, time, desc, category, tags):
            messagebox.showinfo("Success", f"Event {name} created.")
        else:
            messagebox.showerror("Error", "Failed to create event.")

    def load_events(self):
        result = client.get_user_events()
        if not result:
            self.events_output.delete(1.0, tk.END)
            self.events_output.insert(tk.END, "No user or events found.")
            return

        self.events_output.delete(1.0, tk.END)
        self.events_output.insert(tk.END, f"User: {result['user_name']}\n\n")
        self.events_output.insert(tk.END, "Organized Events:\n")
        for e in result["event_infos"]["organized_events"]:
            self.events_output.insert(tk.END, f"- {e['name']} at {e['location']}\n")

        self.events_output.insert(tk.END, "\nAttended Events:\n")
        for e in result["event_infos"]["attended_events"]:
            self.events_output.insert(tk.END, f"- {e['name']} at {e['location']}\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = EMSApp(root)
    root.mainloop()

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from src.ems_client import EMSClient

client = EMSClient("http://127.0.0.1:5000/api/")

def parse_datetime_from_string(time_string):
    try:
        return datetime.strptime(time_string, "%Y-%m-%d %H:%M")
    except ValueError:
        return None

class LoginFrame(ttk.Frame):
    def __init__(self, master, switch_to_register, switch_to_dashboard):
        super().__init__(master)
        self.switch_to_dashboard = switch_to_dashboard

        ttk.Label(self, text="Login", font=("Arial", 16)).grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Label(self, text="Username:").grid(row=1, column=0)
        self.username_entry = ttk.Entry(self)
        self.username_entry.grid(row=1, column=1)

        ttk.Button(self, text="Login", command=self.login_user).grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(self, text="Register", command=switch_to_register).grid(row=3, column=0, columnspan=2)

    def login_user(self):
        username = self.username_entry.get()
        if client.user_login(username):
            messagebox.showinfo("Login", f"Welcome, {username}!")
            self.switch_to_dashboard()
        else:
            messagebox.showerror("Login Failed", "Invalid username or not registered.")

class RegisterFrame(ttk.Frame):
    def __init__(self, master, switch_to_login, switch_to_dashboard):
        super().__init__(master)
        self.switch_to_login = switch_to_login
        self.switch_to_dashboard = switch_to_dashboard

        ttk.Label(self, text="Register", font=("Arial", 16)).grid(row=0, column=0, columnspan=2, pady=10)

        self.entries = {}
        for i, field in enumerate(["Name", "Email", "Phone"]):
            ttk.Label(self, text=f"{field}:").grid(row=i+1, column=0)
            entry = ttk.Entry(self)
            entry.grid(row=i+1, column=1)
            self.entries[field.lower()] = entry

        ttk.Button(self, text="Create Account", command=self.register_user).grid(row=4, column=0, columnspan=2, pady=10)
        ttk.Button(self, text="Back to Login", command=switch_to_login).grid(row=5, column=0, columnspan=2)

    def register_user(self):
        name = self.entries["name"].get()
        email = self.entries["email"].get()
        phone = self.entries["phone"].get()

        if client.create_user(name, email, phone):
            self.switch_to_dashboard()
        else:
            messagebox.showerror("Error", "Could not register.")

class DashboardFrame(ttk.Frame):
    def __init__(self, master, switch_to_login):
        super().__init__(master)
        self.switch_to_login = switch_to_login

        ttk.Label(self, text="Welcome to Your Dashboard", font=("Arial", 14)).pack(pady=10)

        ttk.Button(self, text="Create Event", command=self.create_event_popup).pack(pady=5)
        ttk.Button(self, text="View My Events", command=self.show_events).pack(pady=5)
        ttk.Button(self, text="Update Profile", command=self.update_profile_popup).pack(pady=5)
        ttk.Button(self, text="Search Event", command=self.search_event_popup).pack(pady=5)
        ttk.Button(self, text="Attend Event", command=self.attend_event_popup).pack(pady=5)
        ttk.Button(self, text="Leave Event", command=self.leave_event_popup).pack(pady=5)
        ttk.Button(self, text="Logout", command=self.logout).pack(pady=20)

        self.output = tk.Text(self, width=60, height=15)
        self.output.pack()

    def logout(self):
        client.user_logout(client.current_user)
        self.switch_to_login()

    def show_events(self):
        events = client.get_user_events()
        self.output.delete(1.0, tk.END)
        if events:
            self.output.insert(tk.END, f"User: {events['user_name']}\n\n")
            for e in events["event_infos"]["organized_events"]:
                self.output.insert(tk.END, f"Organized: {e['name']}\n")
            for e in events["event_infos"]["attended_events"]:
                self.output.insert(tk.END, f"Attended: {e['name']}\n")
        else:
            self.output.insert(tk.END, "No events found.")

    def create_event_popup(self):
        popup = tk.Toplevel(self)
        popup.title("Create Event")

        labels = ["Name", "Location", "Description", "Category", "Tags", "Time (YYYY-MM-DD HH:MM)"]
        entries = {}

        for i, lbl in enumerate(labels):
            ttk.Label(popup, text=lbl).grid(row=i, column=0)
            entry = ttk.Entry(popup)
            entry.grid(row=i, column=1)
            entries[lbl.lower()] = entry

        def submit():
            name = entries["name"].get()
            location = entries["location"].get()
            desc = entries["description"].get()
            category = entries["category"].get().split(',')
            tags = entries["tags"].get().split(',')
            time_str = entries["time (yyyy-mm-dd hh:mm)"].get()
            time = parse_datetime_from_string(time_str)
            if not time:
                messagebox.showerror("Invalid Time", "Please enter time in YYYY-MM-DD HH:MM format.")
                return

            if client.create_event(name, location, time, desc, category, tags):
                messagebox.showinfo("Created", "Event created!")
                popup.destroy()
            else:
                messagebox.showerror("Error", "Event creation failed.")

        ttk.Button(popup, text="Create", command=submit).grid(row=6, columnspan=2, pady=10)

    def search_event_popup(self):
        popup = tk.Toplevel(self)
        popup.title("Search Event")

        ttk.Label(popup, text="Event Name:").grid(row=0, column=0)
        event_entry = ttk.Entry(popup)
        event_entry.grid(row=0, column=1)

        def submit_search():
            event_name = event_entry.get()
            event = client.get_event(event_name)
            self.output.delete(1.0, tk.END)
            popup.destroy()
            if event:
                self.output.insert(tk.END, f"Event Found:\n")
                self.output.insert(tk.END, f"Name: {event['name']}\n")
                self.output.insert(tk.END, f"Location: {event['location']}\n")
                self.output.insert(tk.END, f"Time: {event['time']}\n")
                self.output.insert(tk.END, f"Description: {event.get('description', 'No description')}\n")
            else:
                self.output.insert(tk.END, "No event found with that name.")

        ttk.Button(popup, text="Search", command=submit_search).grid(row=1, columnspan=2, pady=10)

    def attend_event_popup(self):
        popup = tk.Toplevel(self)
        popup.title("Attend Event")

        ttk.Label(popup, text="Event Name:").grid(row=0, column=0)
        event_entry = ttk.Entry(popup)
        event_entry.grid(row=0, column=1)

        def submit_attend():
            event_name = event_entry.get()
            if client.add_user_as_participant(event_name):
                messagebox.showinfo("Success", f"You are now attending {event_name}!")
            else:
                messagebox.showerror("Error", f"Could not attend {event_name}.")
            popup.destroy()

        ttk.Button(popup, text="Attend", command=submit_attend).grid(row=1, columnspan=2, pady=10)

    def leave_event_popup(self):
        popup = tk.Toplevel(self)
        popup.title("Leave Event")

        ttk.Label(popup, text="Event Name:").grid(row=0, column=0)
        event_entry = ttk.Entry(popup)
        event_entry.grid(row=0, column=1)

        def submit_leave():
            event_name = event_entry.get()
            if client.remove_user_participation(event_name):
                messagebox.showinfo("Success", f"You have left {event_name}.")
            else:
                messagebox.showerror("Error", f"Could not leave {event_name}.")
            popup.destroy()

        ttk.Button(popup, text="Leave", command=submit_leave).grid(row=1, columnspan=2, pady=10)

    def update_profile_popup(self):
        popup = tk.Toplevel(self)
        popup.title("Update Profile")

        fields = ["Name", "Email", "Phone"]
        entries = {}

        for i, field in enumerate(fields):
            ttk.Label(popup, text=field).grid(row=i, column=0)
            entry = ttk.Entry(popup)
            entry.grid(row=i, column=1)
            entries[field.lower()] = entry

        def submit():
            updated = {
                "name": entries["name"].get(),
                "email": entries["email"].get(),
                "phone_number": entries["phone"].get()
            }
            if client.modify_user(updated):
                messagebox.showinfo("Updated", "Profile updated!")
                popup.destroy()
            else:
                messagebox.showerror("Error", "Update failed.")

        ttk.Button(popup, text="Update", command=submit).grid(row=3, columnspan=2, pady=10)

class EMSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EMS")
        self.container = ttk.Frame(root)
        self.container.pack(fill="both", expand=True)
        self.current_frame = None
        self.show_login()

    def clear_frame(self):
        if self.current_frame:
            self.current_frame.destroy()

    def show_login(self):
        self.clear_frame()
        self.current_frame = LoginFrame(self.container, self.show_register, self.show_dashboard)
        self.current_frame.pack()

    def show_register(self):
        self.clear_frame()
        self.current_frame = RegisterFrame(self.container, self.show_login, self.show_dashboard)
        self.current_frame.pack()

    def show_dashboard(self):
        self.clear_frame()
        self.current_frame = DashboardFrame(self.container, self.show_login)
        self.current_frame.pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = EMSApp(root)
    root.mainloop()

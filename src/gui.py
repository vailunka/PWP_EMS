"""GUI FOR API on course PWP"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from src.ems_client import EMSClient

client = EMSClient("http://127.0.0.1:5000/api/")


def parse_datetime_from_string(time_string):
    """
    Parses a datetime string in the format 'YYYY-MM-DD HH:MM'.

    Args:
        time_string (str): The datetime string to parse.

    Returns:
        datetime or None: Parsed datetime object, or None if the format is invalid.
    """
    try:
        return datetime.strptime(time_string, "%Y-%m-%d %H:%M")
    except ValueError:
        return None


class LoginFrame(ttk.Frame):
    """
    A frame that allows users to log in.

    Args:
        master (tk.Widget): The parent widget.
        switch_to_register (function): Callback to switch to the registration frame.
        switch_to_dashboard (function):
        Callback to switch to the dashboard frame upon successful login.
    """

    def __init__(self, master, switch_to_register, switch_to_dashboard):
        super().__init__(master)
        self.switch_to_dashboard = switch_to_dashboard

        ttk.Label(self, text="Login", font=("Arial", 16)).grid(
            row=0, column=0, columnspan=2, pady=10
        )

        ttk.Label(self, text="Username:").grid(row=1, column=0)
        self.username_entry = ttk.Entry(self)
        self.username_entry.grid(row=1, column=1)

        ttk.Button(self, text="Login", command=self.login_user).grid(
            row=2, column=0, columnspan=2, pady=10
        )

        ttk.Button(self, text="Register", command=switch_to_register).grid(
            row=3, column=0, columnspan=2
        )

    def login_user(self):
        """
        Logs the user in with the entered username.
        Displays a message box indicating success or failure.
        """
        username = self.username_entry.get()
        if client.user_login(username):
            messagebox.showinfo("Login", f"Welcome, {username}!")
            self.switch_to_dashboard()
        else:
            messagebox.showerror("Login Failed", "Invalid username or not registered.")


class RegisterFrame(ttk.Frame):
    """
    A frame that allows users to register.

    Args:
        master (tk.Widget): The parent widget.
        switch_to_login (function): Callback to switch back to the login frame.
        switch_to_dashboard (function):
        Callback to switch to the dashboard frame upon successful registration.
    """

    def __init__(self, master, switch_to_login, switch_to_dashboard):
        super().__init__(master)
        self.switch_to_login = switch_to_login
        self.switch_to_dashboard = switch_to_dashboard

        ttk.Label(self, text="Register", font=("Arial", 16)).grid(
            row=0, column=0, columnspan=2, pady=10
        )

        self.entries = {}
        for i, field in enumerate(["Name", "Email", "Phone"]):
            ttk.Label(self, text=f"{field}:").grid(row=i + 1, column=0)
            entry = ttk.Entry(self)
            entry.grid(row=i + 1, column=1)
            self.entries[field.lower()] = entry

        ttk.Button(self, text="Create Account", command=self.register_user).grid(
            row=4, column=0, columnspan=2, pady=10
        )

        ttk.Button(self, text="Back to Login", command=switch_to_login).grid(
            row=5, column=0, columnspan=2
        )

    def register_user(self):
        """
        Registers a new user using the entered information.
        Displays a message box on failure and switches to dashboard on success.
        """
        name = self.entries["name"].get()
        email = self.entries["email"].get()
        phone = self.entries["phone"].get()

        if client.create_user(name, email, phone):
            self.switch_to_dashboard()
        else:
            messagebox.showerror("Error", "Could not register.")


class DashboardFrame(ttk.Frame):
    """
    A dashboard frame for logged-in users to manage their profile and events.

    Args:
        master (tk.Widget): The parent widget.
        switch_to_login (function): Callback to return to the login frame.
    """

    def __init__(self, master, switch_to_login):
        super().__init__(master)
        self.switch_to_login = switch_to_login

        ttk.Label(self, text="Welcome to Your Dashboard", font=("Arial", 14)).pack(
            pady=10
        )

        ttk.Button(self, text="Manage Events", command=self.manage_events_popup).pack(
            pady=5
        )

        ttk.Button(self, text="Manage Profile", command=self.manage_profile_popup).pack(
            pady=5
        )

        ttk.Button(self, text="View All Events", command=self.show_all_events).pack(
            pady=5
        )

        ttk.Button(self, text="Logout", command=self.logout).pack(pady=20)

        self.output = tk.Text(self, width=60, height=15)
        self.output.pack()

    def logout(self):
        """
        Logs out the current user and switches to the login frame.
        """
        client.user_logout(client.current_user)
        self.switch_to_login()

    def show_all_events(self):
        """
        Displays all available events in the text output area.
        """
        events = client.get_events()
        self.output.delete(1.0, tk.END)
        if events:
            for e in events:
                self.output.insert(
                    tk.END, f"{e['name']} at {e['location']} on {e['time']}\n"
                )
        else:
            self.output.insert(tk.END, "No events found.")

    def manage_profile_popup(self):
        """
        Opens a popup window for updating or deleting the user's profile.
        """
        popup = tk.Toplevel(self)
        popup.title("Manage Profile")

        profile = client.get_user()
        if not profile:
            messagebox.showerror("Error", "Could not load profile.")
            popup.destroy()
            return

        fields = ["Name", "Email", "Phone"]
        entries = {}

        for i, field in enumerate(fields):
            ttk.Label(popup, text=field).grid(row=i, column=0)
            entry = ttk.Entry(popup)
            entry.grid(row=i, column=1)
            value = (
                profile.get(field.lower())
                if field.lower() != "phone"
                else profile.get("phone_number", "")
            )
            entry.insert(0, value or "")
            entries[field.lower()] = entry

        def update_profile():
            """
            Submits updated profile data to the backend.
            """
            updated = {
                "name": entries["name"].get(),
                "email": entries["email"].get(),
                "phone_number": entries["phone"].get(),
            }
            if client.modify_user(updated):
                messagebox.showinfo("Updated", "Profile updated!")
                popup.destroy()
            else:
                messagebox.showerror("Error", "Profile update failed.")

        def delete_account():
            """
            Deletes the user's account after confirmation.
            """
            confirm = messagebox.askyesno(
                "Confirm",
                "Are you sure you want to delete your account? This cannot be undone.",
            )
            if confirm:
                if client.delete_user():
                    messagebox.showinfo("Deleted", "Your account was deleted.")
                    self.switch_to_login()
                    popup.destroy()
                else:
                    messagebox.showerror("Error", "Account deletion failed.")

        ttk.Button(popup, text="Update Profile", command=update_profile).grid(
            row=3, column=0, pady=10
        )

        ttk.Button(popup, text="Delete Account", command=delete_account).grid(
            row=3, column=1, pady=10
        )

    def manage_events_popup(self):
        """
        Opens a popup for managing events:
         create, delete, attend, leave, or search events.
        """
        popup = tk.Toplevel(self)
        popup.title("Manage Events")

        output = tk.Text(popup, width=70, height=15)
        output.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

        def refresh_events():
            """
            Refreshes the list of user's organized and attended events.
            """
            output.delete(1.0, tk.END)
            events = client.get_user_events()
            if events:
                output.insert(tk.END, f"User: {events['user_name']}\n\n")
                output.insert(tk.END, "Organized Events:\n")
                for e in events["event_infos"]["organized_events"]:
                    output.insert(tk.END, f"  - {e['name']}\n")
                output.insert(tk.END, "\nAttended Events:\n")
                for e in events["event_infos"]["attended_events"]:
                    output.insert(tk.END, f"  - {e['name']}\n")
            else:
                output.insert(tk.END, "No events found.")

        refresh_events()

        def make_popup(title, action_func):
            """
            Creates a generic popup for an event-related action.

            Args:
                title (str): The title and label for the popup.
                action_func (function): The client function to call.
            """
            sub = tk.Toplevel(popup)
            sub.title(title)
            ttk.Label(sub, text="Event Name:").grid(row=0, column=0)
            entry = ttk.Entry(sub)
            entry.grid(row=0, column=1)

            def submit():
                event_name = entry.get()
                if action_func(event_name):
                    messagebox.showinfo("Success", f"{title} successful!")
                    refresh_events()
                    sub.destroy()
                else:
                    messagebox.showerror("Error", f"{title} failed.")
                    sub.destroy()

            ttk.Button(sub, text=title, command=submit).grid(
                row=1, columnspan=2, pady=10
            )

        def create_event():
            """
            Opens a popup to create a new event with full details.
            """
            sub = tk.Toplevel(popup)
            sub.title("Create Event")

            labels = [
                "Name",
                "Location",
                "Description",
                "Category",
                "Tags",
                "Time (YYYY-MM-DD HH:MM)",
            ]
            entries = {}

            for i, lbl in enumerate(labels):
                ttk.Label(sub, text=lbl).grid(row=i, column=0)
                entry = ttk.Entry(sub)
                entry.grid(row=i, column=1)
                entries[lbl.lower()] = entry

            def submit():
                name = entries["name"].get()
                location = entries["location"].get()
                desc = entries["description"].get()
                category = entries["category"].get().split(",")
                tags = entries["tags"].get().split(",")
                time_str = entries["time (yyyy-mm-dd hh:mm)"].get()
                time = parse_datetime_from_string(time_str)
                if not time:
                    messagebox.showerror(
                        "Invalid Time", "Please enter time in YYYY-MM-DD HH:MM format."
                    )
                    return

                if client.create_event(name, location, time, desc, category, tags):
                    messagebox.showinfo("Created", "Event created!")
                    sub.destroy()
                    refresh_events()
                else:
                    messagebox.showerror("Error", "Event creation failed.")

            ttk.Button(sub, text="Create", command=submit).grid(
                row=6, columnspan=2, pady=10
            )

        def search_event():
            """
            Opens a popup to search and display an event by name.
            """
            sub = tk.Toplevel(popup)
            sub.title("Search Event")
            ttk.Label(sub, text="Event Name:").grid(row=0, column=0)
            entry = ttk.Entry(sub)
            entry.grid(row=0, column=1)

            def submit():
                event_name = entry.get()
                event = client.get_event(event_name)
                sub.destroy()
                output.delete(1.0, tk.END)
                if event:
                    output.insert(tk.END, f"Event Found:\n")
                    output.insert(tk.END, f"Name: {event['name']}\n")
                    output.insert(tk.END, f"Location: {event['location']}\n")
                    output.insert(tk.END, f"Time: {event['time']}\n")
                    output.insert(
                        tk.END,
                        f"Description: {event.get('description', 'No description')}\n",
                    )
                else:
                    output.insert(tk.END, "No event found with that name.")

            ttk.Button(sub, text="Search", command=submit).grid(
                row=1, columnspan=2, pady=10
            )

        ttk.Button(popup, text="Create", command=create_event).grid(
            row=1, column=0, padx=5, pady=5
        )
        ttk.Button(
            popup,
            text="Delete",
            command=lambda: make_popup("Delete Event", client.delete_event),
        ).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(popup, text="Search", command=search_event).grid(
            row=1, column=2, padx=5, pady=5
        )
        ttk.Button(
            popup,
            text="Attend",
            command=lambda: make_popup("Attend Event", client.add_user_as_participant),
        ).grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(
            popup,
            text="Leave",
            command=lambda: make_popup("Leave Event", client.remove_user_participation),
        ).grid(row=2, column=1, padx=5, pady=5)


class EMSApp:
    """
    Main application class that manages transitions between frames.

    Args:
        root (tk.Tk): The root Tkinter window.
    """

    def __init__(self, root):
        self.root = root
        self.root.title("EMS")
        self.container = ttk.Frame(root)
        self.container.pack(fill="both", expand=True)
        self.current_frame = None
        self.show_login()

    def clear_frame(self):
        """
        Destroys the current visible frame.
        """
        if self.current_frame:
            self.current_frame.destroy()

    def show_login(self):
        """
        Displays the login screen.
        """
        self.clear_frame()
        self.current_frame = LoginFrame(
            self.container, self.show_register, self.show_dashboard
        )
        self.current_frame.pack()

    def show_register(self):
        """
        Displays the registration screen.
        """
        self.clear_frame()
        self.current_frame = RegisterFrame(
            self.container, self.show_login, self.show_dashboard
        )
        self.current_frame.pack()

    def show_dashboard(self):
        """
        Displays the user dashboard.
        """
        self.clear_frame()
        self.current_frame = DashboardFrame(self.container, self.show_login)
        self.current_frame.pack()


if __name__ == "__main__":
    root = tk.Tk()
    app = EMSApp(root)
    root.mainloop()

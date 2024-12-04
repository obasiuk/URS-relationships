import pandas as pd
from tkinter import Tk, Label, Entry, Button, StringVar, Text, Scrollbar, VERTICAL, END, filedialog, OptionMenu, Frame, DISABLED, NORMAL
import matplotlib.pyplot as plt


def load_data(file_path):
    data = pd.read_csv(file_path)
    data['LastLogin'] = pd.to_datetime(data['LastLogin'])
    return data


def find_inactive_users(data, days=90):
    threshold_date = pd.Timestamp.now() - pd.Timedelta(days=days)
    return data[data['LastLogin'] < threshold_date]


def generate_report(data, output_path, inactive_users):
    with open(output_path, 'w') as file:
        file.write('Analytical Report\n')
        file.write(f'Total users: {len(data)}\n')
        file.write(f'Inactive users (not active for more than 90 days): {len(inactive_users)}\n')
        if not inactive_users.empty:
            file.write("\nList of inactive users:\n")
            file.write(inactive_users[['UserID', 'First Name', 'Last Name', 'System', 'Role', 'LastLogin']].to_string(index=False))
        else:
            file.write("\nNo inactive users found.")


def plot_inactive_users_by_system(inactive_users):
    system_counts = inactive_users['System'].value_counts()
    system_counts.plot(kind='barh', figsize=(8, 6), title='Inactive Users by System')
    plt.xlabel('Number of Inactive Users')
    plt.ylabel('System')
    plt.tight_layout()
    plt.show()


def find_user_data(data, user_id):
    return data[data['UserID'] == user_id]


def log_message(message):
    log_text.insert(END, message + "\n")
    log_text.see(END)


def clear_logs():
    log_text.delete(1.0, END)


def upload_file():
    global data, systems
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if file_path:
        try:
            data = load_data(file_path)
            systems = sorted(data['System'].unique())
            system_var.set("Select System")
            menu = system_menu["menu"]
            menu.delete(0, "end")
            for system in systems:
                menu.add_command(label=system, command=lambda value=system: system_var.set(value))
            log_message(f"File uploaded successfully: {file_path}")
            enable_fields_and_buttons()
        except Exception as e:
            log_message(f"Error loading file: {e}")


def enable_fields_and_buttons():
    btn_generate_report.config(state=NORMAL)
    btn_plot.config(state=NORMAL)
    btn_search_user.config(state=NORMAL)
    btn_show_users.config(state=NORMAL)
    btn_clear_logs.config(state=NORMAL)
    entry_user_id.config(state=NORMAL)
    system_menu.config(state=NORMAL)


def disable_fields_and_buttons():
    btn_generate_report.config(state=DISABLED)
    btn_plot.config(state=DISABLED)
    btn_search_user.config(state=DISABLED)
    btn_show_users.config(state=DISABLED)
    btn_clear_logs.config(state=DISABLED)
    entry_user_id.config(state=DISABLED)
    system_menu.config(state=DISABLED)


def on_generate_report_click():
    if data is None:
        log_message("No data uploaded. Please upload a file first.")
        return
    inactive_users = find_inactive_users(data)
    generate_report(data, 'report.txt', inactive_users)
    log_message("Report successfully generated: report.txt")


def on_plot_click():
    if data is None:
        log_message("No data uploaded. Please upload a file first.")
        return
    inactive_users = find_inactive_users(data)
    log_message("Generating plot...")
    plot_inactive_users_by_system(inactive_users)


def on_search_user_click():
    if data is None:
        log_message("No data uploaded. Please upload a file first.")
        return
    user_id = user_input.get()
    if not user_id:
        log_message("Please enter a UserID.")
    else:
        user_data = find_user_data(data, user_id)
        if user_data.empty:
            log_message(f"No user found with UserID '{user_id}'.")
        else:
            log_message(f"User data for UserID '{user_id}':")
            for index, row in user_data.iterrows():
                log_message(f"  - System: {row['System']}, Role: {row['Role']}")


def on_choose_system():
    global log_text
    if data is None:
        log_message("No data uploaded. Please upload a file first.")
        return
    selected_system = system_var.get()
    if selected_system == "Select System":
        log_message("Please select a system.")
        return
    users = data[data['System'] == selected_system]
    if users.empty:
        log_message(f"No users found for system '{selected_system}'.")
    else:
        log_message(f"Users with access to system '{selected_system}':")
        log_message(f"{'UserID':<15} {'Role':<20}")
        log_message(f"{'-'*35}")
        for index, row in users.iterrows():
            log_message(f"{row['UserID']:<15} {row['Role']:<20}")

    log_text.yview_moveto(0.0)

if __name__ == "__main__":
    data = None
    systems = []

    root = Tk()
    root.title("User Access Manager")
    root.geometry("600x700")

    Button(root, text="Upload User Data", command=upload_file).pack(pady=5)

    Label(root, text="Enter UserID for lookup:").pack(pady=5)
    user_input = StringVar()
    entry_user_id = Entry(root, textvariable=user_input, width=50, state=DISABLED)
    entry_user_id.pack(pady=5)

    btn_search_user = Button(root, text="Search User by UserID", command=on_search_user_click, state=DISABLED)
    btn_search_user.pack(pady=5)

    Label(root, text="Choose System:").pack(pady=5)
    system_var = StringVar()
    system_var.set("Select System")
    system_menu = OptionMenu(root, system_var, "Select System")
    system_menu.config(state=DISABLED)
    system_menu.pack(pady=5)

    btn_show_users = Button(root, text="Show Users for System", command=on_choose_system, state=DISABLED)
    btn_show_users.pack(pady=5)

    btn_generate_report = Button(root, text="Generate Report Inactive Users", command=on_generate_report_click, state=DISABLED)
    btn_generate_report.pack(pady=5)

    btn_plot = Button(root, text="Plot Inactive Users", command=on_plot_click, state=DISABLED)
    btn_plot.pack(pady=5)

    log_frame = Frame(root)
    log_frame.pack(pady=10, fill='both', expand=True)

    left_spacer = Frame(log_frame, width=15)
    left_spacer.pack(side='left', fill='y')

    log_text = Text(log_frame, height=15, width=70, wrap='word')
    log_scrollbar = Scrollbar(log_frame, orient=VERTICAL, command=log_text.yview)
    log_text.config(yscrollcommand=log_scrollbar.set)

    log_text.pack(side='left', fill='both', expand=True)
    log_scrollbar.pack(side='right', fill='y')

    btn_clear_logs = Button(root, text="Clear Logs", command=clear_logs, state=DISABLED)
    btn_clear_logs.pack(pady=(5, 20))

    disable_fields_and_buttons()

    root.mainloop()
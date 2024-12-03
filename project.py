import pandas as pd
from tkinter import Tk, Label, Entry, Button, StringVar, Text, Scrollbar, VERTICAL, END
import matplotlib.pyplot as plt


# LOAD DATA
def load_data(file_path):
    data = pd.read_csv(file_path)
    data['LastLogin'] = pd.to_datetime(data['LastLogin'])  # Convert 'LastLogin' column to datetime
    return data


# FIND INACTIVE USERS
def find_inactive_users(data, days=90):
    threshold_date = pd.Timestamp.now() - pd.Timedelta(days=days)
    inactive_users = data[data['LastLogin'] < threshold_date]
    return inactive_users


# REPORT 1
def generate_report(data, output_path, inactive_users):
    with open(output_path, 'w') as file:
        file.write('Analytical Report\n')
        file.write(f'Total users: {len(data)}\n')
        file.write(f'Inactive users (not active for more than 90 days): {len(inactive_users)}\n')
        if not inactive_users.empty:
            file.write("\nList of inactive users:\n")
            file.write(inactive_users[['UserID', 'First Name', 'Last Name', 'System', 'LastLogin']].to_string(index=False))
        else:
            file.write("\nNo inactive users found.")


# PLOT DATA
def plot_inactive_users_by_system(inactive_users):
    system_counts = inactive_users['System'].value_counts()
    system_counts.plot(kind='barh', figsize=(8, 6), title='Inactive Users by System')
    plt.xlabel('Number of Inactive Users')
    plt.ylabel('System')
    plt.tight_layout()
    plt.show()


# FIND USER BY UserID
def find_user_data(data, user_id):
    user_data = data[data['UserID'] == user_id]
    return user_data


# LOG MESSAGES
def log_message(message):
    log_text.insert(END, message + "\n")
    log_text.see(END)

# CLEAR WINDOW
def clear_logs():
    log_text.delete(1.0, END)  # Delete all text from the log area

# BUTTON HUNDLERS
def on_generate_report_click():
    inactive_users = find_inactive_users(data)
    generate_report(data, 'report.txt', inactive_users)
    log_message("Report successfully generated: report.txt")


def on_plot_click():
    inactive_users = find_inactive_users(data)
    log_message("Generating plot...")
    plot_inactive_users_by_system(inactive_users)


def on_search_user_click():
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
                log_message(f"  - System: {row['System']}, Role: {row['Role']}, Last Login: {row['LastLogin'].date()}")


# MY CODE
if __name__ == "__main__":
    file_path = 'users_access.csv'  # Specify the path to your file
    data = load_data(file_path)

    # Configure the Tkinter window
    root = Tk()
    root.title("User Access Manager")
    root.geometry("500x550")

    # UserID input field
    Label(root, text="Enter UserID for lookup:").pack(pady=5)
    user_input = StringVar()
    Entry(root, textvariable=user_input, width=50).pack(pady=5)

    # Buttons
    Button(root, text="Generate Report", command=on_generate_report_click).pack(pady=5)
    Button(root, text="Plot Inactive Users", command=on_plot_click).pack(pady=5)
    Button(root, text="Search User by UserID", command=on_search_user_click).pack(pady=5)


    # Log text area with scrollbar
    log_text = Text(root, height=15, width=70, wrap='word')
    log_scrollbar = Scrollbar(root, orient=VERTICAL, command=log_text.yview)
    log_text.config(yscrollcommand=log_scrollbar.set)
    log_text.pack(pady=10)
    log_scrollbar.pack(side='right', fill='y')

    Button(root, text="Clear Logs", command=clear_logs).pack(pady=5)

    # Run the Tkinter application
    root.mainloop()

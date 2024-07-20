import tkinter as tk
from tkinter import messagebox
import configparser
import subprocess

# Function to save the configuration
def save_config():
    config = configparser.ConfigParser()

    # Save IQOption accounts
    for account in iqoption_accounts:
        section = f'IQOption_{account["id"]}'
        config[section] = {
            'email': account['email'].get(),
            'password': account['password'].get(),
            'accountType': account['account_type'].get()
        }

    # Save Trading section
    config['Trading'] = {
        'amount': trading_amount.get(),
        'martingale': trading_martingale.get(),
        'short_period': trading_short_period.get(),
        'long_period': trading_long_period.get(),
        'duration': trading_duration.get(),
        'demo_initial_balance': trading_demo_balance.get(),
        'default_strategy': trading_strategy.get()
    }

    # Save Email section
    config['Email'] = {
        'smtp_server': email_smtp_server.get(),
        'smtp_port': email_smtp_port.get(),
        'smtp_user': email_smtp_user.get(),
        'smtp_password': email_smtp_password.get(),
        'notification_email': email_notification.get()
    }

    # Save Paths section
    config['Paths'] = {
        'excel_directory': paths_excel_directory.get(),
        'log_directory': paths_log_directory.get()
    }

    # Save Top Assets section
    config['top_assets'] = {
        'asset1': top_asset1.get(),
        'asset2': top_asset2.get(),
        'asset3': top_asset3.get(),
        'asset4': top_asset4.get(),
        'asset5': top_asset5.get()
    }

    with open('config-test.ini', 'w') as configfile:
        config.write(configfile)

    messagebox.showinfo("Success", "Configuration saved successfully!")

# Function to restart the Docker container
def restart_container():
    save_config()
    try:
        subprocess.run(["docker-compose", "down"], check=True)
        subprocess.run(["docker-compose", "up", "-d"], check=True)
        messagebox.showinfo("Success", "Container restarted successfully!")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to restart container: {e}")

# Function to add a new IQOption account
def add_account():
    account_id = len(iqoption_accounts) + 1
    account_frame = tk.LabelFrame(iqoption_accounts_frame, text=f"IQOption Account {account_id}", padx=10, pady=10)
    account_frame.grid(row=account_id-1, column=0, padx=10, pady=5, sticky="ew")

    tk.Label(account_frame, text="Email").grid(row=0, column=0, sticky="w")
    email_entry = tk.Entry(account_frame, width=40)
    email_entry.grid(row=0, column=1, sticky="ew")

    tk.Label(account_frame, text="Password").grid(row=1, column=0, sticky="w")
    password_entry = tk.Entry(account_frame, width=40, show='*')
    password_entry.grid(row=1, column=1, sticky="ew")

    tk.Label(account_frame, text="Account Type").grid(row=2, column=0, sticky="w")
    account_type_entry = tk.Entry(account_frame, width=40)
    account_type_entry.grid(row=2, column=1, sticky="ew")

    iqoption_accounts.append({
        "id": account_id,
        "email": email_entry,
        "password": password_entry,
        "account_type": account_type_entry
    })

# Create the main window
root = tk.Tk()
root.title("Trading Bot Configuration")
root.geometry("800x600")  # Set initial size
root.minsize(800, 600)   # Set minimum size

# Configure grid layout
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# Frame for IQOption accounts
iqoption_accounts_frame = tk.LabelFrame(root, text="IQOption Accounts", padx=10, pady=10)
iqoption_accounts_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

# List to store IQOption accounts
iqoption_accounts = []

# Button to add new account
add_account_button = tk.Button(iqoption_accounts_frame, text="Add Account", command=add_account)
add_account_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

# Trading Frame
trading_frame = tk.LabelFrame(root, text="Trading", padx=20, pady=20)
trading_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

trading_labels_entries = {
    "Amount": "trading_amount",
    "Martingale": "trading_martingale",
    "Short Period": "trading_short_period",
    "Long Period": "trading_long_period",
    "Duration": "trading_duration",
    "Demo Initial Balance": "trading_demo_balance",
    "Default Strategy": "trading_strategy"
}

for idx, (label, var) in enumerate(trading_labels_entries.items()):
    tk.Label(trading_frame, text=label).grid(row=idx, column=0, sticky="w")
    globals()[var] = tk.Entry(trading_frame, width=40)
    globals()[var].grid(row=idx, column=1, sticky="ew")

# Email Frame
email_frame = tk.LabelFrame(root, text="Email", padx=20, pady=20)
email_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

email_labels_entries = {
    "SMTP Server": "email_smtp_server",
    "SMTP Port": "email_smtp_port",
    "SMTP User": "email_smtp_user",
    "SMTP Password": "email_smtp_password",
    "Notification Email": "email_notification"
}

for idx, (label, var) in enumerate(email_labels_entries.items()):
    tk.Label(email_frame, text=label).grid(row=idx, column=0, sticky="w")
    globals()[var] = tk.Entry(email_frame, width=40)
    if "Password" in label:
        globals()[var].config(show='*')
    globals()[var].grid(row=idx, column=1, sticky="ew")

# Paths Frame
paths_frame = tk.LabelFrame(root, text="Paths", padx=20, pady=20)
paths_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

paths_labels_entries = {
    "Excel Directory": "paths_excel_directory",
    "Log Directory": "paths_log_directory"
}

for idx, (label, var) in enumerate(paths_labels_entries.items()):
    tk.Label(paths_frame, text=label).grid(row=idx, column=0, sticky="w")
    globals()[var] = tk.Entry(paths_frame, width=40)
    globals()[var].grid(row=idx, column=1, sticky="ew")

# Top Assets Frame
assets_frame = tk.LabelFrame(root, text="Top Assets", padx=20, pady=20)
assets_frame.grid(row=4, column=0, padx=10, pady=5, sticky="ew")

assets_labels_entries = {
    "Asset 1": "top_asset1",
    "Asset 2": "top_asset2",
    "Asset 3": "top_asset3",
    "Asset 4": "top_asset4",
    "Asset 5": "top_asset5"
}

for idx, (label, var) in enumerate(assets_labels_entries.items()):
    tk.Label(assets_frame, text=label).grid(row=idx, column=0, sticky="w")
    globals()[var] = tk.Entry(assets_frame, width=40)
    globals()[var].grid(row=idx, column=1, sticky="ew")

# Save and Restart Buttons
buttons_frame = tk.Frame(root, padx=10, pady=10)
buttons_frame.grid(row=5, column=0, padx=10, pady=5, sticky="ew")

save_button = tk.Button(buttons_frame, text="Save Configuration", command=save_config)
save_button.grid(row=0, column=0, padx=5, pady=5)

restart_button = tk.Button(buttons_frame, text="Save and Restart", command=restart_container)
restart_button.grid(row=0, column=1, padx=5, pady=5)

# Run the GUI event loop
root.mainloop()

import subprocess
import requests
import time
import tkinter as tk
from tkinter import messagebox, ttk

# Global variable to control the tracking loop
tracking = False
crypto_entries = []

# Function to fetch the token price
def get_price(token, max_price, min_price, uppercase_token):
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        'ids': token,
        'vs_currencies': 'usd'
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            price = data.get(token, {}).get('usd')
            if price:
                return price
            else:
                messagebox.showerror("Error", f"Token '{token}' not found.")
                return None
        else:
            messagebox.showerror("Error", f"Failed to fetch data. Status code: {response.status_code}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
    return None

# Function to send macOS notification
def send_notification(title, message):
    subprocess.run([
        "osascript", "-e", f'display notification "{message}" with title "{title}"'
    ])

# Function to start or stop tracking the price
def toggle_tracking():
    global tracking
    if not tracking:
        tracking = True
        start_button.config(text="Stop Tracking")
        send_notification("Crypto Price Tracker", "Tracking Started")

        def track_prices():
            while tracking:
                num_cryptos = len(crypto_entries)
                interval_per_crypto = 25  # 25-second intervals for each crypto check
                for i, (token_entry, max_price_entry, min_price_entry, price_label) in enumerate(crypto_entries):
                    token = token_entry.get().lower()
                    uppercase_token = token.upper()
                    try:
                        max_price = float(max_price_entry.get())
                        min_price = float(min_price_entry.get())
                    except ValueError:
                        messagebox.showerror("Error", f"Please enter valid numbers for max and min price for Crypto {i+1}.")
                        stop_tracking()
                        return

                    price = get_price(token, max_price, min_price, uppercase_token)
                    if price is not None:
                        price_label.config(text=f"Current price of {uppercase_token}: ${price}")
                        if price >= max_price:
                            send_notification(f"Price Alert!", f"{uppercase_token} has reached ${price}")
                        elif price <= min_price:
                            send_notification(f"Price Alert!", f"{uppercase_token} fell to ${price}")

                    # Wait for 25 seconds before moving to the next crypto
                    time.sleep(interval_per_crypto)

                # After all cryptos are checked, wait until the 5-minute cycle is complete
                total_cycle_time = 300  # 5 minutes in seconds
                time_spent = num_cryptos * interval_per_crypto  # Total time spent checking all cryptos
                remaining_time = total_cycle_time - time_spent

                # If the time spent checking cryptos is less than 5 minutes, wait the remaining time
                if remaining_time > 0:
                    time.sleep(remaining_time)

        # Start tracking in a separate thread
        import threading
        tracking_thread = threading.Thread(target=track_prices, daemon=True)
        tracking_thread.start()
    else:
        stop_tracking()

def stop_tracking():
    global tracking
    tracking = False
    start_button.config(text="Start Tracking")
    send_notification("Crypto Price Tracker", "Tracking Stopped")

# Function to dynamically create input fields for multiple cryptos
def create_crypto_inputs(event):
    num_cryptos = int(num_cryptos_var.get())

    # Adjust the number of entries
    if len(crypto_entries) < num_cryptos:
        # Add new entries
        for i in range(len(crypto_entries), num_cryptos):
            tk.Label(crypto_frame, text=f"Crypto {i+1}:").grid(row=i * 3, column=0, padx=5, pady=5, sticky='w')
            token_entry = tk.Entry(crypto_frame)
            token_entry.grid(row=i * 3, column=1, padx=5, pady=5)

            tk.Label(crypto_frame, text="Max Price:").grid(row=i * 3 + 1, column=0, padx=5, pady=5, sticky='w')
            max_price_entry = tk.Entry(crypto_frame)
            max_price_entry.grid(row=i * 3 + 1, column=1, padx=5, pady=5)

            tk.Label(crypto_frame, text="Min Price:").grid(row=i * 3 + 2, column=0, padx=5, pady=5, sticky='w')
            min_price_entry = tk.Entry(crypto_frame)
            min_price_entry.grid(row=i * 3 + 2, column=1, padx=5, pady=5)

            price_label = tk.Label(crypto_frame, text="Price will appear here.")
            price_label.grid(row=i * 3, column=2, rowspan=1, padx=5, pady=5, sticky='w')

            crypto_entries.append((token_entry, max_price_entry, min_price_entry, price_label))

    elif len(crypto_entries) > num_cryptos:
        # Remove extra entries
        for i in range(len(crypto_entries) - 1, num_cryptos - 1, -1):
            for widget in crypto_frame.grid_slaves(row=i * 3):
                widget.grid_forget()
            for widget in crypto_frame.grid_slaves(row=i * 3 + 1):
                widget.grid_forget()
            for widget in crypto_frame.grid_slaves(row=i * 3 + 2):
                widget.grid_forget()
            crypto_entries.pop()

# Function to update the scroll region and show/hide scrollbar
def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))
    if canvas.bbox("all")[3] > canvas.winfo_height():
        scrollbar.pack(side="right", fill="y")
    else:
        scrollbar.pack_forget()

# Set up the main window
window = tk.Tk()
window.title("Crypto Price Tracker")

# Set a smaller initial window size
window.geometry('575x300')

# Create a frame for the scrollbar and the content
main_frame = tk.Frame(window)
main_frame.pack(fill="both", expand=True)

# Create a canvas widget to allow scrolling
canvas = tk.Canvas(main_frame, borderwidth=0, highlightthickness=0)
canvas.pack(side="left", fill="both", expand=True)

# Add a scrollbar to the canvas
scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)

# Create a frame inside the canvas where widgets will go
scrollable_frame = tk.Frame(canvas)

# Bind the canvas and frame together
scrollable_frame.bind(
    "<Configure>",
    on_frame_configure
)

# Create a window inside the canvas for the scrollable frame
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

# Configure the canvas scrolling
canvas.configure(yscrollcommand=scrollbar.set)

# Dropdown for selecting number of cryptos
tk.Label(scrollable_frame, text="Number of Cryptos:").grid(row=0, column=0, padx=10, pady=10)
num_cryptos_var = tk.StringVar(value="1")
num_cryptos_dropdown = ttk.Combobox(scrollable_frame, textvariable=num_cryptos_var, values=[str(i) for i in range(1, 13)], state="readonly")  # Make the dropdown readonly
num_cryptos_dropdown.grid(row=0, column=1, padx=10, pady=10)
num_cryptos_dropdown.bind("<<ComboboxSelected>>", create_crypto_inputs)

# Frame to hold crypto inputs
crypto_frame = tk.Frame(scrollable_frame)
crypto_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

# Start/Stop button - Centered
start_button = tk.Button(window, text="Start Tracking", command=toggle_tracking)
start_button.pack(pady=20)

# Start with one crypto input field by default
create_crypto_inputs(None)

# Start the GUI event loop
window.mainloop()

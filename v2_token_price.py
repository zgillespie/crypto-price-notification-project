import subprocess
import requests
import time

def get_price(token):
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
                print(f"The current price of {uppercase_token} is: ${price}")

                if price >= max_price:
                    print(f"{uppercase_token} has reached ${price}")
                    send_notification("Price Alert!", f"{uppercase_token} has reached ${price}")
                elif price <= min_price:
                    print(f"{uppercase_token} has fell to ${price}")
                    send_notification("Price Alert!", f"{uppercase_token} has fell to ${price}")
            else:
                print(f"Token '{token}' not found.")
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")

def send_notification(title, message):
    subprocess.run([
        "osascript", "-e", f'display notification "{message}" with title "{title}"'
    ])

token = input("Enter token name: ").lower()
str_max_price = input("Enter max price to send notifications: ")
max_price = float(str_max_price)
str_min_price = input("Enter minimum price to send notifications: ")
min_price = float(str_min_price)
uppercase_token = token.upper()

send_notification("Reminder", "Script Started")

while True:
    get_price(token)
    time.sleep(60)  # Sleep for 60 seconds (1 minute)

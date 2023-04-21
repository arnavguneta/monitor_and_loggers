# watcher service to monitor app health
# sends over logs of the process to discord

import subprocess
import requests
import time
import json
import os

pm2_app_name = 'coolkidbot'
discord_webhook_url = os.environ.get('DISCORD_WEBHOOK_URL')

# timer to sleep
sleep = 10

# Set the maximum length for the logs
max_length = 1980

def post_to_discord(text):
    payload = {
        'username': 'coolkidbot alert',
        'avatar_url': 'https://i.imgur.com/7GeWG1u.png',
        'content': text
    }
    headers = {
        'Content-Type': 'application/json'
    }
    requests.post(discord_webhook_url, json=payload, headers=headers)
    
while True:
    # Execute the pm2 jlist command to get the status of all PM2 apps
    pm2_output = subprocess.check_output(['pm2', 'jlist'])

    # Parse the JSON response
    pm2_data = json.loads(pm2_output)

    # Look for the app in the list of PM2 apps
    pm2_app = None
    for app in pm2_data:
        if app['name'] == pm2_app_name:
            pm2_app = app
            break

    # Check if the app is running
    if pm2_app and pm2_app['pm2_env']['status'] != 'online':        
        stdout_output = subprocess.check_output(['pm2', 'logs', pm2_app_name, '--nostream', '--lines=15', '--out'])
        stderr_output = subprocess.check_output(['pm2', 'logs', pm2_app_name, '--nostream', '--lines=15', '--err'])

        post_to_discord(f'> The **{pm2_app_name}** app has crashed!')
        post_to_discord(f'[STDOUT]\n```css\n{stdout_output.decode("utf-8")[-max_length:]}\n```')
        post_to_discord(f'[STDERR]\n```css\n{stderr_output.decode("utf-8")[-max_length:]}\n```')
        sleep = 900
    else:
      sleep = 10

    time.sleep(sleep)
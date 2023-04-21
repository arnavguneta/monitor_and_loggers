import requests
import os
import asyncio
import random
import time

err_file = '/home/arnie/.pm2/logs/coolkidbot-error.log'
out_file = '/home/arnie/.pm2/logs/coolkidbot-out.log'
site_out_file = '/home/arnie/.pm2/logs/coolkidsite-out.log'

# Replace with your own webhook URLs
err_webhook_url = os.environ.get('ERR_WEBHOOK_URL')
out_webhook_url = os.environ.get('OUT_WEBHOOK_URL')

# Set the maximum length for each message
max_message_length = 1800

def post_to_discord(text, url):
    payload = {
        'username': 'coolkidbot logs',
        'avatar_url': 'https://i.imgur.com/7GeWG1u.png',
        'content': text
    }
    headers = {
        'Content-Type': 'application/json'
    }
    time.sleep(random.uniform(0, 1.2))
    requests.post(url, json=payload, headers=headers)

async def watch_file(log_file, webhook_url):
  print("Watching file:", log_file)
  # Keep track of the last log message that was sent to Discord
  last_log_sent = ""

  # Try to load the last log message from a file
  try:
      with open(f"{log_file}.last_log_sent", "r") as f:
          last_log_sent = f.read()
  except FileNotFoundError:
      pass
    
  while True:
      # Read the entire contents of the log file
      with open(log_file, "r") as f:
          logs = f.read()
      
      # Get all new log messages since the last message sent to Discord
      new_logs = []
      should_append = not bool(last_log_sent)
      for line in logs.split("\n"):
          if should_append and line != "":
              new_logs.append(line)
          elif line == last_log_sent or last_log_sent == "":
              should_append = True
      
      # Batch new log messages and send them to Discord
      message_chunks = []
      current_chunk = ""
      for log_message in new_logs:
          # Append the current log message to the current chunk
          current_chunk += log_message + "\n"
          
          # If the current chunk is too long, add it to the message chunks
          if len(current_chunk) > max_message_length:
              message_chunks.append(current_chunk)
              current_chunk = ""
      
      # If there is any remaining chunk, add it to the message chunks
      if current_chunk:
          message_chunks.append(current_chunk)
      
      # Send each message chunk to Discord
      for message_chunk in message_chunks:
          post_to_discord(f'```http\n{message_chunk}\n```', webhook_url) 
      
      # Update the last log message sent to Discord
      if new_logs:
        last_log_sent = new_logs[-1]
        with open(f"{log_file}.last_log_sent", "w") as f:
          f.write(last_log_sent)
      
      # Run garbage collection manually to free up any unused memory
      gc.collect()
        
      # Wait for 30 seconds before checking the log file again
      await asyncio.sleep(30)

async def main():
    await asyncio.gather(
      watch_file(out_file, out_webhook_url),
      watch_file(err_file, err_webhook_url),
      watch_file(site_out_file, out_webhook_url)
    )
  
if __name__ == '__main__':
  asyncio.run(main())

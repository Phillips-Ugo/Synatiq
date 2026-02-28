from flask import Flask, request, jsonify
import requests
import re
import os

app = Flask(__name__)

# Your Stack AI Configuration
STACKAI_API_URL = "https://api.stackai.com/inference/v0/run/0633f81a-b58c-40f9-9079-77b01e0b3bce/69a2efaac16c39e32bc8d80d"
STACKAI_API_KEY = "7375ec8e-5bbc-4d7d-9df5-bffe30980015"

# Your Slack Bot Token (from environment variable for security)
SLACK_BOT_TOKEN = xoxb-10599945593062-10588284343687-4kDOCRh0F7UwlXGlv5jXtItx

@app.route('/slack/events', methods=['POST'])
def slack_events():
    data = request.json
    
    # Handle Slack's URL verification challenge
    if data.get('type') == 'url_verification':
        return jsonify({'challenge': data['challenge']})
    
    # Handle app_mention events
    if data.get('event', {}).get('type') == 'app_mention':
        event = data['event']
        
        # Extract data from Slack event
        raw_text = event['text']
        channel_id = event['channel']
        thread_ts = event.get('thread_ts', event['ts'])
        
        # Clean the text (remove bot mention)
        clean_text = re.sub(r'<@[A-Z0-9]+>\s*', '', raw_text).strip()
        
        print(f"Received question: {clean_text}")
        print(f"Channel: {channel_id}, Thread: {thread_ts}")
        
        # Call your Stack AI workflow
        try:
            response = requests.post(
                STACKAI_API_URL,
                headers={
                    'Authorization': f'Bearer {STACKAI_API_KEY}',
                    'Content-Type': 'application/json'
                },
                json={
                    'in-0': clean_text,
                    'user_id': channel_id
                },
                timeout=30
            )
            
            print(f"Stack AI response status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Workflow executed successfully!")
            else:
                print(f"⚠️ Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error calling Stack AI: {str(e)}")
        
    return jsonify({'status': 'ok'}), 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

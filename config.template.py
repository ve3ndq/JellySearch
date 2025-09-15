# Jellyfin API configuration template
# Rename this file to config.py and update with your API key and server details

API_KEY = 'YOUR_API_KEY_HERE'
SERVER = 'YOUR_SERVER_URL_HERE'  # e.g., 'http://your-jellyfin-server.com:8096'
SERVER_ID = 'YOUR_SERVER_ID_HERE'  # Your Jellyfin server ID
WEB_PLAYER_URL = f"{SERVER}/web/#/details?id="  # Base URL
FULL_PLAYER_URL = f"{WEB_PLAYER_URL}{{item_id}}&serverId={SERVER_ID}"  # Template with serverId
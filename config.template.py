# Jellyfin API configuration template
# Rename this file to config.py and update with your API key

API_KEY = 'YOUR_API_KEY_HERE'
SERVER = 'http://jf.brr.savethecdn.com:80'
SERVER_ID = '0445248a59a744c0a8b7cb98fd215aed'  # Your Jellyfin server ID
WEB_PLAYER_URL = f"{SERVER}/web/#/details?id="  # Base URL
FULL_PLAYER_URL = f"{WEB_PLAYER_URL}{{item_id}}&serverId={SERVER_ID}"  # Template with serverId
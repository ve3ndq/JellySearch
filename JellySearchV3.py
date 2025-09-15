
from flask import Flask, render_template_string, request, redirect, url_for, flash
import requests
import os
import sys
import re
import importlib

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For flash messages

# Function to read config values from config.py
def read_config():
    try:
        import config
        importlib.reload(config)  # Reload to get latest changes
        config_values = {
            'API_KEY': getattr(config, 'API_KEY', 'YOUR_API_KEY_HERE'),
            'SERVER': getattr(config, 'SERVER', 'YOUR_SERVER_URL_HERE'),
            'SERVER_ID': getattr(config, 'SERVER_ID', 'YOUR_SERVER_ID_HERE')
        }
        return config_values
    except ImportError:
        return {
            'API_KEY': 'YOUR_API_KEY_HERE',
            'SERVER': 'YOUR_SERVER_URL_HERE',
            'SERVER_ID': 'YOUR_SERVER_ID_HERE'
        }

# Function to update config.py file
def update_config(new_values):
    config_path = os.path.join(current_dir, 'config.py')
    
    # If config.py doesn't exist, create it from template
    if not os.path.exists(config_path):
        template_path = os.path.join(current_dir, 'config.template.py')
        if os.path.exists(template_path):
            with open(template_path, 'r') as template_file:
                template_content = template_file.read()
            
            with open(config_path, 'w') as config_file:
                config_file.write(template_content)
        else:
            # Create a basic config file if template doesn't exist
            with open(config_path, 'w') as config_file:
                config_file.write("# Jellyfin API configuration\n\n")
                config_file.write("API_KEY = 'YOUR_API_KEY_HERE'\n")
                config_file.write("SERVER = 'YOUR_SERVER_URL_HERE'\n")
                config_file.write("SERVER_ID = 'YOUR_SERVER_ID_HERE'\n")
                config_file.write("WEB_PLAYER_URL = f\"{SERVER}/web/#/details?id=\"\n")
                config_file.write("FULL_PLAYER_URL = f\"{WEB_PLAYER_URL}{{item_id}}&serverId={SERVER_ID}\"\n")
    
    # Read the current config file
    with open(config_path, 'r') as file:
        content = file.read()
    
    # Update values in the file content
    for key, value in new_values.items():
        if key in ['API_KEY', 'SERVER', 'SERVER_ID']:
            # Use regex to replace the value while preserving the format
            pattern = rf"{key}\s*=\s*['\"].*?['\"]"
            replacement = f"{key} = '{value}'"
            content = re.sub(pattern, replacement, content)
    
    # Write the updated content back to the file
    with open(config_path, 'w') as file:
        file.write(content)
    
    # Update derived values (WEB_PLAYER_URL and FULL_PLAYER_URL are derived from SERVER and SERVER_ID)
    if 'SERVER' in new_values or 'SERVER_ID' in new_values:
        server = new_values.get('SERVER', read_config()['SERVER'])
        server_id = new_values.get('SERVER_ID', read_config()['SERVER_ID'])
        
        # Update WEB_PLAYER_URL
        pattern = r"WEB_PLAYER_URL\s*=\s*f\"{SERVER}/web/#/details\?id=\""
        replacement = f"WEB_PLAYER_URL = f\"{SERVER}/web/#/details?id=\""
        content = re.sub(pattern, replacement, content)
        
        # Update FULL_PLAYER_URL
        pattern = r"FULL_PLAYER_URL\s*=\s*f\"{WEB_PLAYER_URL}\{+item_id\}+&serverId=.*?\""
        replacement = f"FULL_PLAYER_URL = f\"{{WEB_PLAYER_URL}}{{item_id}}&serverId={server_id}\""
        content = re.sub(pattern, replacement, content)
        
        # Write the updated content back to the file
        with open(config_path, 'w') as file:
            file.write(content)
    
    return True

# Get configuration
config_values = read_config()
API_KEY = config_values['API_KEY']
SERVER = config_values['SERVER']
SERVER_ID = config_values['SERVER_ID']

# Derived values
WEB_PLAYER_URL = f"{SERVER}/web/#/details?id="
FULL_PLAYER_URL = f"{WEB_PLAYER_URL}{{item_id}}&serverId={SERVER_ID}"

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<title>Jellyfin Fast Search</title>
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<link href="https://fonts.googleapis.com/css?family=Roboto:400,500&display=swap" rel="stylesheet">
	<style>
		body {
			background: #101010;
			color: rgba(255,255,255,0.87);
			font-family: 'Roboto', Arial, Helvetica, sans-serif;
			margin: 0;
			padding: 0;
		}
		.header {
			background: #202020;
			padding: 24px 0 12px 0;
			text-align: center;
			font-size: 2.2em;
			font-weight: 500;
			letter-spacing: 1px;
			color: #fff;
			box-shadow: 0 2px 8px rgba(0,0,0,0.2);
			margin-bottom: 24px;
		}
		form {
			display: flex;
			justify-content: center;
			margin-bottom: 32px;
			flex-wrap: wrap;
		}
		input[type="text"] {
			background: #292929;
			color: #fff;
			border: 1.5px solid #292929;
			border-radius: 6px;
			padding: 10px 16px;
			font-size: 1.1em;
			outline: none;
			transition: border 0.2s;
			margin-right: 12px;
			width: 320px;
			max-width: 90vw;
			box-sizing: border-box;
		}
		input[type="text"]:focus {
			border-color: #00a4dc;
		}
		button {
			background: #00a4dc;
			color: #fff;
			border: none;
			border-radius: 6px;
			padding: 10px 24px;
			font-size: 1.1em;
			font-weight: 500;
			cursor: pointer;
			transition: background 0.2s;
			box-shadow: 0 2px 8px rgba(0,164,220,0.08);
			margin-top: 8px;
		}
		button:hover, button:focus {
			background: #0cb0e8;
		}
		table {
			width: 90%;
			margin: 0 auto 32px auto;
			border-collapse: separate;
			border-spacing: 0;
			background: #202020;
			border-radius: 10px;
			overflow: hidden;
			box-shadow: 0 2px 12px rgba(0,0,0,0.18);
			font-size: 1em;
		}
		th, td {
			padding: 12px 16px;
			text-align: left;
			word-break: break-word;
		}
		th {
			background: #181818;
			color: #00a4dc;
			font-weight: 500;
			font-size: 1.05em;
			border-bottom: 2px solid #222;
		}
		tbody tr:nth-child(even) {
			background: #181818;
		}
		tbody tr:nth-child(odd) {
			background: #202020;
		}
		td a {
			color: #00a4dc;
			text-decoration: none;
			font-weight: 500;
			transition: color 0.2s;
			word-break: break-all;
		}
		td a:hover {
			color: #0cb0e8;
			text-decoration: underline;
		}
		pre {
			background: #181818;
			color: #fff;
			padding: 16px;
			border-radius: 8px;
			border: 1px solid #222;
			max-width: 90vw;
			overflow-x: auto;
			margin: 0 auto 32px auto;
			font-size: 0.98em;
		}
		h2 {
			color: #00a4dc;
			text-align: center;
			margin-top: 32px;
		}

		/* Loading Spinner */
		#loading-overlay {
			display: none;
			position: fixed;
			top: 0; left: 0; right: 0; bottom: 0;
			background: rgba(16,16,16,0.85);
			z-index: 9999;
			justify-content: center;
			align-items: center;
		}
		#loading-overlay.active {
			display: flex;
		}
		.spinner {
			border: 6px solid #222;
			border-top: 6px solid #00a4dc;
			border-radius: 50%;
			width: 60px;
			height: 60px;
			animation: spin 1s linear infinite;
		}
		@keyframes spin {
			0% { transform: rotate(0deg); }
			100% { transform: rotate(360deg); }
		}

		/* Responsive Design */
		@media (max-width: 900px) {
			table {
				width: 100%;
				font-size: 0.95em;
			}
			.header {
				font-size: 1.5em;
				padding: 18px 0 8px 0;
			}
			form {
				flex-direction: column;
				align-items: center;
			}
			input[type="text"] {
				width: 95vw;
				margin-right: 0;
				margin-bottom: 10px;
			}
			button {
				width: 95vw;
			}
		}

		@media (max-width: 600px) {
			.header {
				font-size: 1.1em;
				padding: 12px 0 6px 0;
			}
			th, td {
				padding: 8px 6px;
				font-size: 0.95em;
			}
			table {
				font-size: 0.9em;
			}
			form {
				margin-bottom: 18px;
			}
		}
	</style>
</head>
<body>
	<div id="loading-overlay"><div class="spinner"></div></div>
	<div class="header">Jellyfin Fast Search</div>
	<div style="text-align: center; margin-bottom: 20px;">
		<a href="/" style="color: #00a4dc; text-decoration: none; margin-right: 20px;">Search</a>
		<a href="/favorites" style="color: #00a4dc; text-decoration: none; margin-right: 20px;">Favorites</a>
		<a href="/settings" style="color: #00a4dc; text-decoration: none;">Settings</a>
	</div>
	{% if not is_favorites and not is_settings %}
	<form method="get" id="search-form">
		<input type="text" name="q" placeholder="Search..." value="{{ search_term|default('') }}" required>
		<button type="submit">Search</button>
	</form>
	{% endif %}
	{% if results %}
	<table>
		<thead>
			<tr>
				<th>URL</th><th>Type</th><th>Show Name</th><th>Season</th><th>Episode #</th><th>Episode Title</th>
			</tr>
		</thead>
		<tbody>
		{% for row in results %}
			<tr>
				<td><a href="{{ row['URL'] }}" target="_blank">Link</a></td>
				<td>{{ row['Type'] }}</td>
				<td>{{ row['Show Name'] }}</td>
				<td>{{ row['Season'] }}</td>
				<td>{{ row['Episode #'] }}</td>
				<td>{{ row['Episode Title'] }}</td>
			</tr>
		{% endfor %}
		</tbody>
	</table>
	{% endif %}
	
	{% if is_settings %}
	<div style="max-width: 600px; margin: 30px auto; background: #202020; padding: 25px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">
		<h2 style="text-align: center; margin-bottom: 25px; color: #00a4dc;">JellySearch Settings</h2>
		
		{% if success_message %}
		<div style="background: #1e441e; color: #a3d9a3; padding: 15px; border-radius: 5px; margin-bottom: 20px; text-align: center;">
			{{ success_message }}
		</div>
		{% endif %}
		
		{% if error_message %}
		<div style="background: #441e1e; color: #d9a3a3; padding: 15px; border-radius: 5px; margin-bottom: 20px; text-align: center;">
			{{ error_message }}
		</div>
		{% endif %}
		
		<form method="post" action="/settings">
			<div style="margin-bottom: 20px;">
				<label for="api_key" style="display: block; margin-bottom: 8px; font-weight: 500; color: #00a4dc;">API Key</label>
				<input type="text" id="api_key" name="api_key" value="{{ config_values.API_KEY }}" style="width: 100%; background: #292929; color: #fff; border: 1.5px solid #292929; border-radius: 6px; padding: 10px 16px; font-size: 1.1em; outline: none; transition: border 0.2s; box-sizing: border-box;" required>
				<small style="display: block; margin-top: 5px; color: #888;">Your Jellyfin API key for authentication</small>
			</div>
			
			<div style="margin-bottom: 20px;">
				<label for="server" style="display: block; margin-bottom: 8px; font-weight: 500; color: #00a4dc;">Server URL</label>
				<input type="text" id="server" name="server" value="{{ config_values.SERVER }}" style="width: 100%; background: #292929; color: #fff; border: 1.5px solid #292929; border-radius: 6px; padding: 10px 16px; font-size: 1.1em; outline: none; transition: border 0.2s; box-sizing: border-box;" required>
				<small style="display: block; margin-top: 5px; color: #888;">Your Jellyfin server URL (including port if needed)</small>
			</div>
			
			<div style="margin-bottom: 30px;">
				<label for="server_id" style="display: block; margin-bottom: 8px; font-weight: 500; color: #00a4dc;">Server ID</label>
				<input type="text" id="server_id" name="server_id" value="{{ config_values.SERVER_ID }}" style="width: 100%; background: #292929; color: #fff; border: 1.5px solid #292929; border-radius: 6px; padding: 10px 16px; font-size: 1.1em; outline: none; transition: border 0.2s; box-sizing: border-box;" required>
				<small style="display: block; margin-top: 5px; color: #888;">Your Jellyfin server ID for direct links</small>
			</div>
			
			<div style="display: flex; justify-content: space-between;">
				<a href="/" style="background: #333; color: #fff; border: none; border-radius: 6px; padding: 10px 24px; font-size: 1.1em; font-weight: 500; cursor: pointer; text-decoration: none; text-align: center;">Cancel</a>
				<button type="submit" style="background: #00a4dc; color: #fff; border: none; border-radius: 6px; padding: 10px 24px; font-size: 1.1em; font-weight: 500; cursor: pointer; transition: background 0.2s;">Save Changes</button>
			</div>
		</form>
		
		<div style="margin-top: 30px; border-top: 1px solid #333; padding-top: 20px;">
			<h3 style="color: #00a4dc; margin-bottom: 15px;">Test Connection</h3>
			<form method="post" action="/settings/test">
				<button type="submit" style="background: #444; color: #fff; border: none; border-radius: 6px; padding: 10px 24px; font-size: 1.1em; font-weight: 500; cursor: pointer; transition: background 0.2s; width: 100%;">Test Jellyfin Connection</button>
			</form>
			{% if test_result %}
			<div style="margin-top: 15px; padding: 15px; border-radius: 5px; text-align: center; {% if test_success %}background: #1e441e; color: #a3d9a3;{% else %}background: #441e1e; color: #d9a3a3;{% endif %}">
				{{ test_result }}
			</div>
			{% endif %}
		</div>
	</div>
	{% endif %}
<script>
document.getElementById('search-form') && document.getElementById('search-form').addEventListener('submit', function() {
	document.getElementById('loading-overlay').classList.add('active');
});
window.addEventListener('pageshow', function() {
	document.getElementById('loading-overlay').classList.remove('active');
});
</script>
'''

def search_jellyfin(search_term):
	headers = {'X-Emby-Token': API_KEY}
	params = {'SearchTerm': search_term}
	import json
	try:
		response = requests.get(f'{SERVER}/Search/Hints', headers=headers, params=params)
		response.raise_for_status()
		data = response.json()
	except Exception as e:
		return ([{'URL': '', 'Type': '', 'Show Name': f'Error: {e}', 'Season': '', 'Episode #': '', 'Episode Title': ''}], {})

	results = []
	for item in data.get('SearchHints', []):
		item_type = item.get('Type', 'N/A')
		# Series (Show)
		if item_type == 'Series':
			results.append({
				'URL': FULL_PLAYER_URL.format(item_id=item.get('Id', 'N/A')),
				'Type': 'Show',
				'Show Name': item.get('Name', 'N/A'),
				'Season': '',
				'Episode #': '',
				'Episode Title': ''
			})
		# Episode
		elif item_type == 'Episode':
			results.append({
				'URL': FULL_PLAYER_URL.format(item_id=item.get('Id', 'N/A')),
				'Type': 'Episode',
				'Show Name': item.get('SeriesName', 'N/A'),
				'Season': item.get('ParentIndexNumber', ''),
				'Episode #': item.get('IndexNumber', ''),
				'Episode Title': item.get('Name', '')
			})
		# Movie
		elif item_type == 'Movie':
			results.append({
				'URL': FULL_PLAYER_URL.format(item_id=item.get('Id', 'N/A')),
				'Type': 'Movie',
				'Show Name': item.get('Name', ''),
				'Season': '',
				'Episode #': '',
				'Episode Title': ''
			})
	return results, data


def fetch_favorites():
	headers = {'X-Emby-Token': API_KEY}
	params = {
		'Filters': 'IsFavorite',
		'IncludeItemTypes': 'Movie,Series',
		'Recursive': 'true'
	}
	try:
		response = requests.get(f'{SERVER}/Items', headers=headers, params=params)
		response.raise_for_status()
		data = response.json()
	except Exception as e:
		return ([{'URL': '', 'Type': '', 'Show Name': f'Error: {e}', 'Season': '', 'Episode #': '', 'Episode Title': ''}], {})

	results = []
	for item in data.get('Items', []):
		item_type = item.get('Type', 'N/A')
		if item_type == 'Series':
			results.append({
				'URL': FULL_PLAYER_URL.format(item_id=item.get('Id', 'N/A')),
				'Type': 'Show',
				'Show Name': item.get('Name', 'N/A'),
				'Season': '',
				'Episode #': '',
				'Episode Title': ''
			})
		elif item_type == 'Movie':
			results.append({
				'URL': FULL_PLAYER_URL.format(item_id=item.get('Id', 'N/A')),
				'Type': 'Movie',
				'Show Name': item.get('Name', 'N/A'),
				'Season': '',
				'Episode #': '',
				'Episode Title': ''
			})
	return results, data


@app.route('/', methods=['GET'])
def index():
	search_term = request.args.get('q', '')
	if search_term:
		results, _ = search_jellyfin(search_term)
	else:
		results = []
	return render_template_string(HTML_TEMPLATE, results=results, search_term=search_term, is_favorites=False, is_settings=False)


@app.route('/favorites', methods=['GET'])
def favorites():
	results, _ = fetch_favorites()
	return render_template_string(HTML_TEMPLATE, results=results, search_term='', is_favorites=True, is_settings=False)


@app.route('/settings', methods=['GET', 'POST'])
def settings():
	# Get current config values
	config_values = read_config()
	
	# Initialize variables for template
	success_message = None
	error_message = None
	test_result = None
	test_success = None
	
	# Handle form submission
	if request.method == 'POST':
		try:
			# Get form data
			api_key = request.form.get('api_key', '').strip()
			server = request.form.get('server', '').strip()
			server_id = request.form.get('server_id', '').strip()
			
			# Validate input (basic validation)
			if not api_key or not server or not server_id:
				error_message = "All fields are required"
			else:
				# Update config file
				update_config({
					'API_KEY': api_key,
					'SERVER': server,
					'SERVER_ID': server_id
				})
				
				# Update global variables
				global API_KEY, SERVER, SERVER_ID, WEB_PLAYER_URL, FULL_PLAYER_URL
				API_KEY = api_key
				SERVER = server
				SERVER_ID = server_id
				WEB_PLAYER_URL = f"{SERVER}/web/#/details?id="
				FULL_PLAYER_URL = f"{WEB_PLAYER_URL}{{item_id}}&serverId={SERVER_ID}"
				
				success_message = "Settings updated successfully"
				config_values = read_config()  # Refresh config values
		except Exception as e:
			error_message = f"Error updating settings: {str(e)}"
	
	# Render settings page
	return render_template_string(
		HTML_TEMPLATE,
		results=None,
		search_term='',
		is_favorites=False,
		is_settings=True,
		config_values=config_values,
		success_message=success_message,
		error_message=error_message,
		test_result=test_result,
		test_success=test_success
	)


@app.route('/settings/test', methods=['POST'])
def test_connection():
	# Get current config values
	config_values = read_config()
	
	# Variables for template
	test_result = None
	test_success = False
	
	# Test the connection to Jellyfin
	try:
		headers = {'X-Emby-Token': API_KEY}
		response = requests.get(f'{SERVER}/System/Info', headers=headers, timeout=10)
		
		if response.status_code == 200:
			server_info = response.json()
			server_name = server_info.get('ServerName', 'Unknown')
			version = server_info.get('Version', 'Unknown')
			test_result = f"Connection successful! Server: {server_name}, Version: {version}"
			test_success = True
		else:
			test_result = f"Connection failed: HTTP {response.status_code} - {response.reason}"
	except requests.exceptions.RequestException as e:
		test_result = f"Connection error: {str(e)}"
	
	# Render settings page with test results
	return render_template_string(
		HTML_TEMPLATE,
		results=None,
		search_term='',
		is_favorites=False,
		is_settings=True,
		config_values=config_values,
		success_message=None,
		error_message=None,
		test_result=test_result,
		test_success=test_success
	)


if __name__ == '__main__':
	import os
	# Check if we're in production mode
	debug_mode = os.environ.get('FLASK_ENV') != 'production'
	app.run(debug=debug_mode, host='0.0.0.0', port=5001)

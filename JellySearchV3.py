
from flask import Flask, render_template_string, request
import requests
import os
import sys

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    from config import API_KEY, SERVER, WEB_PLAYER_URL, FULL_PLAYER_URL
except ImportError:
    # Fallback for testing or when config is not available
    print("Warning: config.py not found. Please create it with your API_KEY, SERVER, and WEB_PLAYER_URL variables.")
    API_KEY = 'YOUR_API_KEY_HERE'  # This will cause an error when used, prompting proper setup
    SERVER = 'http://jf.brr.savethecdn.com:80'
    WEB_PLAYER_URL = f"{SERVER}/web/#/details?id="
    FULL_PLAYER_URL = f"{WEB_PLAYER_URL}{{item_id}}&serverId=YOUR_SERVER_ID_HERE"

app = Flask(__name__)

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
		<a href="/favorites" style="color: #00a4dc; text-decoration: none;">Favorites</a>
	</div>
	{% if not is_favorites %}
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
<script>
document.getElementById('search-form').addEventListener('submit', function() {
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
	return render_template_string(HTML_TEMPLATE, results=results, search_term=search_term, is_favorites=False)


@app.route('/favorites', methods=['GET'])
def favorites():
	results, _ = fetch_favorites()
	return render_template_string(HTML_TEMPLATE, results=results, search_term='', is_favorites=True)


if __name__ == '__main__':
	import os
	# Check if we're in production mode
	debug_mode = os.environ.get('FLASK_ENV') != 'production'
	app.run(debug=debug_mode, host='0.0.0.0', port=5000)

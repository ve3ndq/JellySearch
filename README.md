# JellySearch

A fast search application for Jellyfin media server.

## Features

- Quick search through your Jellyfin media library
- Display results in a clean, responsive interface
- Link directly to content in Jellyfin web player
- View favorites collection
- Simple and lightweight Flask-based web application

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ve3ndq/JellySearch.git
   cd JellySearch
   ```

2. Create and configure your environment:
   ```bash
   cp config.template.py config.py
   # Edit config.py with your Jellyfin API key and server information
   ```

3. Run the application:
   ```bash
   ./start.sh
   ```

## Configuration

Edit `config.py` with your Jellyfin server details:
- `API_KEY`: Your Jellyfin API key
- `SERVER`: Your Jellyfin server URL (including port)
- `SERVER_ID`: Your Jellyfin server ID

## Requirements

- Python 3.x
- Flask
- Requests

## License

See the [LICENSE](LICENSE) file for details.
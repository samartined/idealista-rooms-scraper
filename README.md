# Idealista Room Scraper

A Python-based web scraper for Idealista.com that helps you find rooms with included expenses. This is a work in progress project that aims to simplify the room hunting process by automatically checking if expenses are included in the rent.

## ⚠️ Disclaimer

This project is under active development and may have limitations or bugs. It's not perfect and might need adjustments based on Idealista's website changes. Use it responsibly and in accordance with Idealista's terms of service.

## Features

- Scrapes room listings from Idealista.com
- Automatically checks if expenses are included in the rent
- Saves results to a CSV file
- Includes local caching to reduce server load
- Configurable page range and delay between requests
- Headless browser operation using Firefox

## Requirements

- Python 3.x
- Firefox ESR
- Geckodriver

## Installation

1. Clone this repository:
```bash
git clone <https://github.com/samartined/idealista-rooms-scraper.git>
cd idealista-rooms-scraper
```

2. Install the required Python packages:
```bash
pip install -r requirements.txt
```

3. Make sure you have Firefox ESR and Geckodriver installed:
```bash
# For Ubuntu/Debian
sudo apt-get install firefox-esr
# Download and install geckodriver from https://github.com/mozilla/geckodriver/releases
```

## Getting the Idealista URL

To use the scraper, you need to get the correct URL from Idealista after applying your filters:

1. Go to [Idealista.com](https://www.idealista.com)
2. Click on "Rent" → "Room"
3. Apply your desired filters (location, price range, etc.)
4. Once you've applied all filters, copy the URL from your browser
5. The URL should look something like this:
   ```
   https://www.idealista.com/en/rent/room/madrid/center/300-500-euros/
   ```
6. Use this URL with the `-u` parameter in the scraper command

Note: Make sure to copy the URL before clicking on any specific listing, as the URL should end with your filter parameters.

## Usage

Run the scraper with the following command:

```bash
python idealista_scraper.py -u "https://www.idealista.com/your-search-url" -p START_PAGE END_PAGE -d MIN_DELAY MAX_DELAY -o output.csv
```

### Arguments

- `-u, --url`: Base Idealista URL with your search filters (without 'pagina-X')
- `-p, --pages`: Page range to scrape (start and end numbers)
- `-d, --delay`: Random delay range between requests in seconds (min and max)
- `-o, --output`: Output CSV filename (default: results.csv)

### Example

```bash
python idealista_scraper.py -u "https://www.idealista.com/alquiler-habitacion/madrid/" -p 1 5 -d 2 20 -o madrid_rooms.csv
```

## Output

The script generates a CSV file with the following columns:
- Price
- Expenses Included (✅ or ❌)
- Location
- Number of Rooms
- Link to the listing

## Limitations

- The scraper might break if Idealista changes their website structure
- Rate limiting might occur if too many requests are made
- Some listings might be missed due to dynamic content loading
- The expense detection is based on keyword matching and might not be 100% accurate

## Contributing

Feel free to submit issues and enhancement requests!

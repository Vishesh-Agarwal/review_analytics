Review Analyzer for Apps built for Hackathon on 29th September 2024

## How to run

Prerequisites:
- NodeJS
- Python


## Backend (Needs OpenAI API Key)
npm install -g pnpm
pnpm install

### On Linux
export OPENAI_API_KEY=XXXXX

### On Windows
$env:OPENAI_API_KEY = "XXXXX"

pnpm start


## Reviews Server
pip install flask google-play-scraper
python py-server.py

## Frontend
cd dashboard
pnpm install
pnpm dev

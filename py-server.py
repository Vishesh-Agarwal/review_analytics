# app.py

from flask import Flask, request, jsonify
import json
import logging
from google_play_scraper import Sort, reviews, app as play_app

app = Flask(__name__)

# Existing functions remain unchanged

def fetch_app_details(app_id):
    """Fetches app details from the Google Play Store."""
    try:
        app_details = play_app(app_id, lang='en', country='us')
        return app_details
    except Exception as e:
        logging.error(f"Error fetching app details: {e}")
        return None

def fetch_reviews(app_id, desired_count=600):
    """Fetches reviews for the specified app ID."""
    all_reviews = []
    continuation_token = None
    while len(all_reviews) < desired_count:
        remaining = desired_count - len(all_reviews)
        count = min(200, remaining)  # Maximum count per request is 200
        try:
            result, continuation_token = reviews(
                app_id,
                lang='en',
                country='us',
                sort=Sort.NEWEST,
                count=count,
                filter_score_with=None,
                continuation_token=continuation_token
            )
            all_reviews.extend(result)
            logging.info(f"Fetched {len(result)} reviews. Total so far: {len(all_reviews)}.")
            if not continuation_token:
                logging.info("No more reviews to fetch.")
                break
        except Exception as e:
            logging.error(f"Error fetching reviews: {e}")
            break
    return all_reviews

def extract_review_fields(reviews_list):
    """Extracts specific fields from the reviews."""
    extracted_reviews = []
    for review in reviews_list:
        extracted_reviews.append({
            'reviewId': review.get('reviewId'),
            'userName': review.get('userName'),
            'content': review.get('content'),
            'score': review.get('score'),
            'thumbsUpCount': review.get('thumbsUpCount'),
            'reviewCreatedVersion': review.get('reviewCreatedVersion')
        })
    return extracted_reviews

def save_to_file(data, file_name):
    """Saves the data to a JSON file."""
    try:
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        logging.info(f"Data saved to {file_name}")
    except Exception as e:
        logging.error(f"Error saving data to file: {e}")

# Flask route to handle the API request
@app.route('/fetch-reviews', methods=['GET'])
def fetch_reviews_endpoint():
    app_id = request.args.get('appId')
    if not app_id:
        return jsonify({'error': 'Missing appId parameter'}), 400

    logging.info(f"Fetching details for app: {app_id}")
    app_details = fetch_app_details(app_id)
    if not app_details:
        logging.error("Failed to fetch app details.")
        return jsonify({'error': 'Failed to fetch app details.'}), 500

    logging.info(f"Fetching reviews for app: {app_id}")
    reviews_list = fetch_reviews(app_id, desired_count=600)
    extracted_reviews = extract_review_fields(reviews_list)

    data_to_save = {
        'app': app_details,
        'reviews': extracted_reviews
    }

    file_name = f"{app_id}_reviews.json"
    save_to_file(data_to_save, file_name)

    return jsonify({'message': f'Data saved to {file_name}'}), 200

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(port=3002)

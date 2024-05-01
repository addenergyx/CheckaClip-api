import os
import random

from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
import requests
from pydantic import ValidationError

from validators import SearchRequest

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('FLASH_SECRET_KEY', 'secret_key')
app.config['YOUTUBE_API_KEY'] = os.environ.get('YOUTUBE_API_KEY')


def convert_to_embed_url(video_url: str) -> str:
    video_id = video_url.split('watch?v=')[1]
    return f'https://www.youtube.com/embed/{video_id}'


def fetch_youtube_shorts(search_term: str, max_results: int) -> list[str] | None:
    youtube_api_key = app.config['YOUTUBE_API_KEY']
    youtube_search_url = 'https://www.googleapis.com/youtube/v3/search'
    params = {
        'part': 'snippet',
        'q': search_term,
        'type': 'video',
        'maxResults': max_results,
        'key': youtube_api_key
    }
    response = requests.get(youtube_search_url, params=params)
    if response.status_code == 200:
        json_data = response.json()
        return [f"https://www.youtube.com/watch?v={x['id']['videoId']}" for x in json_data['items']]

    else:
        raise Exception("Failed to fetch data from YouTube")


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        search_term = request.form.get('search_term')

        if not search_term:
            flash('Search term is required', 'error')  # 'error' is a category for the flash message
            return redirect(url_for('home'))

        return redirect(url_for('results', search_term=search_term))
    return render_template('index.html')


@app.route('/results', methods=['GET'])
def results():
    search_term = request.args.get('search_term', None)

    # Internal request to the API endpoint for YouTube short
    shorts_response = requests.get(url_for('get_shorts', search_term=search_term, _external=True))
    video_url = shorts_response.json().get('urls') if shorts_response.ok else None

    embedded_video_url = convert_to_embed_url(video_url[0])

    # Internal request to the API endpoint for images
    images_response = requests.get(url_for('get_images', search_term=search_term, _external=True))
    image_urls = images_response.json()['urls'] if images_response.ok else []

    return render_template('results.html', video_url=embedded_video_url, image_urls=image_urls)


@app.route('/api/v1/shorts', methods=['GET'])
def get_shorts():
    try:
        search_args = SearchRequest(search_term=request.args.get('search_term', None),
                                    max_results=request.args.get('max_results', 5))
        video_url = fetch_youtube_shorts(search_args.search_term, search_args.max_results)
        return jsonify({'urls': video_url}), 200
    except ValidationError as ve:
        errors = {error['loc'][0]: error['msg'] for error in ve.errors()}
        return jsonify(errors), 400
    except Exception:
        return jsonify({"error": "Failed to fetch data from YouTube"}), 500


@app.route("/api/v1/images", methods=["GET"])
def get_images():
    try:
        search_args = SearchRequest(search_term=request.args.get('search_term', None))
    except ValidationError:
        return {'errors': {'search_term': 'ensure this value has at least 1 characters'}}, 400

    # https://www.flickr.com/services/feeds/docs/photos_public/
    response = requests.get(
        "https://www.flickr.com/services/feeds/photos_public.gne",
        params={
            "format": "json",
            "nojsoncallback": 1,  # return raw JSON
            "tags": search_args.search_term
        }
    )

    if response.status_code == 200:
        json_data = response.json()
        images = [x['media']['m'] for x in random.sample(json_data['items'], min(3, len(json_data['items'])))]
        return jsonify({"urls": images}), 200

    return jsonify({"error": ""}), response.status_code


if __name__ == '__main__':
    app.run(debug=True)

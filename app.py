import os
import random

from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_caching import Cache
import requests
from pydantic import ValidationError

from validators import SearchRequest

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('FLASH_SECRET_KEY', 'secret_key')
app.config['YOUTUBE_API_KEY'] = os.environ.get('YOUTUBE_API_KEY')

app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 300

cache = Cache(app)


def convert_to_embed_url(video_url: str) -> str:
    video_id = video_url.split('watch?v=')[1]
    return f'https://www.youtube.com/embed/{video_id}'


@cache.memoize(timeout=600)
def fetch_youtube_shorts(search_term: str, max_results: int) -> list[str] | None:

    # https://developers.google.com/youtube/v3/docs/search/list
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

    raise Exception("Failed to fetch data from YouTube")


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        search_term = request.form.get('search_term')

        if not search_term:
            flash('Search term is required', 'error')  # flash message requires a secret key
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
    image_url = images_response.json()['urls'][0] if images_response.ok else None

    return render_template('results.html', video_url=embedded_video_url, image_url=image_url)


def build_validation_error_response(errors: list[dict]) -> dict:
    return {
        'status': 400,
        'body': {
            'errors': {error['loc'][0]: error['msg'] for error in errors}
        }
    }


@app.route('/api/v1/shorts', methods=['GET'])
def get_shorts():
    try:
        search_args = SearchRequest(search_term=request.args.get('search_term', None),
                                    max_results=request.args.get('max_results', 5))
        video_url = fetch_youtube_shorts(search_args.search_term, search_args.max_results)
        return jsonify({'urls': video_url}), 200
    except ValidationError as ve:
        status_code = 400
        return build_validation_error_response(ve.errors()), status_code
    except Exception:
        return jsonify({"error": "Failed to fetch data from YouTube"}), 500


@cache.memoize(timeout=600)
def fetch_images(search_term: str) -> list[str] | None:
    # https://www.flickr.com/services/feeds/docs/photos_public/
    response = requests.get(
        "https://www.flickr.com/services/feeds/photos_public.gne",
        params={
            "format": "json",
            "nojsoncallback": 1,
            "tags": search_term
        }
    )
    if response.status_code == 200:
        return response.json()['items']
    raise Exception("Failed to fetch data from Flickr")


def randomise_images(images: list[any], default_max=3) -> list[str]:
    return [x['media']['m'] for x in random.sample(images, min(default_max, len(images)))]


@app.route("/api/v1/images", methods=["GET"])
def get_images():
    try:
        search_args = SearchRequest(search_term=request.args.get('search_term', None))
        images = fetch_images(search_args.search_term)
        randomised_images = randomise_images(images)
        return jsonify({"urls": randomised_images}), 200
    except ValidationError as ve:
        status_code = 400
        return build_validation_error_response(ve.errors()), status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)

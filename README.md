# CheckaClip

API and frontend for media search tool

## Pre-requisites:
Youtube Data API key
1. Create a project in the [Google Cloud Console](https://console.cloud.google.com/)
2. On the new project dashboard, click `APIs & Services` then `Enable APIs and Services`.
3. Search for and enable `Youtube Data API v3`
4. Click `Create Credentials` and select `public data`
5. Add the API key to the .env file in the root of the project

## How to run the app:
1. Clone the repository
2. cd into the repository
3. Run `make run` to start the app
App will run on http://127.0.0.1:5000

Tests can be run with `make tests`

## API
The API has the following endpoints:
- /api/v1/shorts - GET - Returns urls of short videos
- /api/v1/images - GET - Returns urls of images

query parameters:
- search_term: The search term to search for
- max_results: The maximum number of results to return

Example:
http://127.0.0.1:5000/api/v1/shorts?search_term=cats&max_results=5

returns
```json
{
  "urls": [
    "https://www.youtube.com/watch?v=3bhkYoMWTFE",
    "https://www.youtube.com/watch?v=NsMKvVdEPkw",
    "https://www.youtube.com/watch?v=Op3NJrb3mFg",
    "https://www.youtube.com/watch?v=5WwVTuQmmkg",
    "https://www.youtube.com/watch?v=BvJ0DVSFHkk"
  ]
}
```



## Notes: 
You may find that some embedded YouTube videos are showing "Video unavailable" when you try and view them in the app, like this: 
The reason for this may be that they have copyrighted music in the background and for copyright reasons, 
YouTube automatically blocks these from playing if the EMBED setting is ON.
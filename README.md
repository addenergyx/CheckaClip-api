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

Tests can be run with `make tests`

## Notes: 
You may find that some embedded YouTube videos are showing "Video unavailable" when you try and view them in the app, like this: 
The reason for this may be that they have copyrighted music in the background and for copyright reasons, 
YouTube automatically blocks these from playing if the EMBED setting is ON.
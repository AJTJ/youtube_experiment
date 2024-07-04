from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
)
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import json
import os
from googleapiclient.discovery import Resource
from dotenv import load_dotenv
from chromadb import Collection

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]


def search_videos(youtube: Resource, query, max_results=300):
    videos = []
    next_page_token = None
    while len(videos) < max_results:
        request = youtube.search().list(
            order="viewCount",
            part="snippet",
            q=query,
            type="video",
            maxResults=min(50, max_results - len(videos)),
            pageToken=next_page_token,
            videoDuration="medium",
        )

        # test if video has transcript

        """
            filter by having transcript
            filter by being popular
            filter by a heavy liked bias
            filter by a heavy commented bias

            load all json or format
            https://python.langchain.com/v0.1/docs/modules/data_connection/document_loaders/json/
            - how will this transform the data
            - embeddings primary key and then other columns and other things
            - we could add metadata as well to it
            https://python.langchain.com/v0.1/docs/modules/data_connection/document_transformers/recursive_json_splitter/

            Then you run indexing/create embeddings
            https://python.langchain.com/v0.1/docs/modules/data_connection/indexing/
            - which is creating embeddings from documents with a model

            create embeddings for your user query

            run semantic similarity search

            
            OTHER
            - get langchain project working
            - ...
        """

        response = request.execute()
        videos.extend(response["items"])

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return videos[:max_results]


def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript
    except (TranscriptsDisabled, NoTranscriptFound):
        return None
    except Exception as e:
        print(
            f"An error occurred while fetching transcript for video {video_id}: {str(e)}"
        )
        return None


def create_video_output(collection: Collection):

    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "client_secret.json"

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes
    )
    credentials = flow.run_local_server()
    youtube: Resource = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials
    )

    topic = "data science education"
    videos = search_videos(youtube, topic)

    results = []

    for i, video in enumerate(videos, 1):
        video_id = video["id"]["videoId"]
        title = video["snippet"]["title"]
        transcript = get_transcript(video_id)

        if transcript:
            video_data = {
                "title": title,
                "video_id": video_id,
                "transcript": transcript,
            }

            results.append(video_data)

        print(f"Processed video {i}/{len(videos)}: {title}")

    # Write results to a JSON file
    output_file = f"{topic.replace(' ', '_')}_transcripts.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print(f"Results saved to {output_file}")

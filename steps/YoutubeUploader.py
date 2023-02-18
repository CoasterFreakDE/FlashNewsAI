from googleapiclient.http import MediaFileUpload

from utils.google_apis import create_service


class YoutubeUploader:

    def __init__(self, video_file, title, description):
        self.video_file = video_file
        self.title = title
        self.description = description

    def upload(self):
        API_NAME = 'youtube'
        API_VERSION = 'v3'
        SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
        client_file = 'youtube_secret.json'
        youtube = create_service(client_file, API_NAME, API_VERSION, SCOPES)
        # Define the metadata for the video.
        request_body = {
            'snippet': {
                'title': self.title,
                'description': self.description
            },
            'notifySubscribers': True
        }

        media_file = MediaFileUpload(self.video_file)
        # Create the video insert request.
        response_video_upload = youtube.videos().insert(
            part='snippet,status',
            body=request_body,
            media_body=media_file
        ).execute()

        uploaded_video_id = response_video_upload.get('id')
        print(f'Video ID: {uploaded_video_id}')
        return uploaded_video_id

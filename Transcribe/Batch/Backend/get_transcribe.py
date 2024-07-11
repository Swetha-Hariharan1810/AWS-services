import time
import requests
import boto3

def transcribe_file(job_name, file_uri, transcribe_client):
    transcribe_client = boto3.client("transcribe")
    transcribe_client.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={"MediaFileUri": file_uri},
        MediaFormat="wav",
        LanguageCode="en-US",
    )

    max_tries = 60
    while max_tries > 0:
        max_tries -= 1
        job = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
        job_status = job["TranscriptionJob"]["TranscriptionJobStatus"]
        if job_status in ["COMPLETED", "FAILED"]:
            print(f"Job {job_name} is {job_status}.")
            if job_status == "COMPLETED":
                transcript_uri = job['TranscriptionJob']['Transcript']['TranscriptFileUri']
                response = requests.get(transcript_uri)
                if response.status_code == 200:
                    transcript = response.json()
                    print("Transcript contents:")
                    print(transcript)
                else:
                    print(f"Failed to fetch transcript: {response.status_code}")
            return transcript['results']['transcripts'][0]['transcript']
        else:
            print(f"Waiting for {job_name}. Current status is {job_status}.")
        time.sleep(3)

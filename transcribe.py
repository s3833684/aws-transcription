import time
import boto3
import requests
import os

def create_transcription(job_name):
    transcribe = boto3.client('transcribe', region_name='us-east-1')
    job_uri = "https://itisprojectbucket.s3.amazonaws.com/" + job_name +".mp4"
    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': job_uri},
        MediaFormat='mp4',
        LanguageCode='en-US'
    )
    while True:
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
        time.sleep(5)

def getFileURL(JobName):
    client = boto3.client('transcribe', region_name='us-east-1')
    response = client.get_transcription_job(TranscriptionJobName=JobName)
    url=response.get('TranscriptionJob').get('Transcript').get('TranscriptFileUri')

    return url

def check_job_exist(JobName):
    client = boto3.client('transcribe', region_name='us-east-1')

    entries = os.listdir('/home/ubuntu/flaskapp/static/')
    for entry in entries:
        if entry == JobName+".vtt":
            return True
    return False


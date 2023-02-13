# In this program we will read the transcript of a youtube video and summarize it

from youtube_transcript_api import YouTubeTranscriptApi
from utils import get_chunks_from_transcript, summarize_audio_transcript_chunks, set_diagnostics
import argparse
import os
import json
import openai
import streamlit as st

# OpenAI API Key
openai.api_key = st.secrets["OPENAIKEY"]

def get_video_id_from_video_id_or_url(video_id_or_url):
    # a youtube video id is 11 characters long
    # if the video id is longer than that, then it's a url
    if len(video_id_or_url) > 11:
        # it's a url
        # the video id is the last 11 characters
        return video_id_or_url[-11:]
    else:
        # it's a video id
        return video_id_or_url

def main():
    st.title ("Youtube Video Summarizer")

    video_id_or_url = st.text_input("Enter the video id or url of the video to summarize")

    chunk_len_mins = st.number_input("Enter the length of the chunks to summarize in minutes", min_value=1, max_value=60, value=10)

    if video_id_or_url:
        video_id = get_video_id_from_video_id_or_url(video_id_or_url)

        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=("en", "en-US", "en-GB"))

        # show some kind of progress bar
        progress = 0
        p = st.progress(progress)

        chunks = get_chunks_from_transcript(transcript, chunk_len_mins)

        # update the progress bar
        progress += 5
        p.progress(progress)

        # one progress step should be 90/len(chunks).
        progress_step = 80 / len(chunks)

        # summarize_audio_transcript_chunks yields chunks. Get each one and write it.
        for chunk in summarize_audio_transcript_chunks(chunks, "", chunk_len_mins):
            st.write(chunk)
            progress += progress_step
            progress = int(progress)
            p.progress(progress)

        p.progress(100)

if __name__ == "__main__":
    main()

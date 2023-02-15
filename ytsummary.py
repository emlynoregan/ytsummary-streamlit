# In this program we will read the transcript of a youtube video and summarize it

from youtube_transcript_api import YouTubeTranscriptApi
from utils import get_chunks_from_transcript, summarize_audio_transcript_chunks, set_diagnostics
import argparse
import os
import json
import openai
import streamlit as st
from tmw import tmwcheck, UnauthorizedError

# OpenAI API Key
openai.api_key = st.secrets["OPENAIKEY"]

def get_video_id_from_video_id_or_url(video_id_or_url):
    # a youtube video id is 11 characters long
    # if the video id is longer than that, then it's a url

    result = video_id_or_url

    # remove any extra query parameters
    if "&" in video_id_or_url:
        result = video_id_or_url.split("&")[0]

    if len(result) > 11:
        # it's a url
        # the video id is the last 11 characters
        return result[-11:]
    else:
        # it's a video id
        return result

def main():
    tenant_id = st.secrets["TENANT_ID"]

    try:
        info = tmwcheck()
    except UnauthorizedError as e:
        auth_url = e.get_auth_url(tenant_id)

        st.write(f"Unauthorized. Please click the link below to authorize this app.")

        # add a link that will open the auth url in a new tab
        st.markdown(f"[Authorize this app]({auth_url})")

        return
    
    # here we know the user is authorized

    user_name = (info.get('user') or {}).get('user_name')

    st.title ("Youtube Video Summarizer")
    st.write(f"Hello {user_name}!")

    video_id_or_url = st.text_input("Enter the url or id of the video to summarize")

    chunk_len_mins = st.number_input("Enter the length of the chunks to summarize in minutes", min_value=1, max_value=60, value=10)

    if video_id_or_url:
        video_id = get_video_id_from_video_id_or_url(video_id_or_url)
        
        # st.write(f"video_id: {video_id}")

        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=("en", "en-US", "en-GB"))

        # show some kind of progress bar
        progress = 0
        p = st.progress(progress)

        chunks = get_chunks_from_transcript(transcript, chunk_len_mins)

        # update the progress bar
        progress += 5
        p.progress(progress)

        # one progress step should be 90/len(chunks).
        progress_step = 90 / (len(chunks) + 1)

        # summarize_audio_transcript_chunks yields chunks. Get each one and write it.
        for chunk in summarize_audio_transcript_chunks(chunks, "", chunk_len_mins):
            st.write(chunk)
            progress += progress_step
            progress = int(progress)
            p.progress(progress)

        p.progress(100)

if __name__ == "__main__":
    main()

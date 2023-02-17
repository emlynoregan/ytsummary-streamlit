# In this program we will read the transcript of a youtube video and summarize it

from youtube_transcript_api import YouTubeTranscriptApi
from utils import get_chunks_from_transcript, summarize_audio_transcript_chunks, set_diagnostics
import argparse
import os
import json
import openai
import streamlit as st
from tmw import tmwcheck, tmwcheck_tenant, UnauthorizedError, has_scope, check_scope
from streamlit_cookies_manager import EncryptedCookieManager


# OpenAI API Key
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

    authorized = False
    unauth_error = None
    try:
        info = tmwcheck()
        # tmwcheck_tenant(tenant_id, info)
        check_scope(tenant_id, "public", info)
        authorized = True
    except UnauthorizedError as e:
        unauth_error = e

    if not authorized:
        # the user is not authorized

        auth_url = unauth_error.get_auth_url(tenant_id)

        public_signup_url = unauth_error.get_sign_up_url()

        st.title ("Youtube Video Summarizer")

        st.write ("You must sign in to use this app.")

        st.markdown(f"Click here to [Sign in]({auth_url})")
        st.markdown(f"Click here to [Sign up]({public_signup_url})")

        return
    
    # here we know the user is authorized
    user_name = (info.get('user') or {}).get('user_name')
    user_id = (info.get('user') or {}).get('user_id')

    st.title ("Youtube Video Summarizer")
    st.write(f"Hello {user_name}!")


    is_private = has_scope(tenant_id, "private", info)

    api_key = None
    cookies = EncryptedCookieManager(
        prefix = f"{user_id}/scm",
        password = st.secrets["COOKIES_PASSWORD"]
    )

    if not cookies.ready:
        st.stop()

    # users that are not private need to provide openai keys
    if is_private:
        api_key = st.secrets["OPENAIKEY"]
    else:
        api_key = cookies.get("openaikey")

    if not api_key:
        api_key = st.text_input("Enter your OpenAI API Key")

        if api_key:
            cookies["openaikey"] = api_key
            cookies.save()
            st.experimental_rerun()

    if not api_key:
        st.stop()

    try:        
        openai.api_key = api_key

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
    except openai.error.AuthenticationError as e:
        cookies["openaikey"] = ""
        cookies.save()
        raise e

if __name__ == "__main__":
    main()

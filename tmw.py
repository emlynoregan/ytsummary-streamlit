import streamlit as st
import webbrowser
import requests
# from streamlit_cookies_manager import EncryptedCookieManager

# st.write(st.user)

# cookies = EncryptedCookieManager(
#     prefix = st.secrets["COOKIES_PREFIX"],
#     password = st.secrets["COOKIES_PASSWORD"]
# )

# if not cookies.ready():
#     st.stop()

C_METALWIZARD_URL = "https://themetalwizard.net"
C_API_URL = "https://qiuh5okg6pk3ie6m43n36s66vi0quait.lambda-url.us-east-1.on.aws/info"
C_AUTH_URL_TEMPLATE = "https://themetalwizard.net/launch/{tenant_id}"

class UnauthorizedError(Exception):
    def __init__(self, message):
        self.message = message

    def get_auth_url(self, tenant_id):
        return C_AUTH_URL_TEMPLATE.format(tenant_id=tenant_id)

def tmwcheck():
    # get the querystring param "access_token" if it exists
    access_token = st.experimental_get_query_params().get("access_token", None)

    if access_token:
        access_token = access_token[0]
    if access_token == "None":
        access_token = None

    # st.write(access_token)
    # st.write(type(access_token))
    # raise Exception("xxx")

    #** I removed all storage of the access_token in the state or cookies because all methods either don't
    # survive a refresh or are global to all users. I'm just leaving the token in the querystring for now.

    # # if no access_token, then get access_token from the state
    # if not access_token:
    #     st.write('looking in cookies')
    #     # st.write(st.session_state)
    #     # access_token = st.session_state.get("access_token")
    #     access_token = cookies.get("access_token")
    #     st.write(access_token)
    # else:
    #     # remove the access_token from the querystring
    #     # st.write(access_token)
    #     st.experimental_set_query_params(access_token=None)

    if not access_token:
        raise UnauthorizedError("You must login to https://themetalwizard.net to use this app. (1)")
        # # webbrowser.open(C_METALWIZARD_URL)
        # raise Exception("You must login to https://themetalwizard.net to use this app. (1)")

    # # save the token in the state
    # # st.session_state["access_token"] = access_token
    # cookies["access_token"] = access_token
    # cookies.save()

    # st.write(access_token)

    # get the user info    
    r = requests.get(C_API_URL, headers={"Authorization": f"Bearer {access_token}"})

    if r.status_code != 200:
        raise UnauthorizedError("You must login to https://themetalwizard.net to use this app. (2)")
        # # st.write(f"Error: {r.status_code} {r.text}")
        # # webbrowser.open(C_METALWIZARD_URL)
        # raise Exception("You must login to https://themetalwizard.net to use this app. (2)")
    
    response_json = r.json()
    
    # st.write(response_json)

    expected_tenant_id = st.secrets["TENANT_ID"]

    tenants = (response_json.get("info") or {}).get("tenants") or {}

    if expected_tenant_id not in tenants:
        raise UnauthorizedError("You must login to https://themetalwizard.net to use this app. (3)")
        # # webbrowser.open(C_METALWIZARD_URL)
        # raise Exception("You must login to https://themetalwizard.net to use this app. (3)")

    # here we're good.

    return response_json
    

    


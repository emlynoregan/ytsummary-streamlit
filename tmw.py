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
    
    def get_sign_up_url(self):
        public_invite_url = st.secrets["PUBLIC_INVITE_URL"]
        return public_invite_url

def tmwcheck():
    # get the querystring param "access_token" if it exists
    access_token = st.experimental_get_query_params().get("access_token", None)

    if access_token:
        access_token = access_token[0]
    if access_token == "None":
        access_token = None

    if not access_token:
        raise UnauthorizedError("You must login to https://themetalwizard.net to use this app. (1)")

    r = requests.get(C_API_URL, headers={"Authorization": f"Bearer {access_token}"})

    if r.status_code != 200:
        raise UnauthorizedError("You must login to https://themetalwizard.net to use this app. (2)")
    
    response_json = r.json()

    st.write(response_json)

    return response_json

def tmwcheck_tenant(tenant_id, response_json):
    tenants = (response_json.get("info") or {}).get("tenants") or {}

    if tenant_id not in tenants:
        raise UnauthorizedError("You must login to https://themetalwizard.net to use this app. (3)")

    return response_json

def has_scope(tenant_id, scope, response_json):

    scopes = (((response_json.get("info") or {}).get("tenants") or {}).get(tenant_id) or {}).get("scopes") or []

    return scope in scopes
    
def check_scope(tenant_id, scope, response_json):
    if not has_scope(tenant_id, scope, response_json):
        raise UnauthorizedError("You must login to https://themetalwizard.net to use this app. (4)")

    return response_json    


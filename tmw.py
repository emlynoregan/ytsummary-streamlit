import streamlit as st
import requests
from streamlit_cookies_manager import EncryptedCookieManager

C_METALWIZARD_URL = "https://themetalwizard.net"
C_API_URL = "https://qiuh5okg6pk3ie6m43n36s66vi0quait.lambda-url.us-east-1.on.aws/info"
C_AUTH_URL_TEMPLATE = "https://themetalwizard.net/launch/{tenant_id}"

def get_sign_up_url(force_sign_in=False):
    public_invite_url = st.secrets["PUBLIC_INVITE_URL"]
    if force_sign_in:
        public_invite_url += "?force_sign_in=true"
    return public_invite_url

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

    if not access_token:
        raise UnauthorizedError("You must login to https://themetalwizard.net to use this app. (1)")

    r = requests.get(C_API_URL, headers={"Authorization": f"Bearer {access_token}"})

    if r.status_code != 200:
        raise UnauthorizedError("You must login to https://themetalwizard.net to use this app. (2)")
    
    response_json = r.json()

    # st.write(response_json)

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

def auth_with_tmw():
    tenant_id = st.secrets["TENANT_ID"]

    authorized = False
    info = None
    try:
        info = tmwcheck()
        authorized = has_scope(tenant_id, "public", info) or has_scope(tenant_id, "private", info)
    except UnauthorizedError as e:
        pass

    # st.write(info)

    user = info and info.get("user")
    if user:
        user_name = (user or {}).get('user_name')
        user_id = (user or {}).get('user_id')

        public_signup_url_force = get_sign_up_url(True)

        st.markdown(f"Hello {user_name}! [not you?]({public_signup_url_force})")
    else:
        st.write("Hello mysterious stranger!")
    
    if not authorized:
        public_signup_url = get_sign_up_url()

        if user:
            st.write ("You are not authorized to use this app.")

            st.markdown(f"[Click here for authorization]({public_signup_url})")
        else:
            st.markdown(f"[Click here to sign in]({public_signup_url})")

        st.write("*Are you using this app on a mobile device? If you clicked a link in a message to get here, and the link above wont work for you, you may need to open this app in your browser (chrome or safari) first.*")

        st.stop()
    
    is_private = has_scope(tenant_id, "private", info)

    api_key = None
    cookies = EncryptedCookieManager(
        prefix = f"{user_id}/scm",
        password = st.secrets["COOKIES_PASSWORD"]
    )

    if not cookies.ready():
        st.stop()

    # users that are not private need to provide openai keys
    if is_private:
        api_key = st.secrets["OPENAIKEY"]
    else:
        api_key = cookies.get("openaikey")

    if not api_key:
        st.write("You need to provide an OpenAI API Key to use this app.")

        st.markdown("You can get the key from [OpenAI](https://openai.com/).")

        api_key = st.text_input("Enter your OpenAI API Key")

        if api_key:
            cookies["openaikey"] = api_key
            cookies.save()
            st.experimental_rerun()

    if not api_key:
        st.stop()
    else:
        return api_key, cookies
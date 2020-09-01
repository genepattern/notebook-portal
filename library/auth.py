import json
import requests
from django.contrib import auth
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.utils.deprecation import MiddlewareMixin
from requests import HTTPError
from rest_framework import authentication
from rest_framework import exceptions

from library import settings


def lazily_create_user(username, password_or_token):
    """Lazily create the Django user object"""
    try: user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = User()
        user.username = username
        user.set_password(password_or_token)
        user.save()
    return user


def login_from_password(username, password):
    """
    Call the GenePattern server to verify credentials
    :param username:
    :param password:
    :return:
    """
    # Set the necessary params
    params = dict(
        grant_type="password",
        username=username,
        password=password,
        client_id="GenePatternNotebookLibrary"
    )

    # Make the request of the GenePattern server
    url = settings.BASE_GENEPATTERN_URL + "/rest/v1/oauth2/token"
    resp = requests.post(url, params=params, data='', headers={"Accept": "application/json"})

    # Handle the response
    if resp is not None and resp.status_code == 200:
        # Decode the access token
        response_payload = json.loads(resp.content)

        # Lazily create the Django user object
        user = lazily_create_user(username, password)

        # Return the username
        return (user, response_payload['access_token'])
    else:
        # This is likely a 400 Bad Request error due to an invalid username or password
        raise exceptions.AuthenticationFailed('Invalid username or password')


def login_from_cookie(request):
    """Handle login via the GenePattern session cookie"""

    token = request.COOKIES.get('GenePatternAccess')
    if token is None: return None

    # Attempt to call the username endpoint
    url = settings.BASE_GENEPATTERN_URL + "/rest/v1/config/user"
    try:
        resp = requests.get(url, headers={"Authorization": "Bearer " + token})
        resp.raise_for_status()
        resp_json = resp.json()
        username = resp_json['result']

        # Lazily create the Django user object
        user = lazily_create_user(username, token)

        # Return the username
        return { "username": username, "user": user, "token": token, }

    # An error means we can't verify authentication, redirect to login page
    except HTTPError as e: pass

    # Fall back to logging in via login form if cookie is invalid or not available
    return None


class GenePatternAuthenticationBackend(ModelBackend):
    """
    Base Django authentication using the GenePattern server
    """

    def authenticate(self, request, *args, **kwargs):

        # First attempt to authenticate through the GenePattern cookie
        cookie_login = login_from_cookie(request)
        if cookie_login is not None:
            return cookie_login['user']

        # Get the login credentials
        if kwargs:
            username = kwargs.pop("username", None)
            password = kwargs.pop("password", None)
        else:
            return None

        # Call GenePattern server
        try:
            user, token = login_from_password(username, password)
            return user
        except exceptions.AuthenticationFailed:
            return None


class GenePatternAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):

        # First attempt to authenticate through the GenePattern cookie
        cookie_login = login_from_cookie(request)
        if cookie_login is not None:
            return (cookie_login['username'], cookie_login['token'])

        # Get the login credentials
        if 'username' in request.POST and 'password' in request.POST:
            username = request.POST['username']
            password = request.POST['password']
        else:
            return None

        # Call GenePattern server
        return login_from_password(username, password)


class AutomaticUserLoginMiddleware(MiddlewareMixin):
    """Attempt to automatically login if GenePattern cookie is present"""

    def process_view(self, request, view_func, view_args, view_kwargs):
        """Check for the cookie if not logged in"""
        if not AutomaticUserLoginMiddleware._is_user_authenticated(request):
            user = auth.authenticate(request)
            if user is None: return            # No cookie or cannot verify, do not do login

            # Log the user in
            request.user = user
            auth.login(request, user)

    @staticmethod
    def _is_user_authenticated(request):
        user = request.user
        return user and user.is_authenticated

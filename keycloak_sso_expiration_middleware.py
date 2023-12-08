import logging

import jwt

import requests

from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import logout, get_backends
from django.urls import reverse
from django.shortcuts import redirect
from django.http import HttpResponse

from social_django.models import UserSocialAuth
from social_core.backends.keycloak import KeycloakOAuth2

class KeycloakSSOExpirationMiddleware(MiddlewareMixin):

    def __init__(self, get_response):
        super().__init__(get_response)
        self.keycloak = KeycloakOAuth2()

    def _sso_expire(self, request):

        logger = logging.getLogger('KeycloakSSOExpirationMiddleware')

        logger.debug("Processing request..")

        if request.user.is_anonymous:
            return

        user = request.user

        # handle django 1.4 pickling bug
        if hasattr(user, '_wrapped') and hasattr(user, '_setup'):
            if user._wrapped.__class__ == object:
                user._setup()
            user = user._wrapped

        try:
            social_auth_user = user.social_auth.get(provider='keycloak')
        except UserSocialAuth.DoesNotExist as error:
            logger.debug('User does not exist in Keycloak Social Auth provider')
            return

        if self.is_social_auth_user_token_valid(social_auth_user):
            logger.debug('Access token is valid')
            return

        logger.debug('Access token is no longer valid')

        try:
            resp = self.keycloak.refresh_token(social_auth_user.extra_data['refresh_token'])

            social_auth_user.extra_data['access_token'] = resp['access_token']
            social_auth_user.extra_data['refresh_token'] = resp['refresh_token']

            social_auth_user.save()

            logger.debug('Refreshed access token')
        except requests.exceptions.HTTPError as error:
            status_code = error.response.status_code

            logger.debug('Got unexpected status code')
            logger.debug(status_code)

            # Maybe this should only be done on 401?
            logout(request)

            return redirect(reverse('login'))

    def is_social_auth_user_token_valid(self, social_auth_user: UserSocialAuth) -> bool:
        try:
            payload = self.keycloak.user_data(social_auth_user.extra_data['access_token'])
            return True
        except jwt.exceptions.ExpiredSignatureError:
            return False

    def process_request(self, request):
        return self._sso_expire(request)

    def process_response(self, request, response):
        return response

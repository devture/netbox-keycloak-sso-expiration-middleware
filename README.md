# Keycloak SSO Expiration middleware for NetBox

This custom middleware for [NetBox](https://docs.netbox.dev/) helps to destroy user sessions (on the NetBox side) whenever the JWT token coming from [Keycloak](https://www.keycloak.org/) expires.

The normal NetBox behavior when SSO is used is to keep user login sessions forever, regardless of how long the JWT token is valid for.

This HTTP request middleware does the following:

- checks the validity of the JWT token. If valid (not expired yet), the request immediately proceeds
- if the JWT token has expired, it tries to obtain a new one by using the `refresh_token`
  - if successful, the user session is updated to use then new authentication token and refresh token
  - if unsuccessful, the user session is destroyed (the user gets logged out of NetBox)

**This middleware is Keycloak-specific**, but may be adapted to work for other SSO providers that are part of [python-social-auth](http://python-social-auth.readthedocs.org/)


## Installation

To enable this middleware, you need to:

- put it on the Python packages path (e.g. `/opt/netbox/venv/lib/python3.10/site-packages/keycloak_sso_expiration_middleware.py` when using the [`netboxcommunity/netbox` container image](https://hub.docker.com/r/netboxcommunity/netbox))

- add it to the `settings.py` file (e.g. `/opt/netbox/netbox/netbox/settings.py` when using the [`netboxcommunity/netbox` container image](https://hub.docker.com/r/netboxcommunity/netbox))

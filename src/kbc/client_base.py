"""
Created on 5. 10. 2018

@author: esner
"""
import requests
import logging
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class HttpClientBase:
    """
    Base class for implementing a single Http client related to some REST API.

    """

    def __init__(self, base_url, max_retries=10, backoff_factor=0.3,
                 status_forcelist=(500, 502, 504), default_http_header=[], auth=None, default_params=None):
        """
        Create an endpoint.

          Args:
            base_url: The base URL for this endpoint. e.g. https://exampleservice.com/api_v1/
            max_retries: Total number of retries to allow.
            backoff_factor:  A back-off factor to apply between attempts.
            status_forcelist:  A set of HTTP status codes that we should force a retry on. e.g. [500,502]
            default_http_header (dict): Default header to be sent with each request
                                        eg. {'Authorization': 'Bearer ' + token,
                                                       'Content-Type' : 'application/json',
                                                       'Accept' : 'application/json'}
            auth: Default Authentication tuple or object to attach to (from  requests.Session().auth).
                  eg. auth = (user, password)
            default_params: default parameters to be sent with each request

        """
        if not base_url:
            raise ValueError("Base URL is required.")
        self.base_url = base_url
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.status_forcelist = status_forcelist
        self._auth = auth
        self._auth_header = default_http_header
        self._default_params = default_params

    def requests_retry_session(self, session=None):
        session = session or requests.Session()
        retry = Retry(
            total=self.max_retries,
            read=self.max_retries,
            connect=self.max_retries,
            backoff_factor=self.backoff_factor,
            status_forcelist=self.status_forcelist,
            method_whitelist=('GET', 'POST', 'PATCH', 'UPDATE')
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def _get_raw(self, url, params=None, **kwargs):
        """
        Construct a requests GET call with args and kwargs and process the
        results.


        Args:
            url (str): requested url
            params (dict): additional url params to be passed to the underlying
                requests.get
            **kwargs: Key word arguments to pass to the get requests.get

        Returns:
            r (requests.Response): :class:`Response <Response>` object.

        Raises:
            requests.HTTPError: If the API request fails.
        """
        s = requests.Session()
        s.auth = self._auth

        headers = kwargs.pop('headers', {})
        headers.update(self._auth_header)
        s.headers.update(headers)
        # set default params
        if self._default_params:
            params = self._default_params.update(params)

        r = self.requests_retry_session(session=s).request('GET', url=url, params=params, auth=self._auth, **kwargs)
        try:
            r.raise_for_status()
        except requests.HTTPError:
            # Handle different error codes
            raise Exception('Request failed with code: {}, message: {}'.format(r.status_code, r.text))
        else:
            return r

    def get(self, url, params=None, **kwargs):
        r = self._get_raw(url, params, **kwargs)
        return r.json()

    def _post_raw(self, *args, **kwargs):
        """
        Construct a requests POST call with args and kwargs and process the
        results.

        Args:
            *args: Positional arguments to pass to the post request.
            **kwargs: Key word arguments to pass to the post request.

        Returns:
            Response: Returns :class:`Response <Response>` object.

        Raises:
            requests.HTTPError: If the API request fails.
        """
        s = requests.Session()
        headers = kwargs.pop('headers', {})
        headers.update(self._auth_header)
        s.headers.update(headers)
        s.auth = self._auth

        params = kwargs.pop('params')
        # set default params
        if self._default_params:
            kwargs.update({'params': self._default_params.update(params)})

        r = self.requests_retry_session(session=s).request('POST', *args, **kwargs)
        try:
            r.raise_for_status()
        except requests.HTTPError as e:
            logging.warning(e, exc_info=True)
            # Handle different error codes
            raise
        else:
            return r

    def post(self, *args, **kwargs):
        """
        Construct a requests POST call with args and kwargs and process the
        results.

        Args:
            *args: Positional arguments to pass to the post request.
            **kwargs: Key word arguments to pass to the post request.

        Returns:
            body: json reposonse json-encoded content of a response

        Raises:
            requests.HTTPError: If the API request fails.
        """
        s = requests.Session()
        headers = kwargs.pop('headers', {})
        headers.update(self._auth_header)

        params = kwargs.pop('params', {})
        # set default params
        if self._default_params:
            kwargs.update({'params': self._default_params.update(params)})
        r = self.requests_retry_session(session=s).request('POST', headers=headers, *args, **kwargs)
        try:
            r.raise_for_status()
        except requests.HTTPError as e:
            logging.warning(e, exc_info=True)
            # Handle different error codes
            raise
        else:
            return r.json()

    def _patch(self, *args, **kwargs):
        """
        Construct a requests POST call with args and kwargs and process the
        results.

        Args:
            *args: Positional arguments to pass to the post request.
            **kwargs: Key word arguments to pass to the post request.

        Returns:
            body: Response body parsed from json.

        Raises:
            requests.HTTPError: If the API request fails.
        """
        headers = kwargs.pop('headers', {})
        headers.update(self._auth_header)
        r = requests.patch(headers=headers, *args, **kwargs)
        try:
            r.raise_for_status()
        except requests.HTTPError as e:
            logging.warning(e, exc_info=True)
            # Handle different error codes
            raise
        else:
            return r

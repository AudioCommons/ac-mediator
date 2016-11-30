from django.test import TestCase
from api.models import ApiClient
from accounts.models import Account
from django.core.urlresolvers import reverse


class OAuth2TestCase(TestCase):

    def setUp(self):

        # Create users
        self.dev_user = Account.objects.create_user('dev', password='devpass')
        self.end_user_password = 'endpass'
        self.end_user = Account.objects.create_user('end', password=self.end_user_password)

        # Create clients
        ApiClient.objects.create(
            name='PublicImplicitClient',
            user=self.dev_user,
            agree_tos=True,
            client_type=ApiClient.CLIENT_PUBLIC,
            authorization_grant_type=ApiClient.GRANT_IMPLICIT,
            redirect_uris='http://example.com',
            password_grant_is_allowed=False,
        )
        ApiClient.objects.create(
            name='PublicPasswordClient',
            user=self.dev_user,
            agree_tos=True,
            client_type=ApiClient.CLIENT_PUBLIC,
            authorization_grant_type=ApiClient.GRANT_PASSWORD,
            redirect_uris='',
            password_grant_is_allowed=False,  # Start at not allowed
        )
        ApiClient.objects.create(
            name='ConfidentialAuthorizationCodeClient',
            user=self.dev_user,
            agree_tos=True,
            client_type=ApiClient.CLIENT_CONFIDENTIAL,
            authorization_grant_type=ApiClient.GRANT_AUTHORIZATION_CODE,
            redirect_uris='http://example.com',
            password_grant_is_allowed=False,
        )

    @staticmethod
    def get_params_from_url(url):
        params_part = url.split('?')[1]
        return {item.split('=')[0]: item.split('=')[1] for item in params_part.split('&')}

    @staticmethod
    def fragment_params_from_url(url):
        params_part = url.split('#')[1]
        return {item.split('=')[0]: item.split('=')[1] for item in params_part.split('&')}

    def check_dict_has_fields(self, dictionary, fields):
        for field in fields:
            self.assertIn(field, dictionary)

    def check_access_token_response_fields(self, resp):
        self.check_dict_has_fields(
            resp.json(), ['expires_in', 'scope', 'refresh_token', 'access_token', 'token_type'])

    def check_redirect_uri_access_token_frag_params(self, params):
        self.check_dict_has_fields(
            params, ['expires_in', 'scope', 'access_token', 'token_type'])

    def test_password_grant_flow(self):

        # Return 'unauthorized_client' when trying password grant with a client of other authorization_grant_type
        client = ApiClient.objects.get(name='PublicImplicitClient')
        resp = self.client.post(
            reverse('oauth2_provider:token'),
            {
                'client_id': client.client_id,
                'grant_type': 'password',
                'username': self.end_user.username,
                'password': self.end_user_password,
            })
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json()['error'], 'unauthorized_client')

        # Return 'unauthorized_client' when trying password grant with a client with authorization_grant_type
        # set to 'password' but with 'password_grant_is_allowed' set to False
        client = ApiClient.objects.get(name='PublicPasswordClient')
        resp = self.client.post(
            reverse('oauth2_provider:token'),
            {
                'client_id': client.client_id,
                'grant_type': 'password',
                'username': self.end_user.username,
                'password': self.end_user_password,
            })
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json()['error'], 'unauthorized_client')

        # Return 200 OK when trying password grant with a client with authorization_grant_type
        # set to 'password' and with 'password_grant_is_allowed' set to True
        client.password_grant_is_allowed = True
        client.save()
        resp = self.client.post(
            reverse('oauth2_provider:token'),
            {
                'client_id': client.client_id,
                'grant_type': 'password',
                'username': self.end_user.username,
                'password': self.end_user_password,
            })
        self.assertEqual(resp.status_code, 200)
        self.check_access_token_response_fields(resp)

        # Return 'invalid_client' when missing client_id
        resp = self.client.post(
            reverse('oauth2_provider:token'),
            {
                #'client_id': client.client_id,
                'grant_type': 'password',
                'username': self.end_user.username,
                'password': self.end_user_password,
            })
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json()['error'], 'invalid_client')

        # Return 'invalid_client' when client_id does not exist in db
        resp = self.client.post(
            reverse('oauth2_provider:token'),
            {
                'client_id': 'thi5i5aninv3nt3dcli3ntid',
                'grant_type': 'password',
                'username': self.end_user.username,
                'password': self.end_user_password,
            })
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json()['error'], 'invalid_client')

        # Return 'unsupported_grant_type' when grant type does not exist
        resp = self.client.post(
            reverse('oauth2_provider:token'),
            {
                'client_id': client.client_id,
                'grant_type': 'invented_grant',
                'username': self.end_user.username,
                'password': self.end_user_password,
            })
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['error'], 'unsupported_grant_type')

        # Return 'invalid_request' when no username is provided
        resp = self.client.post(
            reverse('oauth2_provider:token'),
            {
                'client_id': client.client_id,
                'grant_type': 'password',
                #'username': self.end_user.username,
                'password': self.end_user_password,
            })
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['error'], 'invalid_request')

        # Return 'invalid_request' when no password is provided
        resp = self.client.post(
            reverse('oauth2_provider:token'),
            {
                'client_id': client.client_id,
                'grant_type': 'password',
                'username': self.end_user.username,
                #'password': self.end_user_password,
            })
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['error'], 'invalid_request')

    def test_implicit_grant_flow(self):

        # Redirect to login page when visiting authorize page with an AnonymousUser
        client = ApiClient.objects.get(name='PublicImplicitClient')
        resp = self.client.get(
            reverse('oauth2_provider:authorize'),
            {
                'client_id': client.client_id,
                'response_type': 'token',
            })
        self.assertIn('/login/', resp.url)

        # Redirect includes 'error' param when using non existing response type
        self.client.login(username=self.end_user.username, password=self.end_user_password)
        resp = self.client.get(
            reverse('oauth2_provider:authorize'),
            {
                'client_id': client.client_id,
                'response_type': 'non_existing_response_type',
            })
        self.assertEquals(resp.url.startswith(client.default_redirect_uri), True)
        resp_params = self.get_params_from_url(resp.url)
        self.check_dict_has_fields(resp_params, ['error'])
        self.assertEqual(resp_params['error'], 'unsupported_response_type')

        # Redirect includes 'error' param when using non supported response type
        resp = self.client.get(
            reverse('oauth2_provider:authorize'),
            {
                'client_id': client.client_id,
                'response_type': 'code',
            })
        self.assertEquals(resp.url.startswith(client.default_redirect_uri), True)
        resp_params = self.get_params_from_url(resp.url)
        self.check_dict_has_fields(resp_params, ['error'])
        self.assertEqual(resp_params['error'], 'unauthorized_client')

        # Authorization page is displayed with errors with non existing client_id
        resp = self.client.get(
            reverse('oauth2_provider:authorize'),
            {
                'client_id': 'thi5i5aninv3nt3dcli3ntid',
                'response_type': 'code',
            })
        self.assertEqual(resp.status_code, 400)
        self.assertIn('Invalid client_id parameter value', str(resp.content))

        #  Authorization page is displayed correctly when correct response_type and client_id
        resp = self.client.get(
            reverse('oauth2_provider:authorize'),
            {
                'client_id': client.client_id,
                'response_type': 'token',
            })
        self.assertEqual(resp.status_code, 200)
        self.assertIn('name="allow" value="Authorize"', str(resp.content))

        # Final redirect includes token params
        resp = self.client.post(
            reverse('oauth2_provider:authorize'),
            {
                'client_id': client.client_id,
                'response_type': 'token',
                'redirect_uri': client.default_redirect_uri,
                'scope': 'read',
                'state': 'an_optional_state',
                'allow': 'Authorize',
            })
        self.assertEquals(resp.url.startswith(client.default_redirect_uri), True)
        resp_fragment_params = self.fragment_params_from_url(resp.url)
        self.assertEquals(resp_fragment_params['state'], 'an_optional_state')  # Check state is returned and preserved
        self.assertEquals('refresh_token' in resp_fragment_params, False)  # Check that refresh token is not returned
        self.check_redirect_uri_access_token_frag_params(resp_fragment_params)  # Check other params

    def test_authorization_code_grant_flow(self):

        # Redirect to login page when visiting authorize page with an AnonymousUser
        client = ApiClient.objects.get(name='ConfidentialAuthorizationCodeClient')
        resp = self.client.get(
            reverse('oauth2_provider:authorize'),
            {
                'client_id': client.client_id,
                'response_type': 'code',
            })
        self.assertIn('/login/', resp.url)

        # Redirect includes 'error' param when using non existing response type
        self.client.login(username=self.end_user.username, password=self.end_user_password)
        resp = self.client.get(
            reverse('oauth2_provider:authorize'),
            {
                'client_id': client.client_id,
                'response_type': 'non_existing_response_type',
            })
        self.assertEquals(resp.url.startswith(client.default_redirect_uri), True)
        resp_params = self.get_params_from_url(resp.url)
        self.check_dict_has_fields(resp_params, ['error'])
        self.assertEqual(resp_params['error'], 'unsupported_response_type')

        # Redirect includes 'error' param when using non supported response type
        resp = self.client.get(
            reverse('oauth2_provider:authorize'),
            {
                'client_id': client.client_id,
                'response_type': 'token',
            })
        self.assertEquals(resp.url.startswith(client.default_redirect_uri), True)
        resp_params = self.get_params_from_url(resp.url)
        self.check_dict_has_fields(resp_params, ['error'])
        self.assertEqual(resp_params['error'], 'unauthorized_client')

        # Authorization page is displayed with errors with non existing client_id
        resp = self.client.get(
            reverse('oauth2_provider:authorize'),
            {
                'client_id': 'thi5i5aninv3nt3dcli3ntid',
                'response_type': 'code',
            })
        self.assertEqual(resp.status_code, 400)
        self.assertIn('Invalid client_id parameter value', str(resp.content))

        #  Authorization page is displayed correctly when correct response_type and client_id
        resp = self.client.get(
            reverse('oauth2_provider:authorize'),
            {
                'client_id': client.client_id,
                'response_type': 'code',
            })
        self.assertEqual(resp.status_code, 200)
        self.assertIn('name="allow" value="Authorize"', str(resp.content))

        # Redirect includes 'code' and 'state' params
        resp = self.client.post(
            reverse('oauth2_provider:authorize'),
            {
                'client_id': client.client_id,
                'response_type': 'code',
                'redirect_uri': client.default_redirect_uri,
                'scope': 'read',
                'state': 'an_optional_state',
                'allow': 'Authorize',
            })
        self.assertEquals(resp.url.startswith(client.default_redirect_uri), True)
        resp_params = self.get_params_from_url(resp.url)
        self.assertEquals(resp_params['state'], 'an_optional_state')  # Check state is returned and preserved
        self.check_dict_has_fields(resp_params, ['code'])  # Check code is there

        # Return 200 OK 'access_denied' when requesting access token setting client_id and client_secret in body params
        code = resp_params['code']
        resp = self.client.post(
            reverse('oauth2_provider:token'),
            {
                'client_id': client.client_id,
                'client_secret': client.client_secret,
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': client.default_redirect_uri
            })
        self.assertEqual(resp.status_code, 200)
        self.check_access_token_response_fields(resp)

        # Return 'invalid_client' when trying to get access without client_secret
        code = resp_params['code']
        resp = self.client.post(
            reverse('oauth2_provider:token'),
            {
                'client_id': client.client_id,
                #'client_secret': client.client_secret,
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': client.default_redirect_uri
            })
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json()['error'], 'invalid_client')

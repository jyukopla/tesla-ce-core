#  Copyright (c) 2021 Xavier Baró
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU Affero General Public License as
#      published by the Free Software Foundation, either version 3 of the
#      License, or (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU Affero General Public License for more details.
#
#      You should have received a copy of the GNU Affero General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
""" Tests for users administration """
import pytest

from tests.conftest import get_random_string

from tests import auth_utils


@pytest.mark.django_db
def test_api_admin_user(rest_api_client, user_global_admin):
    """
        CRUD for users without institution
    """
    # Set global admin user.
    client = auth_utils.client_with_user_obj(user_global_admin)

    # Create a new user
    user_name = get_random_string(10)
    password = get_random_string(10)
    email = '{}@tesla-ce.eu'.format(user_name)
    user_data = {
        'username': user_name,
        'uid': user_name,
        'email': email,
        'first_name': user_name[:5],
        'last_name': user_name[5:],
        'login_allowed': True,
        'is_active': True,
        'is_staff': False,
        'password': password,
        'password2': password
    }
    user_create_resp = client.post('/api/v2/admin/user/', data=user_data, type='json')
    assert user_create_resp.status_code == 201

    # Ensure that this user cannot authenticate, as is not in any institution and is not an GLOBAL_ADMIN
    try:
        auth_utils.client_with_user_credentials(email, password)
        pytest.fail('User without institution and admin privileges should not be able to login')
    except AssertionError:
        pass

    # Grant administration privileges
    user_mod_resp = client.patch(
        '/api/v2/admin/user/{}/'.format(user_create_resp.data['id']),
        data={'is_staff': True},
        type='json'
    )
    assert user_mod_resp.status_code == 200

    # Get the user profile
    user_client = auth_utils.client_with_user_credentials(email, password)
    profile = auth_utils.get_profile(user_client)

    assert len(profile['roles']) == 1
    assert 'GLOBAL_ADMIN' in profile['roles']
    assert profile['username'] == user_name
    assert profile['email'] == email
    assert profile['first_name'] == user_name[:5]
    assert profile['last_name'] == user_name[5:]

    # Find for this user by email
    find_user_resp = client.get('/api/v2/admin/user/?email={}'.format(email))
    assert find_user_resp.status_code == 200
    assert find_user_resp.data['count'] == 1
    assert find_user_resp.data['results'][0]['id'] == profile['id']

    # Remove the user
    user_del_resp = client.delete(
        '/api/v2/admin/user/{}/'.format(user_create_resp.data['id'])
    )
    assert user_del_resp.status_code == 204

    # Ensure that this user does not exist
    find2_user_resp = client.get('/api/v2/admin/user/?email={}'.format(email))
    assert find2_user_resp.status_code == 200
    assert find2_user_resp.data['count'] == 0


@pytest.mark.django_db
def test_api_admin_institution_user(rest_api_client, user_global_admin, institution_test_case):
    """
        CRUD for users with institution
    """
    # Set global admin user.
    client = auth_utils.client_with_user_obj(user_global_admin)

    # Create a new user
    user_name = get_random_string(10)
    password = get_random_string(10)
    email = '{}@tesla-ce.eu'.format(user_name)
    user_data = {
        'username': user_name,
        'uid': user_name,
        'email': email,
        'first_name': user_name[:5],
        'last_name': user_name[5:],
        'login_allowed': True,
        'is_active': True,
        'is_staff': False,
        'institution_id': institution_test_case['institution'].id,
        'password': password,
        'password2': password
    }
    user_create_resp = client.post('/api/v2/admin/user/', data=user_data, type='json')
    assert user_create_resp.status_code == 201

    # Get the user profile
    user_client = auth_utils.client_with_user_credentials(email, password)
    profile = auth_utils.get_profile(user_client)

    assert len(profile['roles']) == 0
    assert 'institution' in profile
    assert profile['institution']['id'] == institution_test_case['institution'].id
    assert profile['email'] == email
    assert profile['username'] == user_name
    assert profile['last_name'] == user_name[5:]
    assert profile['first_name'] == user_name[:5]

    # Find for this user by email
    find_user_resp = client.get('/api/v2/admin/user/?email={}'.format(email))
    assert find_user_resp.status_code == 200
    assert find_user_resp.data['count'] == 1
    assert find_user_resp.data['results'][0]['id'] == profile['id']

    # Set administration rights on the institution
    mod_user_resp = client.patch('/api/v2/admin/user/{}/'.format(profile['id']),
                                 data={'inst_admin': True}, type='json')
    assert mod_user_resp.status_code == 200

    # Get user data
    user_data_resp = client.get(
        '/api/v2/admin/user/{}/'.format(user_create_resp.data['id'])
    )
    assert user_data_resp.status_code == 200
    assert len(user_data_resp.data['roles']) == 1
    assert "ADMIN" in user_data_resp.data['roles']

    # Remove the user
    user_del_resp = client.delete(
        '/api/v2/admin/user/{}/'.format(user_create_resp.data['id'])
    )
    assert user_del_resp.status_code == 204

    # Ensure that this user does not exist
    find2_user_resp = client.get('/api/v2/admin/user/?email={}'.format(email))
    assert find2_user_resp.status_code == 200
    assert find2_user_resp.data['count'] == 0


@pytest.mark.django_db
def test_api_admin_user_mix(rest_api_client, user_global_admin, institution_test_case):
    """
        Test the transformation of users from institution to global and opposite
    """
    # Set global admin user.
    client = auth_utils.client_with_user_obj(user_global_admin)

    # Create a new user without institution
    user_name = get_random_string(10)
    password = get_random_string(10)
    email = '{}@tesla-ce.eu'.format(user_name)
    user_data = {
        'username': user_name,
        'uid': user_name,
        'email': email,
        'first_name': user_name[:5],
        'last_name': user_name[5:],
        'login_allowed': True,
        'is_active': True,
        'is_staff': False,
        'password': password,
        'password2': password
    }
    user_create_resp = client.post('/api/v2/admin/user/', data=user_data, type='json')
    assert user_create_resp.status_code == 201
    assert user_create_resp.data['institution'] is None

    # Assign the user to an institution
    user_mod_resp = client.patch(
        '/api/v2/admin/user/{}/'.format(user_create_resp.data['id']),
        data={
            'institution_id': institution_test_case['institution'].id,
            'uid': email
        },
        type='json'
    )
    assert user_mod_resp.status_code == 200
    assert user_mod_resp.data['institution'] is not None
    assert user_mod_resp.data['institution']['id'] == institution_test_case['institution'].id
    assert user_mod_resp.data['email'] == email
    assert user_mod_resp.data['first_name'] == user_name[:5]
    assert user_mod_resp.data['last_name'] == user_name[5:]

    # Create a new institution
    new_inst_resp = client.post('/api/v2/admin/institution/', data={
        'name': "PyTest Test institution",
        'acronym': get_random_string(10)
    }, type='json')
    assert new_inst_resp.status_code == 201

    # Assign the user to an institution
    user_mod2_resp = client.patch(
        '/api/v2/admin/user/{}/'.format(user_create_resp.data['id']),
        data={'institution_id': new_inst_resp.data['id']},
        type='json'
    )
    assert user_mod2_resp.status_code == 200
    assert user_mod2_resp.data['institution'] is not None
    assert user_mod2_resp.data['institution']['id'] == new_inst_resp.data['id']
    assert user_mod2_resp.data['email'] == email
    assert user_mod2_resp.data['first_name'] == user_name[:5]
    assert user_mod2_resp.data['last_name'] == user_name[5:]

    # Remove the institution from user
    user_mod3_resp = client.patch(
        '/api/v2/admin/user/{}/'.format(user_create_resp.data['id']),
        data={'institution_id': -1},
        type='json'
    )
    assert user_mod3_resp.status_code == 200
    assert user_mod3_resp.data['institution'] is None
    assert user_mod3_resp.data['email'] == email
    assert user_mod3_resp.data['first_name'] == user_name[:5]
    assert user_mod3_resp.data['last_name'] == user_name[5:]

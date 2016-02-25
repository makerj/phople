from django.conf import settings
from django.test import TestCase, Client
from rest_framework import status

from apiserver.models import User, DatePost, Couple


def res(fileanme):
    import os
    return os.path.join(settings.BASE_DIR, 'testres', fileanme)


def init_password():
    for user in User.objects.all():
        user.set_password('1234')
        user.save()


FORM_TYPE = 'application/x-www-form-urlencoded'


class AuthTestCase(TestCase):
    fixtures = ['test_auth.json']

    @classmethod
    def setUpTestData(cls):
        init_password()

    def setUp(self):
        # prepare logged user for convenience
        self.c = Client(enforce_csrf_checks=True)
        self.assertEqual(self.c.post('/login', {'username': 'makerj', 'password': '1234'}).status_code, 200)

    def test_check_exists_user(self):
        # not exists case
        c = Client(enforce_csrf_checks=True)
        r = c.get('/user/makerj/exists')
        self.assertEqual(r.status_code, status.HTTP_306_RESERVED)

        # exists case
        c = Client(enforce_csrf_checks=True)
        r = c.get('/user/thisusernotexists/exists')
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_signup(self):
        # fine case
        c = Client(enforce_csrf_checks=True)
        r = c.post('/signup', {'username': 'tester', 'password': '1234'})
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

        # bad Request Case (mandatory field missing)
        c = Client(enforce_csrf_checks=True)
        r = c.post('/signup', {'username': 'tester'})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

        # bad Request Case (logged user tried signup)
        c = Client(enforce_csrf_checks=True)
        r = c.post('/login', {'username': 'makerj', 'password': '1234'})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        r = c.post('/signup', {'username': 'tester'})
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

        # conflict case
        c = Client(enforce_csrf_checks=True)
        r = c.post('/signup', {'username': 'tester', 'password': '1234'})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signdown(self):
        # fine case
        c = Client(enforce_csrf_checks=True)
        r = c.post('/login', {'username': 'signdownuser', 'password': '1234'})
        r = c.delete('/signdown')
        self.assertEqual(r.status_code, status.HTTP_200_OK)

        # not logged in
        c = Client(enforce_csrf_checks=True)
        r = c.delete('/signdown')
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_logging(self):
        # login properly
        c = Client(enforce_csrf_checks=True)
        r = c.post('/login', {'username': 'makerj', 'password': '1234'})
        self.assertEqual(r.status_code, status.HTTP_200_OK)

        # ignore already logged user
        r = c.post('/login', {'username': 'makerj', 'password': '1234'})
        self.assertEqual('makerj', r.data['username'])  # response must contains return user information. even this case
        self.assertEqual(r.status_code, status.HTTP_200_OK)

        # logout properly
        r = c.delete('/logout')
        self.assertEqual(r.status_code, status.HTTP_200_OK)

        # Request logout without session
        r = c.delete('/logout')
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

        # invalid credential
        r = c.post('/login', {'username': 'notexisting', 'password': '1234'})
        self.assertNotEqual(r.status_code, status.HTTP_200_OK)

    # def test_userdetail(self):  # Causes too many S3 resource. avoid frequent testing
    #     c = Client(enforce_csrf_checks=True)
    #     # login first
    #     r = c.post('/login', {'username': 'makerj', 'password': '1234'})
    #     self.assertEqual(r.status_code, status.HTTP_200_OK)
    #     # upload fields
    #     with open(res('profile.jpg'), 'rb') as profile, open(res('profile-background.png'), 'rb') as profile_background:
    #         r = c.post('/me', dict(birth_date=date.today(), profile_message='hello',
    #                                profile_image=profile, profile_background_image=profile_background))
    #         self.assertEqual(r.status_code, status.HTTP_202_ACCEPTED)
    #     c = Client(enforce_csrf_checks=True)
    #     r = c.post('/login', {'username': 'makerj', 'password': '1234'})
    #     self.assertTrue(all(['profile_image' in str(r.data), 's3.amazonaws.com' in str(r.data)]))

    def test_couple(self):
        import datetime
        # create
        c = self.c
        r = c.post('/couple',
                   dict(title='makers', description='we are makers', coupling_begin=datetime.date(2015, 3, 26)))
        couple_id = r.data.get('id')

        # retrieve
        r = c.get('/couple')
        self.assertEqual(r.data.get('count'), 1)
        self.assertEqual(r.data.get('results')[0].get('title'), 'makers')

        # update
        r = c.put('/couple/{}'.format(couple_id), 'title=new title&description=new desc!', FORM_TYPE)
        self.assertEqual('new title', r.data.get('title'))
        self.assertEqual('new desc!', r.data.get('description'))

        # partial_update
        r = c.patch('/couple/{}'.format(couple_id), 'title=another title', FORM_TYPE)
        self.assertEqual('another title', r.data.get('title'))
        self.assertEqual('new desc!', r.data.get('description'))

        # associate
        self.c.post('/me', {'couple': couple_id})
        self.assertEqual(couple_id, self.c.get('/me').data.get('couple'))
        self.assertNotEqual(self.c.get('/couple/{}'.format(couple_id)).data.get('users'), None)

        # destroy
        r = c.delete('/couple/1')
        self.assertEqual(r.status_code, 204)
        r = c.get('/couple')
        self.assertEqual(0, len(r.data.get('results')))


class DatePostTestCase(TestCase):
    fixtures = ['test_datepost.json']

    @classmethod
    def setUpTestData(cls):
        init_password()

    def setUp(self):
        # prepare logged user for convenience
        self.c = Client(enforce_csrf_checks=True)
        self.assertEqual(self.c.post('/login', {'username': 'makerj', 'password': '1234'}).status_code, 200)

    def test_create(self):
        # create
        c = self.c
        r = c.post('/datepost', {'title': 'first datepost', 'message': 'msg', 'tags': [1, 2, 3]})
        datepost_id = r.data.get('id')

        # retrieve
        r = c.get('/datepost')
        self.assertEqual(r.data.get('count'), 1)
        self.assertEqual(r.data.get('results')[0].get('title'), 'first datepost')

        # update
        r = c.put('/datepost/{}'.format(datepost_id), 'title=new title&message=new msg!', FORM_TYPE)
        self.assertEqual('new title', r.data.get('title'))
        self.assertEqual('new msg!', r.data.get('message'))

        # partial_update
        r = c.patch('/datepost/{}'.format(datepost_id), 'title=another title', FORM_TYPE)
        self.assertEqual('another title', r.data.get('title'))
        self.assertEqual('new msg!', r.data.get('message'))

        # destroy
        r = c.delete('/datepost/{}'.format(datepost_id))
        self.assertEqual(r.status_code, 204)
        r = c.get('/datepost')
        self.assertEqual(0, len(r.data.get('results')))

import base64
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from .models import *
from core.models import *
from posts.models import PostModel
from follow.models import FollowerModel, FollowRequestModel
from comments_likes.models import CommentModel, LikeModel
import os
from django.conf import settings
from django.http import FileResponse

class FollowRequestsObjectEndTest(APITestCase):
    def setUp(self):
        self.author_data = {
            'username': 'ana',
            'password': '12345678',
            'isVerified': True,
            'id': 'http://testserver/api/authors/ana',
            'host': 'http://testserver/api/',
            'displayName': 'ana',
            'github': '',
            'page': '',
        }

        self.reader_data = {
            'username': 'bob',
            'password': '12345678',
            'isVerified': True,
            'id': 'http://testserver/api/authors/bob',
            'host': 'http://testserver/api/',
            'displayName': 'bob',
            'github': '',
            'page': '',
        }

        self.author = AuthorModel.objects.create(**self.author_data)
        self.reader = AuthorModel.objects.create(**self.reader_data)
        self.url = reverse('socialapp:api-getFollow-object_pk', kwargs={'object_pk': 'ana'})
        self.url2 = reverse('socialapp:api-getFollow-object_pk', kwargs={'object_pk': 'cec'})

        self.follow_request_data = {
            'summary': "bob wants to follow ana",
            'actor': self.reader,
            'object': self.author
        }

        self.follow_request = FollowRequestModel.objects.create(**self.follow_request_data)

    def test_no_cred(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.get(self.url2)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_followReq(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.get(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data_displayed'][0]['profileImage'], '')
        self.assertEqual(response.data['data_displayed'][0]['id'], 'http://testserver/api/authors/bob')

    def test_get_followReq_404(self):
        credentials = base64.b64encode(b'cec:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.get(self.url2, **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_all_follower(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.get(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data_displayed'][0]['profileImage'], '')
        self.assertEqual(response.data['data_displayed'][0]['id'], 'http://testserver/api/authors/bob')

    def test_get_all_follower_404(self):
        credentials = base64.b64encode(b'cec:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.get(self.url2, **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class FollowRequestObjectEndTest(APITestCase):
    def setUp(self):
        self.author_data = {
            'username': 'ana',
            'password': '12345678',
            'isVerified': True,
            'id': 'http://testserver/api/authors/ana',
            'host': 'http://testserver/api/',
            'displayName': 'ana',
            'github': '',
            'page': '',
        }

        self.reader_data = {
            'username': 'bob',
            'password': '12345678',
            'isVerified': True,
            'id': 'http://testserver/api/authors/bob',
            'host': 'http://testserver/api/',
            'displayName': 'bob',
            'github': '',
            'page': '',
        }

        self.author = AuthorModel.objects.create(**self.author_data)
        self.reader = AuthorModel.objects.create(**self.reader_data)
        self.url = reverse('socialapp:api-handleFollow-object_pk-actor_id', kwargs={'object_pk': 'ana', 'actor_id': 'http://testserver/api/authors/bob'})
        self.url2 = reverse('socialapp:api-handleFollow-object_pk-actor_id', kwargs={'object_pk': 'ana', 'actor_id': 'http://testserver/api/authors/cec'})

    def test_no_cred(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.get(self.url2)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_followReq_to_accept_and_database(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        follow_request_data = {
            'summary': "bob wants to follow ana",
            'actor': self.reader,
            'object': self.author
        }

        FollowRequestModel.objects.create(**follow_request_data)
        response = self.client.post(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, None)
        self.assertEqual(len(FollowRequestModel.objects.all()), 0)

    def test_post_followReq_to_reject_and_database(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        follow_request_data = {
            'summary': "bob wants to follow ana",
            'actor': self.reader,
            'object': self.author
        }

        FollowRequestModel.objects.create(**follow_request_data)

        data = {'actor': self.reader, 'object': self.author}
        FollowerModel.objects.create(**data)

        response = self.client.delete(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(FollowRequestModel.objects.all()), 0)
        self.assertEqual(len(FollowerModel.objects.all()), 0)

    def test_post_followReq_404(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }

        response = self.client.post(self.url2, **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_to_reject_followReq_404(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        follow_request_data = {
            'summary': "bob wants to follow ana",
            'actor': self.reader,
            'object': self.author
        }
        FollowRequestModel.objects.create(**follow_request_data)
        response = self.client.delete(self.url2, **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        followRequest_models = FollowRequestModel.objects.all()
        self.assertEqual(len(followRequest_models), 1)

class FollowRequestActorEndTest(APITestCase):
    def setUp(self):
        self.author_data = {
            'username': 'ana',
            'password': '12345678',
            'isVerified': True,
            'id': 'http://testserver/api/authors/ana',
            'host': 'http://testserver/api/',
            'displayName': 'ana',
            'github': '',
            'page': '',
        }

        self.reader_data = {
            'username': 'bob',
            'password': '12345678',
            'isVerified': True,
            'id': 'http://testserver/api/authors/bob',
            'host': 'http://testserver/api/',
            'displayName': 'bob',
            'github': '',
            'page': '',
        }

        self.author = AuthorModel.objects.create(**self.author_data)
        self.reader = AuthorModel.objects.create(**self.reader_data)
        self.url = reverse('socialapp:api-handleFollow-actor_pk-object_id', kwargs={'actor_pk': 'bob', 'object_id': 'http://testserver/api/authors/ana'})

    def test_no_cred(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_follow_an_author_and_database(self):
        credentials = base64.b64encode(b'bob:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.post(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        follower_model = FollowerModel.objects.get(mid = 1)
        followreq_model = FollowRequestModel.objects.get(mid = 1)
        self.assertEqual(follower_model.actor, self.reader)
        self.assertEqual(follower_model.object, self.author)
        self.assertEqual(followreq_model.actor, self.reader)
        self.assertEqual(followreq_model.object, self.author)
        self.assertEqual(followreq_model.summary, 'User bob wants to follow user ana.')
        response = self.client.post(self.url, **headers)

    def test_follow_an_author_repeat_409(self):
        credentials = base64.b64encode(b'bob:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.post(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        follower_models = FollowerModel.objects.all()
        followreq_models = FollowRequestModel.objects.all()
        self.assertEqual(len(follower_models), 1)
        self.assertEqual(len(followreq_models), 1)

    def test_unfollow_an_author_and_database(self):
        credentials = base64.b64encode(b'bob:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        self.client.post(self.url, **headers)
        response = self.client.delete(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(FollowerModel.objects.all()), 0)
        self.assertEqual(len(FollowRequestModel.objects.all()), 0)

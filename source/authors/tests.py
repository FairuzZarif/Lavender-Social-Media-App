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

class AuthorsViewTest(APITestCase):

    def setUp(self):
        self.author_data = {
            'username': '123',
            'password': '12345678',
            'isVerified': True,
            'id': 'http://testserver/api/authors/123',
            'host': 'http://testserver/api/',
            'displayName': 'Test Author',
            'github': '',
            'page': '',
        }
        self.author = AuthorModel.objects.create(**self.author_data)
        self.url = reverse('socialapp:api-authors')

    def test_no_author(self):
        credentials = base64.b64encode(b'321:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.get(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_valid_credentials_get(self):
        credentials = base64.b64encode(b'123:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.get(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('authors', response.data)
        self.assertEqual(len(response.data['authors']), 1)
        self.assertEqual(response.data['authors'][0]['displayName'], 'Test Author')
        self.assertEqual(response.data['authors'][0]['id'], 'http://testserver/api/authors/123')
        self.assertEqual(response.data['authors'][0]['host'], 'http://testserver/api/')
        self.assertEqual(response.data['authors'][0]['github'], '')
        self.assertEqual(response.data['authors'][0]['profileImage'], '')
        self.assertEqual(response.data['authors'][0]['page'], '')

    def test_post_author_login_and_database(self):
        data = {
            "username": "abc",
            "password": "123456789",
        }
        response = self.client.post(self.url, data)
        expected_data = {
            'type': 'author',
            'id': 'http://testserver/api/authors/abc',
            'host': 'http://testserver/api/',
            'displayName': '',
            'github': '',
            'profileImage': '',
            'page': 'http://testserver/authors/abc'
        }
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, expected_data)
        self.assertTrue(AuthorModel.objects.filter(username='abc').exists())
        author_model = AuthorModel.objects.get(username='abc')
        self.assertEqual(author_model.username, 'abc')
        self.assertEqual(author_model.password, '123456789')
        self.assertEqual(author_model.isVerified, False)
        self.assertEqual(author_model.type, 'author')
        self.assertEqual(author_model.id, 'http://testserver/api/authors/abc')
        self.assertEqual(author_model.host, 'http://testserver/api/')
        self.assertEqual(author_model.displayName, '')
        self.assertEqual(author_model.github, '')
        self.assertEqual(author_model.profileImage, '')
        self.assertEqual(author_model.page, 'http://testserver/authors/abc')
        

    def test_post_author_conflict(self):
        data = {
            'username': '123',
            'password': '12345678',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_post_author_invalid(self):
        data = {
            'username': '',
            'password': '6',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class AuthorViewTest(APITestCase):

    def setUp(self):
        self.author_data = {
            'username': '123',
            'password': '12345678',
            'isVerified': True,
            'id': 'http://testserver/api/authors/123',
            'host': 'http://testserver/api/',
            'displayName': 'Test Author',
            'github': '',
            'page': '',
        }
        self.author_data_2 = {
            'username': '555',
            'password': '12345678',
            'isVerified': True,
            'id': 'http://testserver/api/authors/555',
            'host': 'http://testserver/api/',
            'displayName': 'Test Author2',
            'github': '',
            'page': '',
        }
        self.author = AuthorModel.objects.create(**self.author_data)
        self.url = reverse('socialapp:api-author-author_pk', kwargs = {'author_pk': '123'})
        self.url1 = reverse('socialapp:api-author-author_id', kwargs = {'author_id': 'http://testserver/api/authors/123'})
        self.url2 = reverse('socialapp:api-author-author_pk', kwargs = {'author_pk': '555'})

    def test_no_cred(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.get(self.url2)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_author_pk_success(self):
        credentials = base64.b64encode(b'123:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.get(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("displayName", response.data)
        self.assertEqual(response.data["displayName"], 'Test Author')
        self.assertEqual(response.data['id'], 'http://testserver/api/authors/123')
        self.assertEqual(response.data['host'], 'http://testserver/api/')
        self.assertEqual(response.data['github'], '')
        self.assertEqual(response.data['profileImage'], '')
        self.assertEqual(response.data['page'], '')

    def test_get_author_id_success(self):
        credentials = base64.b64encode(b'123:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.get(self.url1, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("displayName", response.data)
        self.assertEqual(response.data["displayName"], 'Test Author')
        self.assertEqual(response.data['id'], 'http://testserver/api/authors/123')
        self.assertEqual(response.data['host'], 'http://testserver/api/')
        self.assertEqual(response.data['github'], '')
        self.assertEqual(response.data['profileImage'], '')
        self.assertEqual(response.data['page'], '')

    def test_verify_author(self):
        credentials = base64.b64encode(b'123:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        data = {
                "username": "123",
                "password": "12345678"
                }
        response = self.client.post(self.url, data, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["displayName"], 'Test Author')
        self.assertEqual(response.data['id'], 'http://testserver/api/authors/123')
        self.assertEqual(response.data['host'], 'http://testserver/api/')
        self.assertEqual(response.data['github'], '')
        self.assertEqual(response.data['profileImage'], '')
        self.assertEqual(response.data['page'], '')

    def test_update_author_bad_request(self):
        credentials = base64.b64encode(b'123:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        update_data = {
            "username": "123",
            "password": "",
        }
        response = self.client.put(self.url, update_data, **headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_author_badRequest_and_forbidden(self):
        credentials = base64.b64encode(b'123:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        update_data = {
            'username':'',
            'password':'password123',
            'id':'http://testserver/api/authors/otheruser',
            'host':'http://testserver/api/',
            'displayName':'Other Author',
            'github':'https://github.com/otherauthor',
            'profile_image':'http://testserver/images/otherauthor.jpg',
            'page':'http://testserver/api/authors/otheruser'
        }
        response = self.client.put(self.url, update_data, **headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.post(self.url, update_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class StreamViewTest(APITestCase):
    def setUp(self):
        self.author_data = {
                    'username': 'ana',
                    'password': '12345678',
                    'id': 'http://testserver/api/authors/ana',
                    'host': 'http://testserver/api/',
                    'displayName': 'ana',
                    'github': '',
                    'page': '',
                }
        
        self.author_2_data = {
                    'username': 'bob',
                    'password': '12345678',
                    'id': 'http://testserver/api/authors/bob',
                    'host': 'http://testserver/api/',
                    'displayName': 'bob',
                    'github': '',
                    'page': '',
                }

        self.meta_data = {
            'title': 'This is a title',
            'id': '',
            'description': 'This is a description.',
            'contentType': 'text/plain',
            'content': 'This is a content',
            'author': 'http://testserver/api/authors/ana',
            'visibility' : ''
        }

        self.public_data = {**self.meta_data, 'id':'http://testserver/api/authors/ana/posts/1', 'visibility': "PUBLIC"}
        self.public_data_2 = {**self.meta_data, 'id':'http://testserver/api/authors/ana/posts/2', 'visibility': "PUBLIC"}
        self.friend_data = {**self.meta_data, 'id':'http://testserver/api/authors/ana/posts/3', 'visibility': "FRIENDS"}
        self.unlisted_data = {**self.meta_data, 'id':'http://testserver/api/authors/ana/posts/4', 'visibility': "UNLISTED"}

        self.author = AuthorModel.objects.create(**self.author_data)
        self.author2 = AuthorModel.objects.create(**self.author_2_data)
        self.url = reverse('socialapp:api-stream-author_id', kwargs={'author_id': 'http://testserver/api/authors/ana'})
        self.url2 = reverse('socialapp:api-stream-author_id', kwargs={'author_id': 'http://testserver/api/authors/bob'})
        self.post_url = reverse('socialapp:api-posts-author_pk', kwargs={'author_pk': 'ana'})

    def test_no_cred(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.get(self.url2)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_empty_stream(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.get(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_get_2_public_post_stream(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        self.client.post(self.post_url, self.public_data, **headers)
        self.client.post(self.post_url, self.public_data_2, **headers)
        response = self.client.get(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['id'], 'http://testserver/api/authors/ana/posts/2')
        self.assertEqual(response.data[0]['visibility'], 'PUBLIC')
        self.assertEqual(response.data[1]['id'], 'http://testserver/api/authors/ana/posts/1')
        self.assertEqual(response.data[1]['visibility'], 'PUBLIC')

    def test_self_friend_and_unlisted_post_stream(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        self.client.post(self.post_url, self.friend_data, **headers)
        self.client.post(self.post_url, self.unlisted_data, **headers)
        response = self.client.get(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['id'], 'http://testserver/api/authors/ana/posts/2')
        self.assertEqual(response.data[0]['visibility'], 'UNLISTED')
        self.assertEqual(response.data[1]['id'], 'http://testserver/api/authors/ana/posts/1')
        self.assertEqual(response.data[1]['visibility'], 'FRIENDS')

    def test_normal_data(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        self.client.post(self.post_url, self.public_data, **headers)
        self.client.post(self.post_url, self.friend_data, **headers)
        credentials = base64.b64encode(b'bob:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.get(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['id'], 'http://testserver/api/authors/ana/posts/2')
        self.assertEqual(response.data[0]['visibility'], 'FRIENDS')
        self.assertEqual(response.data[1]['id'], 'http://testserver/api/authors/ana/posts/1')
        self.assertEqual(response.data[1]['visibility'], 'PUBLIC')
        response = self.client.get(self.url2, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], 'http://testserver/api/authors/ana/posts/1')
        self.assertEqual(response.data[0]['visibility'], 'PUBLIC')

class StreamLengthViewTest(APITestCase):
    def setUp(self):
        self.author_data = {
                        'username': 'ana',
                        'password': '12345678',
                        'id': 'http://testserver/api/authors/ana',
                        'host': 'http://testserver/api/',
                        'displayName': 'ana',
                        'github': '',
                        'page': '',
                    }
        self.author = AuthorModel.objects.create(**self.author_data)

        self.meta_data = {
            'title': 'This is a title',
            'id': '',
            'description': 'This is a description.',
            'contentType': 'text/plain',
            'content': 'This is a content',
            'author': self.author,
            'visibility' : ''
        }

        self.public_data = {**self.meta_data, 'id':'http://testserver/api/authors/ana/posts/1', 'visibility': "PUBLIC"}
        self.public_data2 = {**self.meta_data, 'id':'http://testserver/api/authors/ana/posts/2', 'visibility': "PUBLIC"}

        self.url = reverse('socialapp:api-streamLength-author_id', kwargs={'author_id': 'http://testserver/api/authors/ana'})

    def test_get_stream_length_0(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.get(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['stream_length'], 0)

    def test_get_stream_length_2(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        self.post = PostModel.objects.create(**self.public_data)
        self.post2 = PostModel.objects.create(**self.public_data2)
        response = self.client.get(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['stream_length'], 2)

class StreamPostViewTest(APITestCase):
    def setUp(self):
        self.author_data = {
                        'username': 'ana',
                        'password': '12345678',
                        'id': 'http://testserver/api/authors/ana',
                        'host': 'http://testserver/api/',
                        'displayName': 'ana',
                        'github': '',
                        'page': '',
                    }
        self.author = AuthorModel.objects.create(**self.author_data)

        self.meta_data = {
            'title': 'This is a title',
            'id': '',
            'description': 'This is a description.',
            'contentType': 'text/plain',
            'content': 'This is a content',
            'author': self.author,
            'visibility' : ''
        }

        self.public_data = {**self.meta_data, 'id':'http://testserver/api/authors/ana/posts/1', 'visibility': "PUBLIC"}
        self.public_data2 = {**self.meta_data, 'id':'http://testserver/api/authors/ana/posts/2', 'visibility': "PUBLIC"}
        self.post = PostModel.objects.create(**self.public_data)
        self.post2 = PostModel.objects.create(**self.public_data2)

        self.url = reverse('socialapp:api-streamPost-author_id-seq_num', kwargs={'author_id': 'http://testserver/api/authors/ana', 'seq_num': 1})
        self.url2 = reverse('socialapp:api-streamPost-author_id-seq_num', kwargs={'author_id': 'http://testserver/api/authors/ana', 'seq_num': 2})
        self.url3 = reverse('socialapp:api-streamPost-author_id-seq_num', kwargs={'author_id': 'http://testserver/api/authors/ana', 'seq_num': 3})
        self.url4 = reverse('socialapp:api-streamPost-author_id-seq_num', kwargs={'author_id': 'http://testserver/api/authors/ana', 'seq_num': 0})
        self.url5 = reverse('socialapp:api-streamPost-author_id-seq_num', kwargs={'author_id': 'http://testserver/api/authors/ana', 'seq_num': '?'})

    def test_no_cred(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.get(self.url2)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.get(self.url3)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_first_post_in_stream(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.get(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], 'http://testserver/api/authors/ana/posts/2')

    def test_get_second_post_in_stream(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.get(self.url2, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], 'http://testserver/api/authors/ana/posts/1')

    def test_get_no_post_in_stream(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.get(self.url3, **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_wrong_index_in_stream(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.get(self.url4, **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_bad_request_in_stream(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.get(self.url5, **headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

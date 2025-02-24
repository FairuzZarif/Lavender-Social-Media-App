import base64
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from .models import *
from authors.models import AuthorModel
from posts.models import PostModel
from follow.models import FollowerModel, FollowRequestModel
from comments_likes.models import CommentModel, LikeModel
import os
from django.conf import settings
from django.http import FileResponse

class PostsViewTest(APITestCase):

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

        self.reader_data = {
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
        self.friend_data = {**self.meta_data, 'id':'http://testserver/api/authors/ana/posts/2', 'visibility': "FRIENDS"}
        self.deleted_data = {**self.meta_data, 'id':'http://testserver/api/authors/ana/posts/3', 'visibility': "DELETED"}
        self.unlisted_data = {**self.meta_data, 'id':'http://testserver/api/authors/ana/posts/4', 'visibility': "UNLISTED"}

        self.author = AuthorModel.objects.create(**self.author_data)
        self.reader = AuthorModel.objects.create(**self.reader_data)
        self.url = reverse('socialapp:api-posts-author_pk', kwargs={'author_pk': 'ana'})

    def test_no_cred(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_post_post_and_database(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.post(self.url, self.public_data, **headers)
        public_post_model = PostModel.objects.get(mid = 1)
        self.assertEqual(public_post_model.id, 'http://testserver/api/authors/ana/posts/1')
        self.assertEqual(public_post_model.visibility, 'PUBLIC')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_author_view_get_post_and_database(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        self.client.post(self.url, self.public_data, **headers)
        self.client.post(self.url, self.friend_data, **headers)
        self.client.post(self.url, self.deleted_data, **headers)
        self.client.post(self.url, self.unlisted_data, **headers)
        post_models = PostModel.objects.all()
        self.assertEqual(len(post_models), 4)
        public_post_model = PostModel.objects.get(mid = 1)
        self.assertEqual(public_post_model.id, 'http://testserver/api/authors/ana/posts/1')
        self.assertEqual(public_post_model.visibility, 'PUBLIC')
        public_post_model = PostModel.objects.get(mid = 2)
        self.assertEqual(public_post_model.id, 'http://testserver/api/authors/ana/posts/2')
        self.assertEqual(public_post_model.visibility, 'FRIENDS')
        public_post_model = PostModel.objects.get(mid = 3)
        self.assertEqual(public_post_model.id, 'http://testserver/api/authors/ana/posts/3')
        self.assertEqual(public_post_model.visibility, 'DELETED')
        public_post_model = PostModel.objects.get(mid = 4)
        self.assertEqual(public_post_model.id, 'http://testserver/api/authors/ana/posts/4')
        self.assertEqual(public_post_model.visibility, 'UNLISTED')
        response = self.client.get(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data[1]['id'], 'http://testserver/api/authors/ana/posts/2')
        self.assertEqual(response.data[1]['title'], 'This is a title')
        self.assertEqual(response.data[1]['description'], 'This is a description.')
        self.assertEqual(response.data[1]['contentType'], 'text/plain')
        self.assertEqual(response.data[1]['author'], 'http://testserver/api/authors/ana')
        self.assertEqual(response.data[1]['visibility'], 'FRIENDS')
        self.assertEqual(response.data[0]['visibility'], 'UNLISTED')

    def test_stranger_view_get_post(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        self.client.post(self.url, self.public_data, **headers)
        self.client.post(self.url, self.friend_data, **headers)
        self.client.post(self.url, self.deleted_data, **headers)
        self.client.post(self.url, self.unlisted_data, **headers)

        credentials = base64.b64encode(b'bob:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.get(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['id'], 'http://testserver/api/authors/ana/posts/1')
        self.assertEqual(response.data[0]['title'], 'This is a title')
        self.assertEqual(response.data[0]['description'], 'This is a description.')
        self.assertEqual(response.data[0]['contentType'], 'text/plain')
        self.assertEqual(response.data[0]['author'], 'http://testserver/api/authors/ana')
        self.assertEqual(len(response.data), 1)
    
    def test_follower_view_get_post(self):
        data = {'actor': self.reader, 'object': self.author}
        follow = FollowerModel.objects.create(**data)
        
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        self.client.post(self.url, self.public_data, **headers)
        self.client.post(self.url, self.friend_data, **headers)
        self.client.post(self.url, self.deleted_data, **headers)
        self.client.post(self.url, self.unlisted_data, **headers)

        credentials = base64.b64encode(b'bob:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.get(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['id'], 'http://testserver/api/authors/ana/posts/4')
        self.assertEqual(response.data[0]['title'], 'This is a title')
        self.assertEqual(response.data[0]['description'], 'This is a description.')
        self.assertEqual(response.data[0]['contentType'], 'text/plain')
        self.assertEqual(response.data[0]['author'], 'http://testserver/api/authors/ana')
        self.assertEqual(response.data[0]['visibility'], 'UNLISTED')

    def test_friend_view_get_post(self):
        data = {'actor': self.reader, 'object': self.author}
        follow = FollowerModel.objects.create(**data)
        data = {'actor': self.author, 'object': self.reader}
        follow = FollowerModel.objects.create(**data)

        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        self.client.post(self.url, self.public_data, **headers)
        self.client.post(self.url, self.friend_data, **headers)
        self.client.post(self.url, self.deleted_data, **headers)
        self.client.post(self.url, self.unlisted_data, **headers)

        credentials = base64.b64encode(b'bob:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.get(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data[1]['id'], 'http://testserver/api/authors/ana/posts/2')
        self.assertEqual(response.data[1]['title'], 'This is a title')
        self.assertEqual(response.data[1]['description'], 'This is a description.')
        self.assertEqual(response.data[1]['contentType'], 'text/plain')
        self.assertEqual(response.data[1]['author'], 'http://testserver/api/authors/ana')
        self.assertEqual(response.data[1]['visibility'], 'FRIENDS')

class PostViewTest(APITestCase):
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

        self.changed_data = {
            'title': 'This is a changed title',
            'description': 'This is a changed description.',
            'contentType': 'text/plain',
            'content': 'This is a content',
            'visibility' : 'PUBLIC'
        }

        self.deleted_data = {
            'title': 'This is a title',
            'description': 'This is a description.',
            'contentType': 'text/plain',
            'content': 'This is a content',
            'visibility' : 'DELETED'
        }

        self.public_data = {**self.meta_data, 'id':'http://testserver/api/authors/ana/posts/1', 'visibility': "PUBLIC"}

        self.author = AuthorModel.objects.create(**self.author_data)
        self.author2 = AuthorModel.objects.create(**self.author_2_data)
        self.url = reverse('socialapp:api-post-author_pk-post_pk', kwargs={'author_pk': 'ana', 'post_pk': '1'})
        self.url2 = reverse('socialapp:api-post-post_id', kwargs={'post_id': 'http://testserver/api/authors/ana/posts/1'})
        self.url3 = reverse('socialapp:api-posts-author_pk', kwargs={'author_pk': 'ana'})
        self.stream_url = reverse('socialapp:api-stream-author_id', kwargs={'author_id': 'http://testserver/api/authors/bob'})

    def test_no_cred(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_spec_post_pk(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        self.client.post(self.url3, self.public_data, **headers)
        response = self.client.get(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], 'http://testserver/api/authors/ana/posts/1')
        self.assertEqual(response.data['description'], 'This is a description.')
        self.assertEqual(response.data['contentType'], 'text/plain')
        self.assertEqual(response.data['visibility'], 'PUBLIC')

    def test_get_spec_post_id(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        self.client.post(self.url3, self.public_data, **headers)
        response = self.client.get(self.url2, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], 'http://testserver/api/authors/ana/posts/1')
        self.assertEqual(response.data['description'], 'This is a description.')
        self.assertEqual(response.data['contentType'], 'text/plain')
        self.assertEqual(response.data['visibility'], 'PUBLIC')

    def test_put_spec_post_pk(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        self.client.post(self.url3, self.public_data, **headers)
        response = self.client.put(self.url, self.changed_data, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], 'http://testserver/api/authors/ana/posts/1')
        self.assertEqual(response.data['description'], 'This is a changed description.')
        self.assertEqual(response.data['contentType'], 'text/plain')
        self.assertEqual(response.data['visibility'], 'PUBLIC')

    def test_stream_get_edited_post(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        self.client.post(self.url3, self.public_data, **headers)
        self.client.put(self.url, self.changed_data, **headers)

        credentials = base64.b64encode(b'bob:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.get(self.stream_url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['id'],'http://testserver/api/authors/ana/posts/1')
        self.assertEqual(response.data[0]['description'], 'This is a changed description.')

    def test_del_spec_post_pk(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        self.client.post(self.url3, self.public_data, **headers)
        response = self.client.delete(self.url, self.deleted_data, **headers)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        deleted_post = PostModel.objects.get(id = 'http://testserver/api/authors/ana/posts/1')
        self.assertEqual(deleted_post.visibility, 'DELETED')

    def test__stream_cant_get_deleted_post(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        self.client.post(self.url3, self.public_data, **headers)
        self.client.delete(self.url, self.deleted_data, **headers)

        credentials = base64.b64encode(b'bob:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.get(self.stream_url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

class PostImageViewTest(APITestCase):
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
            'title': 'This is a title for img post',
            'id': '',
            'description': 'This is a description.',
            'contentType': 'image/png;base64',
            'content': 'data:image/png;base64,iVBORw0K',
            'author': self.author,
            'visibility' : ''
        }

        self.public_data = {**self.meta_data, 'id':'http://testserver/api/authors/ana/posts/1', 'visibility': "PUBLIC"}

        self.post = PostModel.objects.create(**self.public_data)
        self.url = reverse('socialapp:api-postImage-author_pk-post_pk', kwargs={'author_pk': 'ana', 'post_pk': '1'})
        self.url2 = reverse('socialapp:api-postImage-author_pk-post_pk', kwargs={'author_pk': 'ana', 'post_pk': '2'})
        self.url3 = reverse('socialapp:api-postImage-post_id', kwargs={'post_id': 'http://testserver/api/authors/ana/posts/1'})
        self.url4 = reverse('socialapp:api-postImage-post_id', kwargs={'post_id': 'http://testserver/api/authors/ana/posts/2'})

    def test_get_invalid_img_post_pk(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.get(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_invalid_img_post_id(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.get(self.url3, **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_img_post_404(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.get(self.url2, **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.get(self.url4, **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

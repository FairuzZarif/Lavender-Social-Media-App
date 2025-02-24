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
from authors.tests import *
from follow.tests import *
from posts.tests import *
from comments_likes.tests import *

class profileImageViewTest(APITestCase):

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
        self.test_img_id = 'test_image.jpg'
        self.image_dir = os.path.join(settings.MEDIA_ROOT, 'images', 'profile_images')
        self.image_path = os.path.join(self.image_dir, self.test_img_id)
        os.makedirs(self.image_dir, exist_ok=True)

        with open(self.image_path, 'wb') as f:
            f.write(b'test image content')

        self.url = reverse('socialapp:api-profileimage-img_id', kwargs = {'img_id': 'test_image.jpg'})
        self.url2 = reverse('socialapp:api-profileimage-img_id', kwargs = {'img_id': 'no_image.jpg'})
        
    def test_get_existing_image(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response, FileResponse)

    def test_no_existing_image(self):
        response = self.client.get(self.url2)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class InboxViewTest(APITestCase):
    
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

        self.incorrect_inbox_post_data = {
            'type': 'post',
            'title': 'A post from others',
            'id': 'http://anotherserver/api/authors/bob/posts/1',
            'description': 'its a post',
            'contentType': 'text/plain',
            'content': 'the content of my remote post',
            'author': {
                'type': 'author',
                'id': 'http://anotherserver/api/authors/bob',
                'host': 'http://anotherserver/api/',
                'displayName': 'bob',
                'github': '',
                'page': '',
                'profileImage': '',
            },
            'published': '2015-03-09T13:07:04+00:00',
            'visibility': 'PUBLIC'
        }

        self.inbox_post_data = {
            'type': 'post',
            'title': 'A post from others',
            'id': 'http://anotherserver/api/authors/bob/posts/1',
            'description': 'its a post',
            'contentType': 'text/plain',
            'content': 'the content of my remote post',
            'author': {
                'type': 'author',
                'id': 'http://anotherserver/api/authors/bob',
                'host': 'http://anotherserver/api/',
                'displayName': 'bob',
                'github': '',
                'page': 'http://anotherserver/authors/bob',
                'profileImage': '',
            },
            'published': '2015-03-09T13:07:04+00:00',
            'visibility': 'PUBLIC'
        }

        self.inbox_trash_img_post_data = {
            'type': 'post',
            'title': 'A post from others',
            'id': 'http://anotherserver/api/authors/bob/posts/1',
            'description': 'its a post',
            'contentType': 'image/png;base64',
            'content': 'e/fniuacgnseucnicwfviurfbsturjenvergauchfhfgbd3chngshfhu4g',
            'author': {
                'type': 'author',
                'id': 'http://anotherserver/api/authors/bob',
                'host': 'http://anotherserver/api/',
                'displayName': 'bob',
                'github': '',
                'page': 'http://anotherserver/authors/bob',
                'profileImage': '',
            },
            'published': '2015-03-09T13:07:04+00:00',
            'visibility': 'PUBLIC'
        }

        self.inbox_fr_data = {
            'type': 'follow',
            'summary': 'bob want to follow ana',
            'actor': {
                'type': 'author',
                'id': 'http://anotherserver/api/authors/bob',
                'host': 'http://anotherserver/api/',
                'displayName': 'bob',
                'github': '',
                'page': 'http://anotherserver/authors/bob',
                'profileImage': '',
            },
            'object': {
                'type': 'author',
                'id': 'http://testserver/api/authors/ana',
                'host': 'http://testserver/api/',
                'displayName': 'ana',
                'github': '',
                'page': '',
                'profileImage': '',
            }
        }

        self.inbox_comment_data = {
            'type': 'comment',
            'comment': 'its a comment',
            'author': {
                'type': 'author',
                'id': 'http://anotherserver/api/authors/bob',
                'host': 'http://anotherserver/api/',
                'displayName': 'bob',
                'github': '',
                'page': 'http://anotherserver/authors/bob',
                'profileImage': '',
            },
            'contentType': 'text/markdown',
            'published': '2015-03-09T13:07:04+00:00',
            'id': 'http://anotherserver/api/authors/bob/commented/1',
            'post': "http://anotherserver/api/authors/bob/posts/1"
        }

        self.inbox_like_data = {
            'type': 'like',
            'author': {
                'type': 'author',
                'id': 'http://anotherserver/api/authors/bob',
                'host': 'http://anotherserver/api/',
                'displayName': 'bob',
                'github': '',
                'page': 'http://anotherserver/authors/bob',
                'profileImage': '',
            },
            'published': '2015-03-09T13:07:04+00:00',
            'id': 'http://anotherserver/api/authors/bob/liked/1',
            'object': 'http://anotherserver/api/authors/bob/posts/1'
        }

        self.share_node_data = {
            'host': 'http://anotherserver/',
            'allowIn': True,
            'inUsername': 'test',
            'inPassword': '123',
            'allowOut': True,
            'outUsername': 'test',
            'outPassword': '123'
        }

        self.author = AuthorModel.objects.create(**self.author_data)
        self.url = reverse('socialapp:api-inbox-author_pk', kwargs = {'author_pk': 'ana'})

    def test_node(self):
        credentials = base64.b64encode(b'test:123').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://anotherserver/',
            "HTTP_Authorization": f"Basic {credentials}",
            "Content-Type": "application/json"
        }
        self.node = ShareNodeModel.objects.create(**self.share_node_data)
        body = self.inbox_fr_data
        response = self.client.post(self.url, body, **headers, format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(len(FollowerModel.objects.all()),1)
        follower_model = FollowerModel.objects.all().first()
        self.assertEqual(follower_model.actor.id, 'http://anotherserver/api/authors/bob')
        self.assertEqual(follower_model.object.id, 'http://testserver/api/authors/ana')

        remote_author_model = AuthorModel.objects.get(id = 'http://anotherserver/api/authors/bob')
        self.assertEqual(remote_author_model.id, 'http://anotherserver/api/authors/bob')
        self.assertEqual(remote_author_model.displayName, 'bob')
        self.assertEqual(remote_author_model.host, 'http://anotherserver/api/')

        body = self.incorrect_inbox_post_data
        response = self.client.post(self.url, body, **headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        body = self.inbox_post_data
        response = self.client.post(self.url, body, **headers, format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(len(PostModel.objects.all()),1)
        post_model = PostModel.objects.all().first()
        self.assertEqual(post_model.type, 'post')
        self.assertEqual(post_model.id, 'http://anotherserver/api/authors/bob/posts/1')
        self.assertEqual(post_model.author.id, 'http://anotherserver/api/authors/bob')
        self.assertEqual(post_model.title, 'A post from others')
        self.assertEqual(post_model.description, 'its a post')
        self.assertEqual(post_model.content, 'the content of my remote post')
        self.assertEqual(post_model.visibility, 'PUBLIC')

        body = self.inbox_comment_data
        response = self.client.post(self.url, body, **headers, format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(len(CommentModel.objects.all()),1)
        Comment_model = CommentModel.objects.all().first()
        self.assertEqual(Comment_model.type, 'comment')
        self.assertEqual(Comment_model.id, 'http://anotherserver/api/authors/bob/commented/1')
        self.assertEqual(Comment_model.author.id, 'http://anotherserver/api/authors/bob')
        self.assertEqual(Comment_model.comment, 'its a comment')
        self.assertEqual(Comment_model.post, post_model)

        body = self.inbox_like_data
        response = self.client.post(self.url, body, **headers, format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(len(LikeModel.objects.all()),1)
        Like_model = LikeModel.objects.all().first()
        self.assertEqual(Like_model.type, 'like')
        self.assertEqual(Like_model.id, 'http://anotherserver/api/authors/bob/liked/1')
        self.assertEqual(Like_model.author.id, 'http://anotherserver/api/authors/bob')
        self.assertEqual(Like_model.post, post_model)
        self.assertEqual(Like_model.object, post_model.id)

    def test_node_wrong_cred(self):
        credentials = base64.b64encode(b'notest:321').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://anotherserver/',
            "HTTP_Authorization": f"Basic {credentials}",
            "Content-Type": "application/json"
        }
        self.node = ShareNodeModel.objects.create(**self.share_node_data)
        body = self.inbox_fr_data
        response = self.client.post(self.url, body, **headers, format='json')
        self.assertEqual(response.status_code,status.HTTP_403_FORBIDDEN)

    def test_node_checkbox(self):
        unshare_node_data = {
            'host': 'http://anotheranotherserver/',
            'allowIn': False,
            'inUsername': 'test',
            'inPassword': '123',
            'allowOut': True,
            'outUsername': 'test',
            'outPassword': '123'
        }
        self.node = ShareNodeModel.objects.create(**unshare_node_data)
        credentials = base64.b64encode(b'test:123').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/',
            "HTTP_Authorization": f"Basic {credentials}",
            "Content-Type": "application/json"
        }
        self.node = ShareNodeModel.objects.create(**self.share_node_data)
        body = self.inbox_fr_data
        response = self.client.post(self.url, body, **headers, format='json')
        self.assertEqual(response.status_code,status.HTTP_403_FORBIDDEN)
    
    def test_inbox_img_400(self):
        credentials = base64.b64encode(b'test:123').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://anotherserver/',
            "HTTP_Authorization": f"Basic {credentials}",
            "Content-Type": "application/json"
        }
        self.node = ShareNodeModel.objects.create(**self.share_node_data)

        body = {'type': 'idk'}
        response = self.client.post(self.url, body, **headers, format='json')
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)

""" Need to add following view
class FollowingViewTest(APITestCase):
    
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
        self.url = reverse('socialapp:api-following-author_pk', kwargs={'actor_pk': 'bob'})

    def test_no_cred(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_followings(self):
        data = {'actor': self.reader, 'object': self.author}
        FollowerModel.objects.create(**data)
        
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.get(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['following']), 1)
        self.assertEqual(response.data['following'][0]['actor']['id'], 'http://testserver/api/authors/bob')
        self.assertEqual(response.data['following'][0]['object']['id'], 'http://testserver/api/authors/ana')
"""

""" Need to add followers view
class FollowersViewTest(APITestCase):
    
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
        self.url = reverse('socialapp:api-follwers-author_pk', kwargs={'object_pk': 'ana'})

    def test_no_cred(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_followers(self):
        data = {'actor': self.reader, 'object': self.author}
        FollowerModel.objects.create(**data)
        
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.get(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['followers']), 1)
        self.assertEqual(response.data['followers'][0]['type'], 'author')
        self.assertEqual(response.data['followers'][0]['id'], 'http://testserver/api/authors/bob')
"""

""" Need to add follower remote view
class FollowerViewTest(APITestCase):
    
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
        self.url = reverse('socialapp:api-follower-object_pk-actor_id', kwargs={'object_pk': 'ana', 'actor_id': 'http://testserver/api/authors/bob'})
    
    def test_no_cred(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_check_follower(self):
        data = {'actor': self.reader, 'object': self.author}
        FollowerModel.objects.create(**data)
        
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.get(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_no_follower_404(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.get(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_follower_and_database(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.put(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, None)
        follower_model = FollowerModel.objects.get(mid = 1)
        self.assertEqual(follower_model.actor, self.reader)
        self.assertEqual(follower_model.object, self.author)

    def test_remove_follower(self):
        data = {'actor': self.reader, 'object': self.author}
        FollowerModel.objects.create(**data)
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.delete(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        follower_models = FollowerModel.objects.all()
        self.assertEqual(len(follower_models), 0)
"""

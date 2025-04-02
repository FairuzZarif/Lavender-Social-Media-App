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

"""
IMPORTANT: to run the test, please go to .env file and change the first line to: LOCAL_HOST=http://testserver/
"""

# Reference: Django view tests for AuthorsView, ChatGPT, OpenAI, 2024-10-20.
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


class FollowerRemoteView(APITestCase):

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
            'id': 'http://anotherserver/api/authors/bob',
            'host': 'http://anotherserver/api/',
            'displayName': 'bob',
            'github': '',
            'page': '',
        }
        self.author = AuthorModel.objects.create(**self.author_data)
        self.reader = AuthorModel.objects.create(**self.reader_data)
        self.url = reverse('socialapp:api-remote-follower-actor_pk-object_id', kwargs={'actor_pk': 'ana', 'object_id': 'http://anotherserver/api/authors/bob'})

    def test_no_cred(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_check_follower(self):
        data = {'actor': self.author, 'object': self.reader}
        FollowerModel.objects.create(**data)
        
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.get(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, None)


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
        print(response.data[1])
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

class CommentsViewTest(APITestCase):
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
        self.post = PostModel.objects.create(**self.public_data)
        self.comment_data = {
            'id': 'http://testserver/api/authors/ana/commented/1',
            'author': self.author,
            'comment': 'This is a comment',
            'contentType': 'text/plain',
            'post': self.post
        }
        self.comment = CommentModel.objects.create(**self.comment_data)
        self.url = reverse('socialapp:api-comments-author_pk-post_pk', kwargs={'author_pk': 'ana', 'post_pk': '1'})
        self.url2 = reverse('socialapp:api-comments-post_id', kwargs={'post_id': 'http://testserver/api/authors/ana/posts/1'})
        self.url3 = reverse('socialapp:api-comments-author_pk-post_pk', kwargs={'author_pk': 'ana', 'post_pk': '2'})
        self.url4 = reverse('socialapp:api-comments-post_id', kwargs={'post_id': 'http://testserver/api/authors/ana/posts/2'})

    def test_no_cred(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_comments_pk(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.get(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['type'], 'comments')
        self.assertEqual(response.data['id'], 'http://testserver/api/authors/ana/posts/1/comments')
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['src'][0]['type'], 'comment')
        self.assertEqual(response.data['src'][0]['id'], 'http://testserver/api/authors/ana/commented/1')
        self.assertEqual(response.data['src'][0]['comment'], 'This is a comment')

    def test_get_comments_id(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.get(self.url2, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['type'], 'comments')
        self.assertEqual(response.data['id'], 'http://testserver/api/authors/ana/posts/1/comments')
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['src'][0]['type'], 'comment')
        self.assertEqual(response.data['src'][0]['id'], 'http://testserver/api/authors/ana/commented/1')
        self.assertEqual(response.data['src'][0]['comment'], 'This is a comment')

    def test_get_comments_404(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.get(self.url3, **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.get(self.url4, **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CommentedViewTest(APITestCase):
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
        self.post = PostModel.objects.create(**self.public_data)
        self.comment_data = {
            'id': 'http://testserver/api/authors/ana/commented/1',
            'author': self.author,
            'comment': 'This is a comment',
            'contentType': 'text/plain',
            'post': self.post
        }
        self.url = reverse('socialapp:api-commented-author_pk', kwargs={'author_pk': 'ana'})
        self.url2 = reverse('socialapp:api-commented-author_id', kwargs={'author_id': 'http://testserver/api/authors/ana'})
        self.url3 = reverse('socialapp:api-commented-author_pk', kwargs={'author_pk': 'bob'})
        self.url4 = reverse('socialapp:api-commented-author_id', kwargs={'author_id': 'http://testserver/api/authors/bob'})

    def test_no_cred(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_commented_and_database(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        data = {
            "post": "http://testserver/api/authors/ana/posts/1",
            "contentType": "text/plain",
            "comment": "post a comment"
        }
        response = self.client.post(self.url, data, **headers)
        comment_model = CommentModel.objects.get(mid = 1)
        self.assertEqual(comment_model.type, 'comment')
        self.assertEqual(comment_model.id, 'http://testserver/api/authors/ana/commented/1')
        self.assertEqual(comment_model.author, self.author)
        self.assertEqual(comment_model.comment, 'post a comment')
        self.assertEqual(comment_model.contentType, 'text/plain')
        self.assertEqual(comment_model.post, self.post)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['type'], 'comment')
        self.assertEqual(response.data['id'], 'http://testserver/api/authors/ana/commented/1')
        self.assertEqual(response.data['comment'], 'post a comment')
        self.assertEqual(response.data['post'], 'http://testserver/api/authors/ana/posts/1')

    def test_post_commented_no_post(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        data = {
            "comment": "post a comment"
        }
        response = self.client.post(self.url, data, **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_commented_pk(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        data = {
            "post": "http://testserver/api/authors/ana/posts/1",
            "contentType": "text/plain",
            "comment": "post a comment"
        }
        data2 = {
            "post": "http://testserver/api/authors/ana/posts/1",
            "contentType": "text/plain",
            "comment": "post second comment"
        }
        self.client.post(self.url, data, **headers)
        self.client.post(self.url, data2, **headers)
        response = self.client.get(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['src'][0]['id'], 'http://testserver/api/authors/ana/commented/2')
        self.assertEqual(response.data['src'][0]['comment'], 'post second comment')
        self.assertEqual(response.data['src'][1]['id'], 'http://testserver/api/authors/ana/commented/1')
        self.assertEqual(response.data['src'][1]['comment'], 'post a comment')

    def test_get_commented_id(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        data = {
            "post": "http://testserver/api/authors/ana/posts/1",
            "contentType": "text/plain",
            "comment": "post a comment"
        }
        data2 = {
            "post": "http://testserver/api/authors/ana/posts/1",
            "contentType": "text/plain",
            "comment": "post second comment"
        }
        self.client.post(self.url, data, **headers)
        self.client.post(self.url, data2, **headers)
        response = self.client.get(self.url2, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['src'][0]['id'], 'http://testserver/api/authors/ana/commented/2')
        self.assertEqual(response.data['src'][0]['comment'], 'post second comment')
        self.assertEqual(response.data['src'][1]['id'], 'http://testserver/api/authors/ana/commented/1')
        self.assertEqual(response.data['src'][1]['comment'], 'post a comment')

    def test_get_no_commented_(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        data = {
            "post": "http://testserver/api/authors/ana/posts/1",
            "contentType": "text/plain",
            "comment": "post a comment"
        }
        self.client.post(self.url, data, **headers)
        response = self.client.get(self.url3, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['src'], [])
        response = self.client.get(self.url4, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['src'], [])


class CommentViewTest(APITestCase):
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
        self.post = PostModel.objects.create(**self.public_data)
        self.comment_data = {
            'id': 'http://testserver/api/authors/ana/commented/1',
            'author': self.author,
            'comment': 'This is a comment',
            'contentType': 'text/plain',
            'post': self.post
        }
        self.comment = CommentModel.objects.create(**self.comment_data)
        self.url = reverse('socialapp:api-comment-author_pk-post_pk-comment_id', kwargs = {'author_pk': 'ana', 'post_pk': '1', 'comment_id': 'http://testserver/api/authors/ana/commented/1'})
        self.url2 = reverse('socialapp:api-comment-comment_id', kwargs = {'author_pk': 'ana', 'comment_pk': '1'})
        self.url3 = reverse('socialapp:api-commented-comment_id', kwargs = {'comment_id': 'http://testserver/api/authors/ana/commented/1'})
        self.url4 = reverse('socialapp:api-comment-author_pk-post_pk-comment_id', kwargs = {'author_pk': 'ana', 'post_pk': '2', 'comment_id': 'http://testserver/api/authors/ana/commented/2'})
        self.url5 = reverse('socialapp:api-comment-comment_id', kwargs = {'author_pk': 'ana', 'comment_pk': '2'})
        self.url6 = reverse('socialapp:api-commented-comment_id', kwargs = {'comment_id': 'http://testserver/api/authors/ana/commented/2'})

    def test_get_comment_pk_and_cid(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.get(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['type'], 'comment')
        self.assertEqual(response.data['id'], 'http://testserver/api/authors/ana/commented/1')
        self.assertEqual(response.data['comment'], 'This is a comment')

    def test_get_comment_cid(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.get(self.url2, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['type'], 'comment')
        self.assertEqual(response.data['id'], 'http://testserver/api/authors/ana/commented/1')
        self.assertEqual(response.data['comment'], 'This is a comment')

    def test_get_comment_withed_cid(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.get(self.url3, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['type'], 'comment')
        self.assertEqual(response.data['id'], 'http://testserver/api/authors/ana/commented/1')
        self.assertEqual(response.data['comment'], 'This is a comment')

    def test_get_comment_404(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.get(self.url4, **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.get(self.url5, **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.get(self.url6, **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class LikesViewTest(APITestCase):
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
        self.post = PostModel.objects.create(**self.public_data)
        self.comment_data = {
            'id': 'http://testserver/api/authors/ana/commented/1',
            'author': self.author,
            'comment': 'This is a comment',
            'contentType': 'text/plain',
            'post': self.post
        }
        
        self.comment = CommentModel.objects.create(**self.comment_data)
        self.url = reverse('socialapp:api-postLikes-author_pk-post_pk', kwargs={'author_pk': 'ana', 'post_pk': '1'})
        self.url2 = reverse('socialapp:api-postLikes-post_id', kwargs={'post_id': 'http://testserver/api/authors/ana/posts/1'})
        self.url3 = reverse('socialapp:api-commentLikes-author_pk-post_pk-comment_id', kwargs={'author_pk': 'ana', 'post_pk': '1', 'comment_id': 'http://testserver/api/authors/ana/commented/1'})
        self.url4 = reverse('socialapp:api-authorLikes-author_pk', kwargs={'author_pk': 'ana'})
        self.url5 = reverse('socialapp:api-authorLikes-author_id', kwargs={'author_id': 'http://testserver/api/authors/ana'})
        self.url6 = reverse('socialapp:api-postLikes-author_pk-post_pk', kwargs={'author_pk': 'bob', 'post_pk': '1'})
        self.url7 = reverse('socialapp:api-postLikes-post_id', kwargs={'post_id': 'http://testserver/api/authors/ana/posts/2'})
        self.url8 = reverse('socialapp:api-commentLikes-author_pk-post_pk-comment_id', kwargs={'author_pk': 'bob', 'post_pk': '1', 'comment_id': 'http://testserver/api/authors/ana/commented/3'})

        self.post_like_data = {
            'id': 'http://testserver/api/authors/ana/liked/1',
            'author': self.author,
            'post': self.post,
            'object': 'http://testserver/api/authors/ana/posts/1' 
        }

        self.comment_like_data = {
            'id': 'http://testserver/api/authors/ana/liked/2',
            'author': self.author,
            'comment': self.comment,
            'object': 'http://testserver/api/authors/ana/commented/1' 
        }

        self.post_like = LikeModel.objects.create(**self.post_like_data)
        self.comment_like = LikeModel.objects.create(**self.comment_like_data)

    def test_no_cred(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_post_likes_by_postPk(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.get(self.url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['type'], 'likes')
        self.assertEqual(response.data['id'], 'http://testserver/api/authors/ana/posts/1/likes')
        self.assertEqual(response.data['src'][0]['type'], 'like')
        self.assertEqual(response.data['src'][0]['id'], 'http://testserver/api/authors/ana/liked/1')

    def test_get_post_likes_by_postId(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.get(self.url2, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['type'], 'likes')
        self.assertEqual(response.data['id'], 'http://testserver/api/authors/ana/posts/1/likes')
        self.assertEqual(response.data['src'][0]['type'], 'like')
        self.assertEqual(response.data['src'][0]['id'], 'http://testserver/api/authors/ana/liked/1')

    def test_get_comment_likes_by_commentPk(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.get(self.url3, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['type'], 'likes')
        self.assertEqual(response.data['id'], 'http://testserver/api/authors/ana/commented/1/likes')
        self.assertEqual(response.data['src'][0]['type'], 'like')
        self.assertEqual(response.data['src'][0]['id'], 'http://testserver/api/authors/ana/liked/2')

    def test_get_author_likes_by_authorPk(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.get(self.url4, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['type'], 'likes')
        self.assertEqual(response.data['id'], 'http://testserver/api/authors/ana/likes')
        self.assertEqual(len(response.data['src']), 2)
        self.assertEqual(response.data['src'][0]['id'], 'http://testserver/api/authors/ana/liked/2')
        self.assertEqual(response.data['src'][1]['id'], 'http://testserver/api/authors/ana/liked/1')

    def test_get_author_likes_by_authorId(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.get(self.url5, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['type'], 'likes')
        self.assertEqual(response.data['id'], 'http://testserver/api/authors/ana/likes')
        self.assertEqual(len(response.data['src']), 2)
        self.assertEqual(response.data['src'][0]['id'], 'http://testserver/api/authors/ana/liked/2')
        self.assertEqual(response.data['src'][1]['id'], 'http://testserver/api/authors/ana/liked/1')

    def test_get_likes_404(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        response = self.client.get(self.url6, **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.get(self.url7, **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.get(self.url8, **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class LikeViewTest(APITestCase):
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
        self.post = PostModel.objects.create(**self.public_data)
        self.comment_data = {
            'id': 'http://testserver/api/authors/ana/commented/1',
            'author': self.author,
            'comment': 'This is a comment',
            'contentType': 'text/plain',
            'post': self.post
        }
        
        self.comment = CommentModel.objects.create(**self.comment_data)

        self.url = reverse('socialapp:api-sendLike-author_pk', kwargs = {'author_pk': 'ana'})
        self.url2 = reverse('socialapp:api-like-like_id', kwargs = {'like_id': 'http://testserver/api/authors/ana/liked/1'})
        self.url3 = reverse('socialapp:api-like-author_pk-like_pk', kwargs = {'author_pk': 'ana', 'like_pk': '1'})
        self.url4 = reverse('socialapp:api-sendLike-author_pk', kwargs = {'author_pk': 'bob'})

    def test_no_cred(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_a_like_and_database(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        body = {
            "type": "like",
            "post": "http://testserver/api/authors/ana/posts/1"
        }
        response = self.client.post(self.url, body, **headers)
        like_model = LikeModel.objects.get(mid = 1)
        self.assertEqual(like_model.type, 'like')
        self.assertEqual(like_model.id, 'http://testserver/api/authors/ana/liked/1')
        self.assertEqual(like_model.post, self.post)
        self.assertEqual(like_model.comment, None)
        self.assertEqual(like_model.object, 'http://testserver/api/authors/ana/posts/1')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['author']['id'], 'http://testserver/api/authors/ana')
        self.assertEqual(response.data['id'], 'http://testserver/api/authors/ana/liked/1')
        self.assertEqual(response.data['object'], 'http://testserver/api/authors/ana/posts/1')
        response = self.client.post(self.url, body, **headers)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_post_404_notFound(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        body = {
            "type": "like",
            "post": "http://testserver/api/authors/ana/posts/1"
        }
        response = self.client.post(self.url4, body, **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_get_a_like_by_likeId(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        post_like_data = {
            'id': 'http://testserver/api/authors/ana/liked/1',
            'author': self.author,
            'post': self.post,
            'object': 'http://testserver/api/authors/ana/posts/1' 
        }
        LikeModel.objects.create(**post_like_data)
        response = self.client.get(self.url2, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['author']['id'], 'http://testserver/api/authors/ana')
        self.assertEqual(response.data['id'], 'http://testserver/api/authors/ana/liked/1')
        self.assertEqual(response.data['object'], 'http://testserver/api/authors/ana/posts/1')

    def test_get_a_like_by_likePk(self):
        credentials = base64.b64encode(b'ana:12345678').decode('utf-8')
        headers = {
            "HTTP_X-Original-Host": 'http://testserver/api/',
            'HTTP_AUTHORIZATION': f'Basic {credentials}',
            "Content-Type": "application/json"
        }
        post_like_data = {
            'id': 'http://testserver/api/authors/ana/liked/1',
            'author': self.author,
            'post': self.post,
            'object': 'http://testserver/api/authors/ana/posts/1' 
        }
        LikeModel.objects.create(**post_like_data)
        response = self.client.get(self.url3, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['author']['id'], 'http://testserver/api/authors/ana')
        self.assertEqual(response.data['id'], 'http://testserver/api/authors/ana/liked/1')
        self.assertEqual(response.data['object'], 'http://testserver/api/authors/ana/posts/1')

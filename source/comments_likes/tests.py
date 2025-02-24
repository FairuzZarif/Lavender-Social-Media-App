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
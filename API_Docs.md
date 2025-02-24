# Lavender API
## Version: 1.0.0

### /api/api/authors/{author_pk}/posts/

#### GET
##### Summary:

Retrieve posts for a specific author

##### Description:


            Get posts created by a specific author. If the user is the author, 
            all posts will be returned. If the user is a friend, only public 
            and friends-only posts will be visible. If the user is a stranger, 
            only public posts will be returned.
            - Authentication: Optional for public posts.
            - Permissions: Authenticated users can view more restricted posts.
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_pk | path | Primary key (serial) of the author | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Successfully retrieved posts |
| 403 | Permission denied |
| 404 | Author not found |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

#### POST
##### Summary:

Create a new post for a specific author

##### Description:


            Create a new post under a specific author's profile.
            - Authentication: Required.
            - Permissions: Only authenticated users can create posts.
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_pk | path | Primary key (serial) of the author | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 201 | Post created successfully |
| 400 | Invalid post data |
| 404 | Author not found |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

### /api/api/authors/{author_pk}/posts/{post_pk}

#### GET
##### Summary:

Retrieve a specific post

##### Description:


            Get a specific post with detailed information such as comments and likes.
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_mid | path | Primary key (serial) of the author | Yes | string |
| author_pk | path |  | Yes | string |
| post_mid | path | Primary key (serial) of the post | Yes | string |
| post_pk | path |  | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Successfully retrieved post |
| 403 | Permission denied |
| 404 | Post not found |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

#### PUT
##### Summary:

Update a specific post

##### Description:


            Update the content of a specific post. Only the post author can update the post.
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_mid | path | Primary key (serial) of the author | Yes | string |
| author_pk | path |  | Yes | string |
| post_mid | path | Primary key (serial) of the post | Yes | string |
| post_pk | path |  | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Post updated successfully |
| 400 | Invalid input |
| 403 | Permission denied |
| 404 | Post not found |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

#### DELETE
##### Summary:

Delete a specific post

##### Description:


            Delete a specific post by its post ID. Only the post author can delete the post..
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_mid | path | Primary key (serial) of the author | Yes | string |
| author_pk | path |  | Yes | string |
| post_mid | path | Primary key (serial) of the post | Yes | string |
| post_pk | path |  | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 204 | Post deleted successfully |
| 403 | Permission denied |
| 404 | Post not found |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

### /api/api/authors/{author_pk}/posts/{post_pk}/image

#### GET
##### Summary:

Retrieve the image of an image post

##### Description:


            Get the image inside an image post.
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_pk | path | Primary key (serial) of the author | Yes | string |
| post_id | path | id (fqid) of the post | Yes | string |
| post_pk | path | Primary key (serial) of the post | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Successfully retrieved the image |
| 404 | Post not found |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

### /api/api/posts/{post_id}

#### GET
##### Summary:

Retrieve a specific post

##### Description:


            Get a specific post with detailed information such as comments and likes.
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_mid | path | Primary key (serial) of the author | Yes | string |
| post_id | path |  | Yes | string |
| post_mid | path | Primary key (serial) of the post | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Successfully retrieved post |
| 403 | Permission denied |
| 404 | Post not found |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

#### PUT
##### Summary:

Update a specific post

##### Description:


            Update the content of a specific post. Only the post author can update the post.
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_mid | path | Primary key (serial) of the author | Yes | string |
| post_id | path |  | Yes | string |
| post_mid | path | Primary key (serial) of the post | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Post updated successfully |
| 400 | Invalid input |
| 403 | Permission denied |
| 404 | Post not found |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

#### DELETE
##### Summary:

Delete a specific post

##### Description:


            Delete a specific post by its post ID. Only the post author can delete the post..
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_mid | path | Primary key (serial) of the author | Yes | string |
| post_id | path |  | Yes | string |
| post_mid | path | Primary key (serial) of the post | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 204 | Post deleted successfully |
| 403 | Permission denied |
| 404 | Post not found |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

### /api/api/posts/{post_id}/image

#### GET
##### Summary:

Retrieve the image of an image post

##### Description:


            Get the image inside an image post.
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_pk | path | Primary key (serial) of the author | Yes | string |
| post_id | path | id (fqid) of the post | Yes | string |
| post_pk | path | Primary key (serial) of the post | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Successfully retrieved the image |
| 404 | Post not found |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

### /api/api/profileimage/{img_id}

#### GET
##### Summary:

retrive the profile image of an author

##### Description:


            retrive the profile image of an author, by this it can be hosted in different node
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| img_id | path | id of the profile image, it include the type such as .jpg | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | return the image file. |
| 404 | Profile image Not Found |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

### /api/authors/

#### GET
##### Summary:

Retrieve all authors

##### Description:


            Retrieve a list of all authors registered in the system.
            - Authentication: Required.
            - Permissions: Authenticated users can retrieve the list of authors.
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| page | query | Page number for pagination. | No | integer |
| size | query | Number of authors per page. | No | integer |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | A list of authors. |
| 401 | Unauthorized |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

#### POST
##### Summary:

Create a new author

##### Description:


            Register a new author in the system.
            - Authentication: Not required.
            - Permissions: Anyone can create a new author account.
        

##### Responses

| Code | Description |
| ---- | ----------- |
| 201 | Author created successfully. |
| 400 | Bad Request |
| 409 | Conflict |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

### /api/authors/{actor_pk}/frae/{object_id}

#### POST
##### Summary:

Send follow request to a specific user

##### Description:


            Send a follow request from actor_pk to object_id. Here object_id 
            refers to the id who is going to be followed, and actor_pk 
            refers to the primary key of the current user. Once the follow request
            is created, the followee (from the other end) can be notified.
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| actor_pk | path | Primary key (serial) of the author | Yes | string |
| object_id | path | Id (FQID) of the followee | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 201 | Created |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

#### DELETE
##### Summary:

Delete a follow request someone sended to the current user

##### Description:


            Delete a follow request object_id sent to actor_pk. Here object_id 
            refers to the id of the user who sent the request, and actor_pk 
            refers to the primary key of the current user. Once the follow request
            is deleted, the end of object should not receive any unlisted posts
            made by current user.
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| actor_pk | path | Primary key (serial) of the author | Yes | string |
| object_id | path | Id (FQID) of the follower | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 404 | Not Found |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

### /api/authors/{author_id}

#### GET
##### Summary:

Retrieve a specific author

##### Description:


            Get the details of an author by their primary key (`author_pk`) or ID (`author_id`).
            - Authentication: Required.
            - Permissions: Authenticated users can access their own details.
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_id | path | The ID of the author. | Yes | string |
| author_pk | path | The primary key (username) of the author. | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Author details retrieved successfully. |
| 403 | Forbidden |
| 404 | Not Found |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

#### POST
##### Summary:

Verify author credentials

##### Description:


            Verify an author's credentials by providing their password.
            - Authentication: Required.
            - Permissions: Authenticated users can verify credentials for their own account.
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_id | path |  | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Credentials verified successfully. |
| 401 | Unauthorized |
| 404 | Not Found |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

#### PUT
##### Summary:

Update author details

##### Description:


            Update the details of an existing author.
            - Authentication: Required.
            - Permissions: Authenticated users can update their own details.
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_id | path |  | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Author updated successfully. |
| 400 | Bad Request |
| 404 | Not Found |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

### /api/authors/{author_id}/commented

#### GET
##### Summary:

Retrieve a list of comments

##### Description:


            Get a list of 'Comment' object.
            The parameter provided can be:
            1: author_pk
            2: author_id
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_id | path | id (fqid) of the post | Yes | string |
| author_pk | path | Primary key (serial) of the author | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Successfully retrieved a list of comments an author has made |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

#### POST
##### Summary:

Post a new comment to a post

##### Description:


            create a new comment that known which post it belongs to.
            The parameter provided is: author_pk
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_id | path |  | Yes | string |
| author_pk | path | Primary key (serial) of the author | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 201 | Successfully post a comment |
| 400 | Invalid input |
| 404 | Author or Post not found |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

### /api/authors/{author_id}/liked

#### GET
##### Summary:

Retrieve Likes

##### Description:


            Retrieve 'likes' object on a post, comment, or retrieve all likes that made by an author.
            The parameter provided is: 
            1: author_pk + post_pk
            2: post_id
            3: author_pk + post_pk + comment_pk
            4: author_pk
            5: author_id
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_id | path | Id (fqid) of the author | Yes | string |
| author_pk | path | Primary key (serial) of the author | Yes | string |
| comment_pk | path | Primary key (serial) of the comment | Yes | string |
| post_id | path | Id (fqid) of the post | Yes | string |
| post_pk | path | Primary key (serial) of the post | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Successfully get likes |
| 404 | Comment or Post not found |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

### /api/authors/{author_pk}

#### GET
##### Summary:

Retrieve a specific author

##### Description:


            Get the details of an author by their primary key (`author_pk`) or ID (`author_id`).
            - Authentication: Required.
            - Permissions: Authenticated users can access their own details.
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_id | path | The ID of the author. | Yes | string |
| author_pk | path | The primary key (username) of the author. | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Author details retrieved successfully. |
| 403 | Forbidden |
| 404 | Not Found |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

#### POST
##### Summary:

Verify author credentials

##### Description:


            Verify an author's credentials by providing their password.
            - Authentication: Required.
            - Permissions: Authenticated users can verify credentials for their own account.
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_pk | path |  | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Credentials verified successfully. |
| 401 | Unauthorized |
| 404 | Not Found |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

#### PUT
##### Summary:

Update author details

##### Description:


            Update the details of an existing author.
            - Authentication: Required.
            - Permissions: Authenticated users can update their own details.
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_pk | path |  | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Author updated successfully. |
| 400 | Bad Request |
| 404 | Not Found |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

### /api/authors/{author_pk}/commented

#### GET
##### Summary:

Retrieve a list of comments

##### Description:


            Get a list of 'Comment' object.
            The parameter provided can be:
            1: author_pk
            2: author_id
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_id | path | id (fqid) of the post | Yes | string |
| author_pk | path | Primary key (serial) of the author | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Successfully retrieved a list of comments an author has made |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

#### POST
##### Summary:

Post a new comment to a post

##### Description:


            create a new comment that known which post it belongs to.
            The parameter provided is: author_pk
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_pk | path | Primary key (serial) of the author | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 201 | Successfully post a comment |
| 400 | Invalid input |
| 404 | Author or Post not found |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

### /api/authors/{author_pk}/commented/{comment_pk}

#### GET
##### Summary:

Retrieve a comment

##### Description:


            Get a single 'Comment' object.
            The parameter provided can be:
            1: author_pk + post_pk + comment_id
            2: comment_id
            3: comment_id
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_pk | path | Primary key (serial) of the author | Yes | string |
| comment_pk | path |  | Yes | string |
| post_id | path | id (fqid) of the post | Yes | string |
| post_pk | path | Primary key (serial) of the post | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Successfully retrieved comment for a specified post |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

### /api/authors/{author_pk}/inbox

#### POST
##### Summary:

The inbox of node

##### Description:


            The inbox receives all the new posts from followed remote authors, as well as "follow requests," likes, and comments that should be aware of.
            When sending/updating posts, body is a post object
            When sending/updating comments, body is a comment object
            When sending/updating likes, body is a like object
            When sending/updating follow requests, body is a follow object
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_pk | path | The primary key (username) of the author. | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | inbox received |
| 400 | bad request |
| 403 | wrong node username/passward or node reject connection |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

### /api/authors/{author_pk}/liked

#### GET
##### Summary:

Retrieve Likes

##### Description:


            Retrieve 'likes' object on a post, comment, or retrieve all likes that made by an author.
            The parameter provided is: 
            1: author_pk + post_pk
            2: post_id
            3: author_pk + post_pk + comment_pk
            4: author_pk
            5: author_id
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_id | path | Id (fqid) of the author | Yes | string |
| author_pk | path | Primary key (serial) of the author | Yes | string |
| comment_pk | path | Primary key (serial) of the comment | Yes | string |
| post_id | path | Id (fqid) of the post | Yes | string |
| post_pk | path | Primary key (serial) of the post | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Successfully get likes |
| 404 | Comment or Post not found |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

### /api/authors/{author_pk}/liked/{like_pk}

#### GET
##### Summary:

Retrieve Like

##### Description:


            Retrieve a single 'like' object on that made by an author.
            The parameter provided is: 
            1: like_id
            2: author_pk + like_pk
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_pk | path | Primary key (serial) of the author | Yes | string |
| like_id | path | Id (fqid) of the like | Yes | string |
| like_pk | path | Primary key (serial) of the like | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Successfully get a like |
| 404 | like object not found |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

#### POST
##### Summary:

Post a Like

##### Description:


            Post a single 'like' object on that made by an author.
            The parameter provided is author_pk
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_pk | path | Primary key (serial) of the author | Yes | string |
| like_pk | path |  | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 201 | Successfully post a like |
| 404 | author not found |
| 409 | like made by the same author |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

### /api/authors/{author_pk}/liked/send/

#### GET
##### Summary:

Retrieve Like

##### Description:


            Retrieve a single 'like' object on that made by an author.
            The parameter provided is: 
            1: like_id
            2: author_pk + like_pk
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_pk | path | Primary key (serial) of the author | Yes | string |
| like_id | path | Id (fqid) of the like | Yes | string |
| like_pk | path | Primary key (serial) of the like | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Successfully get a like |
| 404 | like object not found |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

#### POST
##### Summary:

Post a Like

##### Description:


            Post a single 'like' object on that made by an author.
            The parameter provided is author_pk
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_pk | path | Primary key (serial) of the author | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 201 | Successfully post a like |
| 404 | author not found |
| 409 | like made by the same author |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

### /api/authors/{author_pk}/post/{post_pk}/comment/{comment_id}

#### GET
##### Summary:

Retrieve a comment

##### Description:


            Get a single 'Comment' object.
            The parameter provided can be:
            1: author_pk + post_pk + comment_id
            2: comment_id
            3: comment_id
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_pk | path | Primary key (serial) of the author | Yes | string |
| comment_id | path |  | Yes | string |
| post_id | path | id (fqid) of the post | Yes | string |
| post_pk | path | Primary key (serial) of the post | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Successfully retrieved comment for a specified post |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

### /api/authors/{author_pk}/posts/

#### GET
##### Summary:

Retrieve posts for a specific author

##### Description:


            Get posts created by a specific author. If the user is the author, 
            all posts will be returned. If the user is a friend, only public 
            and friends-only posts will be visible. If the user is a stranger, 
            only public posts will be returned.
            - Authentication: Optional for public posts.
            - Permissions: Authenticated users can view more restricted posts.
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_pk | path | Primary key (serial) of the author | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Successfully retrieved posts |
| 403 | Permission denied |
| 404 | Author not found |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

#### POST
##### Summary:

Create a new post for a specific author

##### Description:


            Create a new post under a specific author's profile.
            - Authentication: Required.
            - Permissions: Only authenticated users can create posts.
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_pk | path | Primary key (serial) of the author | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 201 | Post created successfully |
| 400 | Invalid post data |
| 404 | Author not found |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

### /api/authors/{author_pk}/posts/{post_pk}

#### GET
##### Summary:

Retrieve a specific post

##### Description:


            Get a specific post with detailed information such as comments and likes.
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_mid | path | Primary key (serial) of the author | Yes | string |
| author_pk | path |  | Yes | string |
| post_mid | path | Primary key (serial) of the post | Yes | string |
| post_pk | path |  | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Successfully retrieved post |
| 403 | Permission denied |
| 404 | Post not found |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

#### PUT
##### Summary:

Update a specific post

##### Description:


            Update the content of a specific post. Only the post author can update the post.
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_mid | path | Primary key (serial) of the author | Yes | string |
| author_pk | path |  | Yes | string |
| post_mid | path | Primary key (serial) of the post | Yes | string |
| post_pk | path |  | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Post updated successfully |
| 400 | Invalid input |
| 403 | Permission denied |
| 404 | Post not found |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

#### DELETE
##### Summary:

Delete a specific post

##### Description:


            Delete a specific post by its post ID. Only the post author can delete the post..
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_mid | path | Primary key (serial) of the author | Yes | string |
| author_pk | path |  | Yes | string |
| post_mid | path | Primary key (serial) of the post | Yes | string |
| post_pk | path |  | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 204 | Post deleted successfully |
| 403 | Permission denied |
| 404 | Post not found |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

### /api/authors/{author_pk}/posts/{post_pk}/comments

#### GET
##### Summary:

Retrieve the comments for a post

##### Description:


            Get the 'Comments' object for a single post, including the 'Comment' objects as a list
            and the count of total comments for this post. 
            The parameter provided can be:
            1: author_pk + post_pk
            2: post_id
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_pk | path | Primary key (serial) of the author | Yes | string |
| post_id | path | id (fqid) of the post | Yes | string |
| post_pk | path | Primary key (serial) of the post | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Successfully retrieved comments for the specified post |
| 404 | Post not found |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

### /api/authors/{author_pk}/posts/{post_pk}/comments/{comment_id}/likes

#### GET
##### Summary:

Retrieve Likes

##### Description:


            Retrieve 'likes' object on a post, comment, or retrieve all likes that made by an author.
            The parameter provided is: 
            1: author_pk + post_pk
            2: post_id
            3: author_pk + post_pk + comment_pk
            4: author_pk
            5: author_id
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_id | path | Id (fqid) of the author | Yes | string |
| author_pk | path | Primary key (serial) of the author | Yes | string |
| comment_id | path |  | Yes | string |
| comment_pk | path | Primary key (serial) of the comment | Yes | string |
| post_id | path | Id (fqid) of the post | Yes | string |
| post_pk | path | Primary key (serial) of the post | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Successfully get likes |
| 404 | Comment or Post not found |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

### /api/authors/{author_pk}/posts/{post_pk}/image

#### GET
##### Summary:

Retrieve the image of an image post

##### Description:


            Get the image inside an image post.
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_pk | path | Primary key (serial) of the author | Yes | string |
| post_id | path | id (fqid) of the post | Yes | string |
| post_pk | path | Primary key (serial) of the post | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Successfully retrieved the image |
| 404 | Post not found |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

### /api/authors/{author_pk}/posts/{post_pk}/likes

#### GET
##### Summary:

Retrieve Likes

##### Description:


            Retrieve 'likes' object on a post, comment, or retrieve all likes that made by an author.
            The parameter provided is: 
            1: author_pk + post_pk
            2: post_id
            3: author_pk + post_pk + comment_pk
            4: author_pk
            5: author_id
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_id | path | Id (fqid) of the author | Yes | string |
| author_pk | path | Primary key (serial) of the author | Yes | string |
| comment_pk | path | Primary key (serial) of the comment | Yes | string |
| post_id | path | Id (fqid) of the post | Yes | string |
| post_pk | path | Primary key (serial) of the post | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Successfully get likes |
| 404 | Comment or Post not found |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

### /api/authors/{object_pk}/froe/

#### GET
##### Summary:

Get all follow requests for the author

##### Description:


            Get all follow requests for the current author. It will return a request
            list, which each item is a dictionary. The key of the dictionary is the id
            of the follower, and the value is the summary of the request (i.e., who 
            wants to follow who), which is also the reuqest message.
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_pk | path | Primary key (serial) of the author | Yes | string |
| object_pk | path |  | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Successfully obtained follow requests |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

### /api/authors/{object_pk}/froe/{actor_id}

#### POST
##### Summary:

accept the follow request

##### Description:


            The object(author that being followed) that choose to accept. 
            Since the follwer object is already created, then just delete the followreq model
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| actor_id | path |  | Yes | string |
| object_pk | path | primary key (Serial) of the author | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | the follow request accepted |
| 403 | Forbidden |
| 404 | no author or follow request exist |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

#### DELETE
##### Summary:

reject the follow request

##### Description:


            The object(author that being followed) that choose to reject. 
            delete the followreq model and follower model at the same time
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| actor_id | path |  | Yes | string |
| object_pk | path | primary key (Serial) of the author | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 204 | the follow request rejected |
| 403 | Forbidden |
| 404 | no author or follow request exist |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

### /api/commented/{comment_id}

#### GET
##### Summary:

Retrieve a comment

##### Description:


            Get a single 'Comment' object.
            The parameter provided can be:
            1: author_pk + post_pk + comment_id
            2: comment_id
            3: comment_id
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_pk | path | Primary key (serial) of the author | Yes | string |
| comment_id | path |  | Yes | string |
| post_id | path | id (fqid) of the post | Yes | string |
| post_pk | path | Primary key (serial) of the post | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Successfully retrieved comment for a specified post |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

### /api/liked/{like_id}

#### GET
##### Summary:

Retrieve Like

##### Description:


            Retrieve a single 'like' object on that made by an author.
            The parameter provided is: 
            1: like_id
            2: author_pk + like_pk
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_pk | path | Primary key (serial) of the author | Yes | string |
| like_id | path | Id (fqid) of the like | Yes | string |
| like_pk | path | Primary key (serial) of the like | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Successfully get a like |
| 404 | like object not found |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

#### POST
##### Summary:

Post a Like

##### Description:


            Post a single 'like' object on that made by an author.
            The parameter provided is author_pk
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_pk | path | Primary key (serial) of the author | Yes | string |
| like_id | path |  | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 201 | Successfully post a like |
| 404 | author not found |
| 409 | like made by the same author |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

### /api/posts/{post_id}

#### GET
##### Summary:

Retrieve a specific post

##### Description:


            Get a specific post with detailed information such as comments and likes.
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_mid | path | Primary key (serial) of the author | Yes | string |
| post_id | path |  | Yes | string |
| post_mid | path | Primary key (serial) of the post | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Successfully retrieved post |
| 403 | Permission denied |
| 404 | Post not found |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

#### PUT
##### Summary:

Update a specific post

##### Description:


            Update the content of a specific post. Only the post author can update the post.
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_mid | path | Primary key (serial) of the author | Yes | string |
| post_id | path |  | Yes | string |
| post_mid | path | Primary key (serial) of the post | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Post updated successfully |
| 400 | Invalid input |
| 403 | Permission denied |
| 404 | Post not found |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

#### DELETE
##### Summary:

Delete a specific post

##### Description:


            Delete a specific post by its post ID. Only the post author can delete the post..
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_mid | path | Primary key (serial) of the author | Yes | string |
| post_id | path |  | Yes | string |
| post_mid | path | Primary key (serial) of the post | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 204 | Post deleted successfully |
| 403 | Permission denied |
| 404 | Post not found |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

### /api/posts/{post_id}/comments

#### GET
##### Summary:

Retrieve the comments for a post

##### Description:


            Get the 'Comments' object for a single post, including the 'Comment' objects as a list
            and the count of total comments for this post. 
            The parameter provided can be:
            1: author_pk + post_pk
            2: post_id
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_pk | path | Primary key (serial) of the author | Yes | string |
| post_id | path | id (fqid) of the post | Yes | string |
| post_pk | path | Primary key (serial) of the post | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Successfully retrieved comments for the specified post |
| 404 | Post not found |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

### /api/posts/{post_id}/image

#### GET
##### Summary:

Retrieve the image of an image post

##### Description:


            Get the image inside an image post.
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_pk | path | Primary key (serial) of the author | Yes | string |
| post_id | path | id (fqid) of the post | Yes | string |
| post_pk | path | Primary key (serial) of the post | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Successfully retrieved the image |
| 404 | Post not found |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

### /api/posts/{post_id}/likes

#### GET
##### Summary:

Retrieve Likes

##### Description:


            Retrieve 'likes' object on a post, comment, or retrieve all likes that made by an author.
            The parameter provided is: 
            1: author_pk + post_pk
            2: post_id
            3: author_pk + post_pk + comment_pk
            4: author_pk
            5: author_id
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_id | path | Id (fqid) of the author | Yes | string |
| author_pk | path | Primary key (serial) of the author | Yes | string |
| comment_pk | path | Primary key (serial) of the comment | Yes | string |
| post_id | path | Id (fqid) of the post | Yes | string |
| post_pk | path | Primary key (serial) of the post | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Successfully get likes |
| 404 | Comment or Post not found |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

### /api/profileimage/{img_id}

#### GET
##### Summary:

retrive the profile image of an author

##### Description:


            retrive the profile image of an author, by this it can be hosted in different node
        

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| img_id | path | id of the profile image, it include the type such as .jpg | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | return the image file. |
| 404 | Profile image Not Found |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

### /api/stream/{author_id}

#### GET
##### Description:

Get the stream of posts.

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_id | path |  | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | No response body |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

### /api/stream/{author_id}/length

#### GET
##### Description:

Get the length of the stream of posts.

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_id | path |  | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | No response body |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

### /api/stream/{author_id}/posts/{seq_num}

#### GET
##### Description:

Get a specific post from the stream.

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| author_id | path |  | Yes | string |
| seq_num | path |  | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | No response body |

##### Security

| Security Schema | Scopes |
| --- | --- |
| LavenderAuth | |

============================================
Complete Authentication System For Flask App
============================================

Description
===========

The directory contains a user authentication system. It contains minimal Pyhon code (I believe :wink:)
that we can add to our project with some minor changes.

The features:

- registration new users
- login with password and logout
- account confirmation system
- password resetting for unauthenticated users
- password changing for authenticated users

To Do
=====

Few actions still need to be added:

- captcha
- add mailing system
- **change secret variables in .env.develop, .env.production, .env.testing files**
- implement update of account data
- implement deletions of account
- implement users roles

Usage
=====

Extend the code contained here. To do this, you need to add your own resource in the webapp package.

**Example** (let's crate user's post resource):

1. Create db model, schema and resource endpoints in *webapp* package:

    .. code::

        :
        ├─── webapp
        :    :
             |   app.py
             :
             ├───models
             :   :
                 |   posts.py
                 └───__init__.py
             :
             ├───schemas
             :   :
                 |   posts.py
                 └───__init__.py
             :
             ├───resources
             :   :
                 |   posts.py
                 └───__init__.py


    *models/posts.py*:

    .. code:: python

        from ..app import db
        from .base import BaseMixin


        class Post(BaseMixin, db.Model):
            """Creates object which is representation of user's post."""

            __tablename__ = 'posts'

            title = db.Column(db.String(50), nullable=False)
            body = db.Column(db.String(100), nullable=False)
            user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

            @classmethod
            def find_by_id(cls, _id: int) -> 'Post':
                """
                Returns post based on the given post id.

                :param _id: post id
                :return: post with the given id or None
                """
                return cls.query.filter_by(id=_id).first()


    *schemas/posts.py*:

    .. code:: python

        from typing import Optional
        from pydantic import BaseModel


        class PostSchema(BaseModel):
            """Post schema."""
            id: Optional[int]
            title: str
            body: str
            user_id: Optional[int]

            class Config:
                """Model configuration."""
                orm_mode = True


    *resources/posts.py*:

    .. code:: python

        from flask_restful import Resource
        from flask_jwt_extended import get_jwt_identity, jwt_required

        from ..schemas.posts import PostSchema
        from ..models.posts import Post
        from ..utils import use_schema, success_response, error_response


        class PostResource(Resource):
            """Manage single post."""

            @jwt_required()
            def get(self, post_id):
                """Returns post with given id."""
                post = Post.find_by_id(post_id)
                if post is None:
                    return error_response(message='Post not found.', http_code=404, data={})
                post_schema = PostSchema.from_orm(post)
                return success_response(message='Post data.', http_code=200, data=post_schema.dict())


        class PostListResource(Resource):
            """Manage list of posts."""

            @jwt_required()
            @use_schema
            def post(self, body: PostSchema):
                """Creates new post."""
                post = Post(**body.dict(exclude={'user_id'}))
                post.user_id = get_jwt_identity()
                post.save_to_db()
                post_schema = PostSchema.from_orm(post)
                return success_response(message='Post saved.', http_code=200, data=post_schema.dict())


    *app.py*:

    .. code:: python

        # ...

        def add_resources(api: Api):
            """
            Adds authentication endpoints.

            :param api: instance of Flask Api extension
            :return: None
            """
            # pylint: disable=import-outside-toplevel
            from .resources.users import UserResource
            from .resources.posts import PostListResource, PostResource
            # pylint: enable=import-outside-toplevel
            api.add_resource(PostListResource, '/posts')
            api.add_resource(PostResource, '/post/<int:post_id>')

        # ...

        # pylint: disable=wrong-import-position,unused-import
        from .models import users as users_models
        from .models import posts as posts_models

    *webapp.__init__.py*:

    .. code:: python

        from .app import create_app, db, users_models, posts_models

        __all__ = [
            'create_app',
            'db',
            'users_models',
            'posts_models',
        ]


2. Test your changes in development mode:

    ``$ docker-compose -f docker/docker-compose.develop.yaml up``

    .. code::

        $ curl -X POST \
               -H "Content-type: application/json" \
               -d "{\"email\":\"admin@fake-mail.com\",\"password\":\"Abcd1234\"}" \
               http://192.168.1.28:5000/auth/login

        ... it returns access token

        $ curl -X POST \
               -H "Content-type: application/json" \
               -H "Authorization: Bearer <your access token>" \
               -d "{\"title\":\"Fake post title :)\",\"body\":\"Fake post body :)\"}"
               http://192.168.1.28:5000/posts
        {
            "message": "Post saved.",
            "category": "success",
            "data": {
                "id": 1,
                "title": "Fake post title :)",
                "body": "Fake post body :)",
                "user_id": 1
            }
        }

        From above body get post id.

        curl -X GET \
             -H "Content-type: application/json"
             -H "Authorization: Bearer <your access token>"
             http://192.168.1.28:5000/post/<post ID>
        {
            "message": "Post data.",
            "category": "success",
            "data": {
                "id": 1,
                "title": "Fake post title :)",
                "body": "Fake post body :)",
                "user_id": 1
            }
        }


3. Add tests:

    .. code::

        :
        ├─── tests
        :    :
             ├─── utests
             :       test_post_resource.py

    .. code:: python

        import json
        import pytest

        from webapp import posts_models


        class TestPostResource:
            """The class tests post resource."""

            def test_create_post(self, client):

                resp = client.post('/posts', json={
                    "title": "Fake post title :)",
                    "body": "Fake post body :)"
                })

                assert resp.status_code == 200

                resp_data = json.loads(resp.data.decode('utf-8'))
                assert resp_data.get('category') == 'success'

                post_id = resp_data.get('data', {}).get('id')
                assert post_id is not None

                new_post = posts_models.Post.find_by_id(post_id)
                assert new_post is not None

            # def get_post(self ...




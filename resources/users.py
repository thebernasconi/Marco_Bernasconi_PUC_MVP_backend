# import necessary modules
from flask_restx import Namespace, Resource, fields
from flask import request
from extensions import db
from models import User
from sqlalchemy.exc import IntegrityError

# Create a namespace for users
ns = Namespace('users', description='User related operations')

# Define swagger documentation and routes
user_model = ns.model('User', {
    'id': fields.Integer(readOnly=True, description='The unique identifier of a user'),
    'name': fields.String(required=True, description='User name'),
    'email': fields.String(required=True, description='User email'),
    'phone': fields.String(required=True, description='User phone number'),
})

# Create user routes
@ns.route('/')
class UserList(Resource):

    #List all users
    @ns.marshal_list_with(user_model)
    @ns.doc(description="Gets all users information available.")
    @ns.response(200, 'List of users retrieved successfully.')
    @ns.response(404, 'No users found.')
    def get(self):
        users = db.session.execute(db.select(User)).scalars().all()
        if not users:
            ns.abort(404, 'No users found.')
        return User.query.all()
    
    #Create a new user
    @ns.expect(user_model, validate=True)
    @ns.marshal_with(user_model, code=201, description='User created successfully')
    @ns.response(400, 'Invalid data')
    @ns.response(409, 'Email already registered.')
    @ns.response(500, 'Internal Server error.')
    @ns.doc(description="Creates a new user with name, email, and phone number.")
    def post(self):
        data = request.get_json() or {}

        # basic validation
        if not data.get('name') or not data.get('email') or not data.get('phone'):
            ns.abort(400, 'Name, email and phone number are mandatory.')
        
        if '@' not in data['email']:
            ns.abort(400, 'Invalid email.')
        
        # duplicate check
        existing = db.session.execute(db.select(User).filter_by(email=data['email'])).scalar_one_or_none()
        if existing:
            ns.abort(409, 'Email already registered.')
        
        # create user
        new_user = User(
            name=data['name'],
            email=data['email'],
            phone=data['phone']
        )

        # save with error handling
        try:
            db.session.add(new_user)
            db.session.commit()
            return new_user, 201
        except IntegrityError:
            db.session.rollback()
            ns.abort(409, 'Error creating user. E-mail already registered.')
        except Exception as e:
            db.session.rollback()
            ns.abort(500, 'Internal Server Error: ' + str(e))
        
        # return created user
        return {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'phone': user.phone 
        }, 201

@ns.route('/<int:id>')
class UserResource(Resource):
    #Get a user by ID
    @ns.marshal_with(user_model)
    @ns.doc(description="Gets user information searching by it's ID.")
    @ns.response(404, 'User not found.')
    def get(self, id):
        user = db.session.get(User, id)
        if not user:
            ns.abort(404, 'User not found.')
        return user
    
    #Update a user by ID
    @ns.expect(user_model, validate=True)
    @ns.marshal_with(user_model)
    @ns.response(200, 'User updated successfully')
    @ns.response(400, 'Invalid data')
    @ns.response(404, 'User not found')
    @ns.doc(description="Updates the user information, replacing it for new information.")
    def put(self, id):
        data = request.get_json() or {}
        user = db.session.get(User, id)
        if not user:
            ns.abort(404, 'User not found.')

        # basic validation
        if not data.get('name') or not data.get('email') or not data.get('phone'):
            return {'message': 'Name, Email and Phone are mandatory.'}, 400
        user.name = data['name']
        user.email = data['email']
        user.phone = data['phone']
        db.session.commit()
        return user
    
    #Delete a user by ID
    @ns.response(204, 'User deleted')
    @ns.response(404, 'User not found.')
    @ns.doc(description="Deletes a user based on it's ID.")
    def delete(self, id):
        user = db.session.get(User, id)
        if not user:
            ns.abort(404, 'User not found.')
        db.session.delete(user)
        db.session.commit()
        return '', 204
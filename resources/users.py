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
    def get(self):
        return User.query.all()
    
    #Create a new user
    @ns.expect(user_model, validate=True)
    @ns.marshal_with(user_model, code=201)
    @ns.doc(description="Create a new user with name, email, and phone number.")
    def post(self):
        data = request.get_json()

        # basic validation
        if not data.get('name') or not data.get('email') or not data.get('phone'):
            return {'message': 'Nome, email e telefone são obrigatórios.'}, 400
        
        if '@' not in data['email']:
            return {'message': 'Email inválido.'}, 400
        
        # duplicate check
        existing = db.session.execute(db.select(User).filter_by(email=data['email'])).scalar_one_or_none()
        if existing:
            return {'message': 'Email já cadastrado.'}, 409
        
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
            return {'message': 'Erro ao criar usuário. E-mail já cadastrado.'}, 409
        
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
    def get(self, id):
        user = db.session.get(User, id)
        return user
    
    #Update a user by ID
    @ns.expect(user_model)
    @ns.marshal_with(user_model)
    def put(self, id):
        data = request.json
        user = db.session.get(User, id)
        user.name = data['name']
        user.email = data['email']
        user.phone = data['phone']
        db.session.commit()
        return user
    
    #Delete a user by ID
    @ns.response(204, 'User deleted')
    def delete(self, id):
        user = db.session.get(User, id)
        db.session.delete(user)
        db.session.commit()
        return '', 204
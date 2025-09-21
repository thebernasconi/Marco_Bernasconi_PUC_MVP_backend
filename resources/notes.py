#imports
from flask import request
from flask_restx import Namespace, Resource, fields
from extensions import db
from models import Note, User
from sqlalchemy.exc import IntegrityError

# Create a namespace for notes
ns = Namespace('notes', description='Notes related operations')

# Define swagger documentation and routes
note_model = ns.model('Note', {
    'id': fields.Integer(readOnly=True, description='O identificador único de uma anotação'),
    'title': fields.String(required=True, description='Título da anotação'),
    'content': fields.String(required=True, description='Conteúdo da anotação'),
    'status': fields.String(required=True, description='Status da anotação', default='active'),
    'user_id': fields.Integer(required=True, description='ID do usuário proprietário da anotação'),
    'created_at': fields.DateTime(readOnly=True, description='Data de criação da anotação')
})
# Create note routes
@ns.route('/')
class NoteList(Resource):
    @ns.expect(note_model, validate=True)
    @ns.marshal_with(note_model, code=201)
    def post(self):
        # Basic validation
        data = request.get_json() or {}
        if not data.get('title') or not data.get('content') or not data.get('user_id'):
            return {'message': 'Título, conteúdo e user_id são obrigatórios.'}, 400
        
        # Check if user exists
        user = db.session.get(User, data['user_id'])
        if not user:
            return {'message': 'Usuário não encontrado, não é possível criar a anotação.'}, 404
        
        # Validate status
        status = data.get('status', 'active')
        if status not in ['active', 'archived', 'closed']:
            return {'message': 'Status inválido. Deve ser "active", "archived" ou "closed".'}, 400
        
        # Create note
        new_note = Note(
            title=data['title'],
            content=data['content'],
            status=status,
            user_id=data['user_id']
        )

        try:
            db.session.add(new_note)
            db.session.commit()
            return new_note, 201
        except IntegrityError:
            db.session.rollback()
            return {'message': 'Erro ao criar anotação.'}, 500
    # List all notes    
    @ns.marshal_list_with(note_model)
    def get(self):
        notes = db.session.execute(db.select(Note)).scalars().all()
        return notes
    # Get note by ID    
@ns.route('/<int:id>')
class NoteResource(Resource):
    @ns.marshal_with(note_model)
    def get(self, id):
        note = db.session.get(Note, id)
        if not note:
            ns.abort(404, 'Anotação não encontrada.')
        return note
    # Update note by ID
    @ns.expect(note_model, validate=True)
    @ns.marshal_with(note_model)
    def put(self, id):
        note = db.session.get(Note, id)
        if not note:
            ns.abort(404, 'Anotação não encontrada.')
        data = request.get_json() or {}
        note.title = data.get('title', note.title)
        note.content = data.get('content', note.content)
        note.status = data.get('status', note.status)
        note.user_id = data.get('user_id', note.user_id)

        db.session.commit()
        return note
    
    # Delete note by ID
    @ns.response(204, 'Anotação deletada com sucesso.')
    def delete(self, id):
        note = Note.query.get_or_404(id)
        db.session.delete(note)
        db.session.commit()
        return '', 204
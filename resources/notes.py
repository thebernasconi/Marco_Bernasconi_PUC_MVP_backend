#imports
from flask import request
from flask_restx import Namespace, Resource, fields
from extensions import db
from models import Note, User
from sqlalchemy.exc import IntegrityError

# Create a namespace for notes
ns = Namespace('notes', description='Operations related to notes')

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
    @ns.doc(description="Creates a new note linked to an existing user.")
    @ns.response(201, 'Note created successfully')
    @ns.response(400, 'Missing required fields or invalid status')
    @ns.response(404, 'User not found')
    @ns.response(500, 'Internal error while creating note')
    def post(self):
        # Basic validation
        data = request.get_json() or {}
        if not data.get('title') or not data.get('content') or not data.get('user_id'):
            ns.abort(400, 'Title, content and user_id are mandatory.')
        
        # Check if user exists
        user = db.session.get(User, data['user_id'])
        if not user:
            ns.abort(404, 'User not found, could not create note.')
        
        # Validate status
        status = data.get('status', 'active')
        if status not in ['active', 'archived', 'closed']:
            ns.abort(400, 'Invalid status. Should be "active", "archived" or "closed".')
        
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
            ns.abort(500, 'Error creating note.')
        
    # List all notes    
    @ns.marshal_list_with(note_model)
    @ns.doc(description="Lists all notes available.")
    @ns.response(200, 'List of notes retrieved successfully')
    @ns.response(404, 'No notes found')
    def get(self):
        notes = db.session.execute(db.select(Note)).scalars().all()
        if not notes:
            ns.abort(404, 'No notes found.')
        return notes
    
# Get note by ID    
@ns.route('/<int:id>')
class NoteResource(Resource):
    @ns.marshal_with(note_model)
    @ns.doc(description="Gets a note by its ID.")
    @ns.response(200, 'Note retrieved successfully.')
    @ns.response(404, 'Note not found.')
    def get(self, id):
        note = db.session.get(Note, id)
        if not note:
            ns.abort(404, 'Anotação não encontrada.')
        return note
    
    # Update note by ID
    @ns.expect(note_model, validate=True)
    @ns.marshal_with(note_model)
    @ns.doc(description="Updates a note by its ID.")
    @ns.response(200, 'Note updated successfully.')
    @ns.response(400, 'Invalid data provided.')
    @ns.response(404, 'Note not found.')
    @ns.response(500, 'Internal server error while updating note.')
    def put(self, id):
        note = db.session.get(Note, id)
        if not note:
            ns.abort(404, 'Anotação não encontrada.')

        data = request.get_json() or {}
        if not isinstance(data, dict):
            ns.abort(400, 'Invalid data provided.')
            
        note.title = data.get('title', note.title)
        note.content = data.get('content', note.content)
        note.status = data.get('status', note.status)
        note.user_id = data.get('user_id', note.user_id)

        db.session.commit()
        return note
    
    # Delete note by ID
    @ns.response(204, 'Note deleted.')
    @ns.response(404, 'Note not found.')
    @ns.doc(description="Deletes a note by its ID.")
    def delete(self, id):
        note = db.session.get(Note, id)
        if not note:
            ns.abort(404, 'Note not found.')
        db.session.delete(note)
        db.session.commit()
        return '', 204
# Imports necessary libraries and modules
from flask import Flask
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from extensions import db

# Configuration settings for the app and database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['RESTX_MASK_SWAGGER'] = False

# Initialize extensions
db.init_app(app)
CORS(app)
api = Api(app, title='MVP PUC Fullstack API', version='1.0', description='API for MVP PUC Fullstack Project', doc='/docs')

# Namespaces (API routs) will be added here
from resources.users import ns as users_ns
from resources.notes import ns as notes_ns

# Register namespaces with the API
api.add_namespace(users_ns, path='/users')
api.add_namespace(notes_ns, path='/notes')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)  # Run the app in debug mode
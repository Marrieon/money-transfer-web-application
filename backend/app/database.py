from .extensions import db

# The db object is initialized in extensions.py and configured in create_app().
# This file can be used to export it or to add custom database functions.

def get_db():
    """Returns the database instance."""
    return db

def save_changes(instance):
    """A utility function to commit a single instance to the session."""
    db.session.add(instance)
    db.session.commit()
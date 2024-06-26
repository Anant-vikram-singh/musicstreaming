from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db=SQLAlchemy()
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    user_type = db.Column(db.String(20), nullable=False, default='normal')  # Added user_type column
    banned = db.Column(db.Boolean, nullable=False, default=False)
    
class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    songs = db.relationship('Song', secondary='playlist_song', backref='playlists', lazy='dynamic')

playlist_song = db.Table('playlist_song',
    db.Column('playlist_id', db.Integer, db.ForeignKey('playlist.id')),
    db.Column('song_id', db.Integer, db.ForeignKey('song.id'))
)

album_song_association = db.Table('album_song_association',
    db.Column('album_id', db.Integer, db.ForeignKey('album.id'), primary_key=True),
    db.Column('song_id', db.Integer, db.ForeignKey('song.id'), primary_key=True)
)

class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    genre = db.Column(db.String(100))
    artist = db.Column(db.String(100))
    songs = db.relationship('Song', secondary=album_song_association, backref='albums', lazy=True)

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    lyrics = db.Column(db.Text)
    duration = db.Column(db.String(20))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    ratings = db.relationship('Rating', backref='song', lazy=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_by = db.relationship('User', backref='created_songs')
    
    def as_dict(self):
        return {
            c.name: (getattr(self, c.name).isoformat() if isinstance(getattr(self, c.name), datetime) else getattr(self, c.name))
            for c in self.__table__.columns
        }

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), nullable=False)
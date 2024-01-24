from flask import Flask, flash, render_template, request, redirect, url_for,flash
from model import db,User,Song, Playlist, Rating, Album
app=Flask(__name__)
from flask import session
import json
app.secret_key = 'super secret key'
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///User.sqlite"
 
db.init_app(app)
app.app_context().push()

@app.route('/')
def home():
    songs = [song.as_dict() for song in Song.query.all()]  # Convert each song to a dictionary
    isLoggedIn = 'logged_in' in session
    songs_json = json.dumps(songs)  # Serialize the list of song dictionaries to a JSON string
    print(songs_json)
    return render_template('home.html', isLoggedIn=isLoggedIn, songs_json=songs_json, songs = songs)

@app.route('/save_playlist', methods=['POST'])
def save_playlist():
    selected_songs = request.json  # Get the selected songs from the request
    print('selected_songs', selected_songs)
    # save the selected songs to the database as a playlist
    
    selected_songs_id = [song['id'] for song in selected_songs]
    print('selected_songs_id', selected_songs_id)
    songs = Song.query.filter(Song.id.in_(selected_songs_id)).all()
    print('songs', songs)
    playlist = Playlist(name='My Playlist', songs=songs, user_id=1)
    db.session.add(playlist)
    db.session.commit()
    # return a json response
    return {'success': True}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['loginUsername']
        password = request.form['loginPassword']
        user_type = request.form['loginType']  # Add this line to get the user type from the form

        user = User.query.filter_by(username=username, password=password, user_type=user_type).first()
        uid = user.id

        if user:
            session['logged_in'] = True
            session['username'] = username
            session['role'] = user_type
            session['uid'] = uid
            
            return redirect(url_for('onboarding'))

        else:
            return render_template('login.html', error='Invalid username, password, or user type')

    return render_template('login.html', error=None)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['signupUsername']
        password = request.form['signupPassword']
        user_type = request.form['signupType']  # Add this line to get the user type from the form

        if User.query.filter_by(username=username).first():
            return render_template('signup.html', error='Username already taken')

        new_user = User(username=username, password=password, user_type=user_type)  # Pass user_type to the User model
        db.session.add(new_user)
        db.session.commit()
        
        print(new_user)
        
        if(new_user):
            session['logged_in'] = True
            session['username'] = username
            session['role'] = user_type
            session['uid'] = new_user.id
            print("user created")
            print(session)
            return redirect(url_for('onboarding'))

    return render_template('signup.html', error=None)

@app.route('/playlist', methods=['GET'])
def playlist():
    playlists = Playlist.query.all()
    return render_template('playlist.html', playlists=playlists)

@app.route('/createdummyadmin', methods=['GET'])
def createdummyadmin():
    new_user = User(username='admin', password='admin', user_type='admin')  # Pass user_type to the User model
    db.session.add(new_user)
    db.session.commit()
    return 'admin created'

@app.route('/dangerous-cleardb', methods=['GET'])
def dangerous_delete_all():
    if 'logged_in' not in session or session['role'] != 'admin':
        # Ensure that only an admin or authorized user can perform this operation
        return redirect(url_for('login'))

    # Iterate over all tables and delete all rows
    for table in reversed(db.metadata.sorted_tables):
        db.session.execute(table.delete())
    db.session.commit()

    return 'All data deleted'

@app.route('/creator', methods=['GET', 'POST'])
def creator():
    if request.method == 'POST':
        # Retrieve form data from the request
        name = request.form.get('name')
        lyrics = request.form.get('lyrics')
        duration = request.form.get('duration')
        
        # Perform validation (e.g., check if required fields are provided)
        if not name:
            return 'Name and Album ID are required fields.'

        # Create a new Song object
        new_song = Song(
            name=name,
            lyrics=lyrics,
            duration=duration,
            created_by_id = session['uid']
        )

        # Add the new song to the database
        db.session.add(new_song)
        db.session.commit()

        flash('Song created successfully')

    # If it's a GET request, render the HTML form

    if 'logged_in' not in session or session['role'] != 'creator':
        flash('You are not authorized to view this page')
        return redirect(url_for('login'))
    
    creatorSongs = Song.query.filter_by(created_by_id = session['uid'])

    return render_template('creator.html', creatorSongs = creatorSongs)

@app.route('/albumn', methods = ['GET', 'POST'])
def album():
    if request.method == 'POST':
        
        songlist = request.json
        
        pylist = []
        
        for song in songlist:
            song_id = int(song)
            pylist.append(Song.query.filter_by(id = song_id).first())
        
        print(pylist)
        
        new_albumn = Album(name = 'Albumn1',songs = pylist)

        print(new_albumn.songs)
            
        db.session.add(new_albumn)
        db.session.commit()
        
        return ''
    
    if request.method == 'GET':
        albumns = Album.query.all()
        for album in albumns:
            print(album.songs)
        return render_template('albumn.html',albumns = albumns)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/save-user-status', methods=['POST'])
def save_user_status():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    usermap = request.json
    
    userMap = usermap.get('userMap')
    returnURL = usermap.get('returnURL')
    
    # iterate the map here and set the banned flag to the corresponding users

    for us in userMap:
        user_id = us.get('key')
        status = us.get('value')
        print(user_id, status)
        
        user = User.query.filter_by(id=user_id).first()

        if user: 
            user.banned = (status == 0)  # Assuming 'banned' is a boolean field in your User model
            db.session.add(user)

    db.session.commit()
    return redirect(returnURL or url_for('admin'))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'logged_in' not in session or session['role'] != 'admin':
        flash('You are not authorized to view this page')
        return redirect(url_for('login'))

    users = User.query.all()
    songs = Song.query.all()
    playlists = Playlist.query.all()
    return render_template('admin.html', users=users, songs=songs, playlists=playlists)

@app.route('/upgrade', methods=['GET', 'POST'])
def upgrade():
    if 'username' in session:
        if request.method == 'POST':
            current_user = User.query.filter_by(username=session['username']).first()
            current_user.role = 'creator'
            db.session.commit()
            return redirect(url_for('home'))
        return render_template('upgrade.html')
    else:
        return redirect(url_for('login'))


@app.route('/onboarding', methods=['GET', 'POST'])
def onboarding():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    return render_template('onboarding.html')

if __name__ == '__main__':
    # Move db.create_all() inside the if block
    # with app.app_context():
    #     db.create_all()


    app.run(debug=True)
from flask import Flask, flash, render_template, request, redirect, url_for,flash
from model import db,User,Song
app=Flask(__name__)
from flask import session
app.secret_key = 'super secret key'
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///User.sqlite"

db.init_app(app)
app.app_context().push()

@app.route('/')
def home():
    songs = Song.query.all()  # Retrieve all songs from the database
    return render_template('home.html', songs = songs)

@app.route('/save_playlist', methods=['POST'])
def save_playlist():
    selected_songs = request.json  # Assuming data is sent as JSON
    # Process and save the playlist data as needed
    print(selected_songs)  # For demonstration purposes
    return 'Playlist saved successfully'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['loginUsername']
        password = request.form['loginPassword']
        user_type = request.form['loginType']  # Add this line to get the user type from the form

        user = User.query.filter_by(username=username, password=password, user_type=user_type).first()

        if user:
            session['logged_in'] = True
            session['username'] = username
            session['role'] = user_type
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
        
        if(new_user):
            session['logged_in'] = True
            session['username'] = username
            session['role'] = user_type
            print("user created")
            print(session)
            return redirect(url_for('onboarding'))

    return render_template('signup.html', error=None)

@app.route('/creator', methods=['GET', 'POST'])
def creator():
    if request.method == 'POST':
        # Retrieve form data from the request
        name = request.form.get('name')
        lyrics = request.form.get('lyrics')
        duration = request.form.get('duration')
        album_id = request.form.get('album_id')

        # Perform validation (e.g., check if required fields are provided)
        if not name or not album_id:
            return 'Name and Album ID are required fields.'

        # Create a new Song object
        new_song = Song(
            name=name,
            lyrics=lyrics,
            duration=duration,
            album_id=album_id
        )

        # Add the new song to the database
        db.session.add(new_song)
        db.session.commit()

        flash('Song created successfully')

    # If it's a GET request, render the HTML form

    if 'logged_in' not in session or session['role'] != 'creator':
        flash('You are not authorized to view this page')
        return redirect(url_for('login'))
    
    return render_template('creator.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'logged_in' not in session or session['role'] != 'admin':
        flash('You are not authorized to view this page')
        return redirect(url_for('login'))
    return render_template('admin.html')

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
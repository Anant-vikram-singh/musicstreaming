from flask import Flask, render_template, request, redirect, url_for,flash
from model import db,User,Song
app=Flask(__name__)

app.secret_key = 'your_secret_key_here'

app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///User.sqlite"

db.init_app(app)
app.app_context().push()

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['loginUsername']
        password = request.form['loginPassword']
        user_type = request.form['loginType']  # Add this line to get the user type from the form

        user = User.query.filter_by(username=username, password=password, user_type=user_type).first()

        if user:
            if user.user_type=="normal":
                return redirect(url_for('home'))
            else:
                return render_template('creator.html')
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

        return redirect(url_for('login'))

    return render_template('signup.html', error=None)

@app.route('/create_song', methods=['POST'])
def create_song():
    if request.method == 'POST':
        # Retrieve form data
        song_name = request.form.get('song_name')
        lyrics = request.form.get('lyrics')
        duration = request.form.get('duration')
        album_id = request.form.get('album_id')

        # Check if a song with the same name already exists
        existing_song = Song.query.filter_by(name=song_name).first()

        if existing_song:
            flash('A song with the same name already exists', 'error')
            return redirect('/create_song')

        # Create a new Song instance
        new_song = Song(name=song_name, lyrics=lyrics, duration=duration, album_id=album_id)

        # Add the new song to the database
        db.session.add(new_song)
        db.session.commit()

        # Redirect to a success page or dashboard
        return render_template('creator.html')

    # Handle other HTTP methods or invalid requests
    return render_template('create_song.html') 



if __name__ == '__main__':
    # Move db.create_all() inside the if block
    # with app.app_context():
    #     db.create_all()


    app.run(debug=True)

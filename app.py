from flask import Flask, render_template, request, redirect, url_for,flash
from model import db,User,Song
app=Flask(__name__)
from flask import session
app.secret_key = 'super secret key'
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
            session['logged_in'] = True
            session['username'] = username
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
            print("user created")
            print(session)
            return redirect(url_for('onboarding'))

    return render_template('signup.html', error=None)


@app.route('/logout')
def logout():
    session.clear()
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
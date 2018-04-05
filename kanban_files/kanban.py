from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user, LoginManager, login_required, logout_user, UserMixin, login_user
from wtforms import Form, StringField, PasswordField, validators
from hashlib import sha256
from enum import Enum
from werkzeug.security import gen_salt


# Configure the app and the database.
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kanban_files.db'
db = SQLAlchemy(app)

# Initialize log-in calls to keep track of users as they're signed in.
login_manager = LoginManager()
login_manager.init_app(app)

# Set up a login manager.
@login_manager.user_loader
def load_user(user_id):
    return User_Data.query.get(int(user_id))

# Create the tables necessary to store the data.

# Table: User Data. Ensure that you store login id, password, and salt associated with the password.
class User_Data(UserMixin,db.Model):
    __tablename__ = "UserData"

    id = db.Column(db.Integer, primary_key=True)
    login_name = db.Column(db.String(500), unique=True)
    login_password = db.Column(db.String(500))
    salt = db.Column(db.String(500))

# Table: Kanban Tasks, which will store all the tasks created in the app.

# We first create a class to represent the different task statuses.
class TaskStatus(Enum):
    to_do = "To do"
    doing = "Doing"
    done = "Done"

#
class Kanban_Items(db.Model):
    __tablename__= "KanbanItems"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("UserData.id"))
    task = db.Column(db.String(500))
    task_status = db.Column(db.Enum(TaskStatus))

# All routes:

# Main page:
# The first route directs to the main page, which contains a welcome message & options to either sign up or sign in.
@app.route('/')
def main_page():
    return render_template('main_page.html')

# Registeration page:

# We first create a form that records all the data from the user.
# A user needs to submit a username, password, and a confirmation password.

class RegisterForm(Form):
    username = StringField('Username', [
        validators.length(min=5, max=50),
        validators.data_required(),
    ])
    password = PasswordField('Password', [
        validators.data_required(),
        validators.EqualTo('confirm', message='Passwords do not match.')
    ])
    confirm = PasswordField('Confirm Password')


# The register route allows people to create an account as long as a username isn't taken.
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Create an instance of register form.
    register_form = RegisterForm(request.form)

    if request.method == 'POST' and register_form.validate():

        # Accept the username as long as the user name doesn't previously exist in the DB.
        username = register_form.username.data

        # Run a query to determine if username exists.
        if User_Data.query.filter_by(login_name = username).first() is not None:
            error = "Username already taken. Please try a new username." # this is not correct.
            return render_template('kanban_register.html',form=register_form, error=error)

        # If it doesn't, secure the password by salting and using a cryptographic hash.
        psswrd = str(((register_form.password.data).encode('utf-8')))

        # Generate a salt of the same length as the password. Store it in the database.
        salt_ = str(gen_salt(len(register_form.password.data)))

        # Prepend the salt to the password and hash the newly formed string togther.
        line_ = salt_+ psswrd
        line_ = line_.encode('utf-8')
        password = sha256(line_)

        # Instantiate an instance of the User Data class with these credentials.
        user_detail = User_Data(login_name=username, login_password=password.digest(), salt=salt_.encode('utf-8'))

        # Add the user data to the database.
        db.session.add(user_detail)
        db.session.commit()

        # Display the message to the user that they are registered.
        flash('You are now registered! You may now log in!','success')

        # Redirect to the login page.
        return redirect(url_for('log_in'))

    return render_template('kanban_register.html', form=register_form )


# LOGIN PAGE:
# Similar to the registration page, we first create a form to take in all the log-in details.

class LoginForm(Form):
    username = StringField('Username', [validators.data_required()])
    password = PasswordField('Password', [validators.data_required()])

@app.route('/login',methods=['GET', 'POST'])
def log_in():
    # Similar to the registration page, create an instance of the log in form.
    login_form = LoginForm(request.form)

    if login_form.validate():

        user = User_Data.query.filter_by(login_name=login_form.username.data).first()

        # First check if the user exists.
        if user:
            username = login_form.username.data
            password_candidate = str(((login_form.password.data).encode('utf-8')))

            # If user does exist, then retrieve salt associated with user,
            # attach it to the given password and rehash it using the same hash function.

            # Query for the salt.
            user_salt_= User_Data.query.with_entities(User_Data.salt).filter_by(login_name=username).first()

            # Decode salt.
            user_salt_usable = user_salt_.salt.decode('utf-8')

            # Concatenate salt with password.
            line = user_salt_usable + password_candidate
            print("the string hashed to check match with password.=",line)

            # Encode the concatenation.
            line = line.encode('utf-8')

            # Hash the concatenation.
            password_cand = (sha256(line)).digest()

            # Verify whether the password stored in the database matches the password generated.
            # If so, log the user in and redirect user to the Kanban board.

            user_pass = User_Data.query.with_entities(User_Data.login_password).filter_by(login_name = username).first()[0]

            if password_cand == user_pass:
                login_user(user)
                flash('You are now successfully logged in.', 'success')
                return redirect(url_for('kanban_board'))
        else:
            return redirect(url_for('log_in'))

    return render_template('kanban_login.html', form=login_form)

# A user can only access their Kanban board if they are logged in.
# When they are logged in, they will only see tasks they created.
# These tasks will be segeregated into three different categories: to do, doing, and done.
@app.route('/kanban_board')
@login_required
def kanban_board():
    if current_user.is_authenticated:
        todo = Kanban_Items.query.filter(Kanban_Items.user_id == current_user.get_id()).filter(Kanban_Items.task_status==TaskStatus.to_do).all()
        doing = Kanban_Items.query.filter(Kanban_Items.user_id == current_user.get_id()).filter(Kanban_Items.task_status==TaskStatus.doing).all()
        done = Kanban_Items.query.filter(Kanban_Items.user_id == current_user.get_id()).filter(Kanban_Items.task_status==TaskStatus.done).all()
        return render_template('kanban_index.html', todo=todo, doing=doing,done=done)

    else:
        error = "This page requires you to log in"
        return render_template('kanban_login.html', error=error)

    return render_template('kanban_index.html')


# The following functions are add and move functions for each of the three categories.
# I realize this is an inefficient way to add tasks, so with more time I would have written one add and one move to function.

# Takes input from the user and adds item in the to do section.
@app.route('/add_todo',methods=['POST'])
def add_todo(): #write test for this:
    kanban_item = Kanban_Items(user_id= current_user.get_id(),task = request.form['todoitem'], task_status = TaskStatus.to_do)
    db.session.add(kanban_item)
    db.session.commit()
    return redirect(url_for('kanban_board'))

# Takes input from the user and adds item in the doing section.
@app.route('/add_doing',methods=['POST'])
def add_doing(): #write test for this:
    kanban_item = Kanban_Items(user_id= current_user.get_id(),task = request.form['todoitem'], task_status = TaskStatus.doing)
    db.session.add(kanban_item)
    db.session.commit()
    return redirect(url_for('kanban_board'))

# Takes input from the user and adds item in the done section.
@app.route('/add_done',methods=['POST'])
def add_done(): #write test for this:
    kanban_item = Kanban_Items(user_id= current_user.get_id(),task = request.form['todoitem'], task_status = TaskStatus.done)
    db.session.add(kanban_item)
    db.session.commit()
    return redirect(url_for('kanban_board'))


# All the move routes move tasks from one category to another.

# Moves an item to the to do category.
@app.route('/move_to_todo/<id>', methods=['GET', 'POST'])
def move_to_todo(id):
    todo = Kanban_Items.query.filter_by(id =int(id)).first()
    todo.task_status = TaskStatus.to_do
    db.session.commit()
    return redirect(url_for('kanban_board'))

# Moves an item to the doing category.
@app.route('/move_to_doing/<id>', methods=['GET', 'POST'])
def move_to_doing(id):
    todo = Kanban_Items.query.filter_by(id=int(id)).first()
    todo.task_status = TaskStatus.doing
    db.session.commit()
    return redirect(url_for('kanban_board'))


# Moves an item to the done category.
@app.route('/move_to_done/<id>', methods=['GET', 'POST'])
def move_to_done(id):
    todo = Kanban_Items.query.filter_by(id=int(id)).first()
    todo.task_status = TaskStatus.done
    db.session.commit()

    return redirect(url_for('kanban_board'))

# The delete route helps delete a task.
@app.route('/delete/<id>', methods=['GET', 'POST'])
def delete(id):
    item_to_delete = Kanban_Items.query.filter_by(id=int(id)).first()
    db.session.delete(item_to_delete)
    db.session.commit()
    return redirect(url_for('kanban_board'))

# A user can log out of their Kanban board by clicking on the log out option on the page.
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You are now logged out', 'success')
    return redirect(url_for('main_page'))

if __name__ == '__main__':
    # Generate secret using a cryptographic random number generator.
    app.secret_key = "cCM\xad\x14\x1cV\xd1\xb1V\xc4\x861\xc2\xf2\xed\x1b\xc9D\x0f%HZ\xf0"
    app.run(debug=True)

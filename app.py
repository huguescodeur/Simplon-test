import platform
from functools import wraps

from flask_bcrypt import Bcrypt
from flask import Flask, flash, redirect, render_template, request, url_for, session
import psycopg2


app = Flask(__name__)

bcrypt = Bcrypt(app)

# ? Les informations pour la connexion à ma db
app.config['PG_HOST'] = 'localhost'
app.config['PG_USER'] = 'postgres'
app.config['PG_PASSWORD'] = '64062639'
app.config['PG_DB'] = 'simplondb'


app.config['SECRET_KEY'] = 'secret key'

# ! Mécanisme de protection pour obligier le user à se connecter
# ? Utiliser le décorateur @login_required
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Veuillez vous connecter pour accéder à cette page.', 'danger')
            return redirect(url_for('connexion'))
        return f(*args, **kwargs)
    return decorated_function


# ! Vérifions la connexion à la db
try:
    db = psycopg2.connect(
        host=app.config['PG_HOST'],
        user=app.config['PG_USER'],
        password=app.config['PG_PASSWORD'],
        dbname=app.config['PG_DB']
        )
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Users")
    users = cursor.fetchall()
    print(users)
    print("Connexion réussie !")
except psycopg2.Error as e:
    print(f"Erreur de connexion : {e}")
finally:
    db.close()



# ? Accueil
@app.route("/accueil")
def accueil():
    return render_template("accueil.html")

# ! Gestion Back-End des Users
# ? Register user
@app.route('/register', methods=['GET', 'POST'])
def register():
    db = psycopg2.connect(
        host=app.config['PG_HOST'],
        user=app.config['PG_USER'],
        password=app.config['PG_PASSWORD'],
        dbname=app.config['PG_DB']
    )

    cursor = db.cursor()

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        retype_password = request.form['retype_password']

        if password != retype_password:
            flash("Les mots de passe ne correspondent pas.", 'danger')
            return redirect(url_for('register'))

        select_query = "SELECT id FROM users WHERE email = %s OR username = %s"
        cursor.execute(select_query, (email, username))
        user_exist = cursor.fetchone()

        if user_exist:
            flash("L'email ou le nom d'utilisateur existe déjà.", 'danger')
        else:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            cursor.execute("SELECT id FROM roles WHERE name = 'Directrice'")
            role_id = cursor.fetchone()[0]

            insert_query = "INSERT INTO users (username, email, password, role_id) VALUES (%s, %s, %s, %s)"
            cursor.execute(insert_query, (username, email, hashed_password, role_id))
            db.commit()
           
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            user_id = cursor.fetchone()[0]

            session['user_id'] = user_id

            flash('Inscription réussie! Vous êtes maintenant connecté.', 'success')
            return redirect(url_for('accueil'))

    return render_template('register.html')



# ? Login user
@app.route('/', methods=['GET', 'POST'])
def login():
    db = psycopg2.connect(
        host=app.config['PG_HOST'],
        user=app.config['PG_USER'],
        password=app.config['PG_PASSWORD'],
        dbname=app.config['PG_DB']
    )

    cursor = db.cursor()

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        select_query = "SELECT id, email, password FROM users WHERE email = %s"
        cursor.execute(select_query, (email,))
        user = cursor.fetchone()

        if user and bcrypt.check_password_hash(user[2], password):
            session['user_id'] = user[0]
            flash('Connexion réussie!', 'success')
            return redirect(url_for('accueil'))
        else:
            flash("Email ou mot de passe incorrect.", 'danger')

    return render_template('login.html')



# ? Logout
@app.route('/logout')
@login_required
def logout():

    session.pop('user_id', None)

    flash('Déconnexion réussie!', 'success')
    return redirect(url_for('register'))


if __name__ == "__main__":
    app.run(debug=True)
    # If the system is a windows /!\ Change  /!\ the   /!\ Port
    if platform.system() == "Windows":
        app.run(host='0.0.0.0', port=50000, debug=True)
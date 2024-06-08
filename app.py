import platform
from datetime import datetime
from functools import wraps

from flask_bcrypt import Bcrypt
from flask import Flask, flash, redirect, render_template, request, url_for, session
import pymysql
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
    

@app.route("/")
def connexion():
    return render_template("index.html")


@app.route("/accueil")
def accueil():
    return render_template("accueil.html")

# ! Gestion Back-End des Users
# ? Register user
@app.route('/register', methods=['GET', 'POST'])
def register():
    # ? Connection à ma db
    db = psycopg2.connect(
        host=app.config['PG_HOST'],
        user=app.config['PG_USER'],
        password=app.config['PG_PASSWORD'],
        dbname=app.config['PG_DB']
        )
    

    # ? Utilisons un curseur pour exécuter nos requêtes SQL
    cursor = db.cursor()

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Vérifions si l'utilisateur existe déjà
        select_query = "SELECT id FROM Users WHERE username = %s"
        cursor.execute(select_query, (email,))
        user_exist = cursor.fetchone()

        if user_exist:
            flash(
                "Cet utilisateur existe déjà. Veuillez choisir un autre nom d'utilisateur.", 'danger')
        else:
            hashed_password = bcrypt.generate_password_hash(
                password)

            insert_query = "INSERT INTO Users (username, email, password) VALUES (%s, %s, %s)"
            cursor.execute(insert_query, (username, email, hashed_password))
            db.commit()
           
            cursor.execute(
                "SELECT id FROM Users WHERE username = %s", (username,))
            user_id = cursor.fetchone()[0]

           
            session['user_id'] = user_id

            flash('Inscription réussie! Vous êtes maintenant connecté.', 'success')
            return redirect(url_for('accueil'))

    return render_template('register.html')


# ? Logout
@app.route('/logout')
@login_required
def logout():

    session.pop('user_id', None)

    flash('Déconnexion réussie!', 'success')
    return redirect(url_for('register'))


if __name__ == "__main__":
    # app.run(debug=True)
    # If the system is a windows /!\ Change  /!\ the   /!\ Port
    if platform.system() == "Windows":
        app.run(host='0.0.0.0', port=50000, debug=True)
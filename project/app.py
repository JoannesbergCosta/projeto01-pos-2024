from flask import Flask, redirect, url_for, session, request, render_template
from authlib.integrations.flask_client import OAuth
from datetime import datetime

app = Flask(__name__)
app.debug = True    
app.secret_key = 'development'


oauth = OAuth(app)
suap = oauth.register(
    name='suap',
    client_id='',
    client_secret='',
    api_base_url='https://suap.ifrn.edu.br/api/',
    access_token_method='POST',
    access_token_url='https://suap.ifrn.edu.br/o/token/',
    authorize_url='https://suap.ifrn.edu.br/o/authorize/',
    fetch_token=lambda: session.get('suap_token'),
    redirect_uri='http://localhost:5000/login/authorized'  
)

@app.route("/")
def index():
    if "suap_token" in session:
        try:
            profile_data = suap.get("v2/minhas-informacoes/meus-dados")
            return render_template("index.html", profile_data=profile_data.json())
        except Exception as e:
            print(f"Error fetching profile data: {e}")
            return render_template("error.html", message="Erro ao obter dados do perfil.")
    else:
        return render_template("login.html")

@app.route("/login")
def login():
    redirect_uri = url_for('auth', _external=True)
    print(f"Redirect URI: {redirect_uri}")  
    return suap.authorize_redirect(redirect_uri)

@app.route('/logout')
def logout():
    session.pop('suap_token', None)
    return redirect(url_for('index'))

@app.route('/login/authorized')
def auth():
    try:
        token = suap.authorize_access_token()
        session['suap_token'] = token
        print(f"Access token: {token}") 
        return redirect(url_for('index'))
    except Exception as e:
        print(f"Authorization error: {e}")  
        return redirect(url_for('index'))

@app.route("/profile")
def profile():
    if "suap_token" in session:
        try:
            profile_data = suap.get("v2/minhas-informacoes/meus-dados")
            return render_template("profile.html", profile_data=profile_data.json())
        except Exception as e:
            print(f"Error fetching profile data: {e}")
            return render_template("error.html", message="Erro ao obter dados do perfil.")
    else:
        return redirect(url_for('index'))

@app.route("/formulario", methods=["GET", "POST"])
def grades():
    if "suap_token" in session:
        year = request.args.get("school_year", datetime.now().year)
        semester = request.args.get("semester", 1)
        try:
            profile_data = suap.get("v2/minhas-informacoes/meus-dados")
            grades_response = suap.get(f"v2/minhas-informacoes/boletim/{year}/{semester}/")
            grades_data = grades_response.json()

            
            print(f"Profile Data: {profile_data.json()}")
            print(f"Grades Data: {grades_data}")  

            return render_template("grades.html",
                                   grades_data=grades_data,
                                   profile_data=profile_data.json(),
                                   year=year,
                                   semester=semester)
        except Exception as e:
            print(f"Error fetching grades data: {e}")
            return render_template("error.html", message="Erro ao obter boletim.")
    else:
        return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)

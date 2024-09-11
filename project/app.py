from flask import Flask, redirect, url_for, session, request, render_template
from authlib.integrations.flask_client import OAuth
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'development'


oauth = OAuth(app)
oauth.register(
    name='suap',
    client_id='',
    client_secret='',
    api_base_url='https://suap.ifrn.edu.br/api/',
    access_token_method='POST',
    access_token_url='https://suap.ifrn.edu.br/o/token/',
    authorize_url='https://suap.ifrn.edu.br/o/authorize/',
    fetch_token=lambda: session.get('suap_token')
)



@app.route("/")
def index():
    if "suap_token" in session:

        profile_data = oauth.suap.get("v2/minhas-informacoes/meus-dados")
        return render_template("index.html", profile_data=profile_data.json())
    else:

        return render_template("login.html")



@app.route("/login")
def login():

    redirect_uri = url_for('auth', _external=True)
    print(f"Redirect URI: {redirect_uri}")  # Verifique a URI gerada
    return oauth.suap.authorize_redirect(redirect_uri)



@app.route('/logout')
def logout():
    session.pop('suap_token', None)
    return redirect(url_for('index'))



@app.route('/login/authorized')
def auth():
    try:
        token = oauth.suap.authorize_access_token()
        session['suap_token'] = token
        return redirect(url_for('index'))
    except Exception as e:
        print(f"Authorization error: {e}")  # Adicione para depuração
        return redirect(url_for('index'))

@app.route("/profile")
def profile():
    if "suap_token" in session:
        profile_data = oauth.suap.get("v2/minhas-informacoes/meus-dados")
        return render_template("profile.html", profile_data=profile_data.json())
    else:
        return redirect(url_for('index'))



@app.route("/formulario", methods=["GET", "POST"])
def grades():
    if "suap_token" in session:
        year = request.args.get("school_year", datetime.now().year)
        semester = request.args.get("semester", 1)
        profile_data = oauth.suap.get("v2/minhas-informacoes/meus-dados")
        grades_data = oauth.suap.get(f"v2/minhas-informacoes/boletim/{year}/{semester}/")
        return render_template("grades.html",
                               grades_data=grades_data.json(),
                               profile_data=profile_data.json(),
                               year=year,
                               semester=semester)
    else:
        return redirect(url_for('index'))



if __name__ == "__main__":
    app.run(debug=True)

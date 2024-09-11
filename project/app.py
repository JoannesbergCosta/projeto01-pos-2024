from flask import Flask, redirect, url_for, session, request, render_template
from authlib.integrations.flask_client import OAuth
from datetime import datetime

# Configuração do Flask
app = Flask(__name__)
app.secret_key = 'development'

# Configuração do OAuth com SUAP
oauth = OAuth(app)
oauth.register(
    name='suap',
    client_id='',  # Substitua pelo seu client_id
    client_secret='',  # Substitua pelo seu client_secret
    api_base_url='https://suap.ifrn.edu.br/api/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://suap.ifrn.edu.br/o/token/',
    authorize_url='https://suap.ifrn.edu.br/o/authorize/',
    fetch_token=lambda: session.get('suap_token')
)


# Rota principal - Exibe login ou perfil
@app.route("/")
def index():
    if "suap_token" in session:
        # Se o usuário estiver autenticado, obtenha os dados do perfil
        profile_data = oauth.suap.get("v2/minhas-informacoes/meus-dados")
        return render_template("index.html", profile_data=profile_data.json())
    else:
        # Caso contrário, exibe a tela de login
        return render_template("login.html")


# Rota para login
@app.route("/login")
def login():
    # Redireciona para a página de autorização do SUAP
    redirect_uri = url_for('auth', _external=True)
    return oauth.suap.authorize_redirect(redirect_uri)


# Rota para logout
@app.route('/logout')
def logout():
    session.pop('suap_token', None)
    return redirect(url_for('index'))


# Rota que trata o callback de autorização do SUAP
@app.route('/login/authorized')
def auth():
    token = oauth.suap.authorize_access_token()  # Obtém o token de acesso
    session['suap_token'] = token  # Armazena o token na sessão
    return redirect(url_for('index'))


# Rota para exibir o perfil do usuário
@app.route("/profile")
def profile():
    if "suap_token" in session:
        profile_data = oauth.suap.get("v2/minhas-informacoes/meus-dados")
        return render_template("profile.html", profile_data=profile_data.json())
    else:
        return redirect(url_for('index'))


# Rota para visualização dos boletins (ano/semestre)
@app.route("/formulario", methods=["GET", "POST"])
def grades():
    if "suap_token" in session:
        year = request.args.get("school_year", datetime.now().year)  # Ano selecionado
        semester = request.args.get("semester", 1)  # Semestre selecionado
        profile_data = oauth.suap.get("v2/minhas-informacoes/meus-dados")
        grades_data = oauth.suap.get(f"v2/minhas-informacoes/boletim/{year}/{semester}/")
        
        return render_template("grades.html", 
                               grades_data=grades_data.json(), 
                               profile_data=profile_data.json(), 
                               year=year, 
                               semester=semester)
    else:
        return redirect(url_for('index'))


# Inicializa a aplicação Flask
if __name__ == "__main__":
    app.run(debug=True)

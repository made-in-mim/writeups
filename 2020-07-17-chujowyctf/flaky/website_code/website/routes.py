from queue import Queue, Full, Empty
import ipaddress
import socket
import os
import time
from flask import Blueprint, request, session, url_for
from flask import render_template, render_template_string, redirect, jsonify
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import gen_salt
from authlib.integrations.flask_oauth2 import current_token
from authlib.oauth2 import OAuth2Error
from .models import db, User, OAuth2Client
from .oauth2 import authorization, require_oauth

bp = Blueprint(__name__, 'home')
csrf = CSRFProtect()
moderation_queue = Queue(maxsize=256)

FLAG = os.getenv('FLAG')
ADMIN = 'admin'

def current_user():
    if 'id' in session:
        uid = session['id']
        return User.query.get(uid)
    return None


def split_by_crlf(s):
    return [v for v in s.splitlines() if v]


@bp.route('/moderation/submit', methods=['POST'])
def submit_mod_request():
    print(f'/moderation/submit: request.remote_addr = {request.remote_addr}')
    if not current_user():
        return redirect('/')
    try:
        url = request.form.get('url')
        moderation_queue.put_nowait(url)
        return 'success'
    except Exception as e: 
        print(e)
        return 'failure (queue might be full)'

@bp.route('/moderation/take', methods=['GET'])
def take_from_mod_queue():
    user = current_user()
    if user is None or user.username != ADMIN:
        return redirect('/')
    items = []
    while not moderation_queue.empty():
        items.append(moderation_queue.get())
    return jsonify(items)


@bp.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).filter_by(password=password).first()
        if not user:
            if not User.query.filter_by(username=username).first():
                user = User(username=username, password=password)
                db.session.add(user)
                db.session.commit()
            else:
                return render_template_string('Name exists, but password is wrong. Go back to <a href="/">index</a>.')
        session['id'] = user.id
        # if user is not just to log in, but need to head back to the auth page, then go for it
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect('/')
    user = current_user()
    if user:
        clients = OAuth2Client.query.filter_by(user_id=user.id).all()
    else:
        clients = []

    return render_template('home.html', user=user, clients=clients)


@bp.route('/logout')
def logout():
    del session['id']
    return redirect('/')


@bp.route('/create_client', methods=['GET', 'POST'])
def create_client():
    user = current_user()
    if not user:
        return redirect('/')
    if request.method == 'GET':
        return render_template('create_client.html')

    client_id = gen_salt(24)
    client_id_issued_at = int(time.time())
    client = OAuth2Client(
        client_id=client_id,
        client_id_issued_at=client_id_issued_at,
        user_id=user.id,
    )

    form = request.form
    client_metadata = {
        "client_name": form["client_name"],
        "client_uri": form["client_uri"],
        "grant_types": split_by_crlf(form["grant_type"]),
        "redirect_uris": split_by_crlf(form["redirect_uri"]),
        "response_types": split_by_crlf(form["response_type"]),
        "scope": form["scope"],
        "token_endpoint_auth_method": form["token_endpoint_auth_method"]
    }
    client.set_client_metadata(client_metadata)

    if form['token_endpoint_auth_method'] == 'none':
        client.client_secret = ''
    else:
        client.client_secret = gen_salt(48)

    db.session.add(client)
    db.session.commit()
    return redirect('/')


@bp.route('/oauth/authorize', methods=['GET', 'POST'])
def authorize():
    user = current_user()
    # if user log status is not true (Auth server), then to log it in
    if not user:
        return redirect(url_for('website.routes.home', next=request.url))
    if request.method == 'GET':
        try:
            grant = authorization.validate_consent_request(end_user=user)
        except OAuth2Error as error:
            return error.error
        return render_template('authorize.html', user=user, grant=grant)
    if not user and 'username' in request.form:
        username = request.form.get('username')
        user = User.query.filter_by(username=username).first()
    return authorization.create_authorization_response(grant_user=user)


@bp.route('/oauth/token', methods=['POST'])
@csrf.exempt # no form to fill in
def issue_token():
    return authorization.create_token_response()


@bp.route('/oauth/revoke', methods=['POST'])
@csrf.exempt # no form to fill in
def revoke_token():
    return authorization.create_endpoint_response('revocation')


@bp.route('/api/flag')
@require_oauth('flag')
def api_flag():
    user = current_token.user
    if user.username == ADMIN:
        return FLAG
    return 'chCTF{no flag for you} (no, seriously, this is not the flag)'

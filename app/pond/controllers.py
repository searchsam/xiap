#!/usr/bin/python3
# Import flask dependencies
from flask import Blueprint, request, session
from flask import jsonify
from authlib.oauth2 import OAuth2Error
from .models import db, User, OAuth2Client
from .oauth2 import authorization

# Define the blueprint: 'pond', set its url prefix: app.url/pond
pond = Blueprint("pond", __name__, url_prefix="/pond")


def current_user():
    uid = session["id"]

    return User.query.get(uid)


@pond.route("/", methods=["POST"])
def home():
    if request.method == "POST":
        username = request.form.get("user")
        user = User.query.filter_by(username=username).first()

        session["id"] = user.id

        client_id = request.form.get("client_id")
        client = OAuth2Client.query.filter_by(client_id=client_id).first()
        if not client:
            client = OAuth2Client(**request.form.to_dict(flat=True))
            client.client_id = client_id
            client.client_name = client_id
            client.client_secret = request.form.get("client_secret")
            client.grant_type = "password"
            client.response_type = "code"
            client.token_endpoint_auth_method = "client_secret_basic"
            client.scope = "profile"
            client.user = user
            db.session.add(client)
            db.session.commit()

        try:
            authorization.validate_consent_request(end_user=user)
        except OAuth2Error as error:
            return error.error

        return jsonify(True), 200
    else:
        return jsonify(False), 500


@pond.route("/data", methods=["POST"])
def data():
    if request.method == "POST":
        authorization.create_token_response()

        print(request.form.get("data"))

        # authorization.create_endpoint_response("revocation")
        # del session["id"]

        return jsonify(True), 200
    else:
        return jsonify(False), 500

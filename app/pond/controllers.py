#!/usr/bin/python3
# Import flask dependencies
from flask import Blueprint, request, session
from flask import jsonify
from authlib.oauth2 import OAuth2Error
from .models import (
    db,
    OAuth2User,
    OAuth2Client,
    JournalXO,
    DataXO,
    Excepts,
    Status,
)
from .oauth2 import authorization

# Define the blueprint: 'pond', set its url prefix: app.url/pond
pond = Blueprint("pond", __name__, url_prefix="/pond")


def current_user():
    uid = session["id"]

    return OAuth2User.query.get(uid)


@pond.route("/", methods=["POST"])
def home():
    if request.method == "POST":
        username = request.form.get("user")
        user = OAuth2User.query.filter_by(username=username).first()

        session["id"] = user.id_user

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
def statusdata():
    if request.method == "POST":
        authorization.create_token_response()

        if request.form.get("data") is not None:
            print(request.form.get("data"))

            # status = list()
            # status = Status(
            #     client_id="",
            #     date_print="",
            #     sync_status="",
            #     collect_status="",
            #     sync_date="",
            #     collect_date="",
            #     create_at="",
            #     update_at="",
            # )
            # db.session.add(status)
            #
            # journal = JournalXO(
            #     client_id="",
            #     activity="",
            #     activity_id="",
            #     checksum="",
            #     creation_time="",
            #     file_size="",
            #     icon_color="",
            #     keep="",
            #     launch_times="",
            #     mime_type="",
            #     mountpoint="",
            #     mtime="",
            #     share_scope="",
            #     spent_times="",
            #     time_stamp="",
            #     title="",
            #     title_set_by_user="",
            #     uid="",
            #     create_at="",
            #     update_at="",
            # )
            # db.session.add(journal)
            #
            # data = DataXO(
            #     client_id="",
            #     activities_history="",
            #     ram="",
            #     rom="",
            #     kernel="",
            #     arqc="",
            #     mac="",
            #     create_at="",
            #     update_at="",
            # )
            # db.session.add(data)
            #
            # excepts = Excepts(
            #     client_id="",
            #     except_type="",
            #     except_messg="",
            #     file_name="",
            #     file_line="",
            #     except_code="",
            #     tb_except="",
            #     server_name="",
            #     user_name="",
            #     create_at="",
            #     update_at="",
            # )
            # db.session.add(excepts)
            #
            # db.session.commit()

        # authorization.create_endpoint_response("revocation")
        # del session["id"]

        return jsonify(True), 200
    else:
        return jsonify(False), 500

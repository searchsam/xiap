#!/usr/bin/python3
# Import flask dependencies
from flask import Blueprint, request, session, jsonify
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
import os
import json

# Define the blueprint: 'pond', set its url prefix: app.url/pond
pond = Blueprint("pond", __name__, url_prefix="/pond")


def current_client(client_id):
    if client_id:
        return OAuth2Client.query.filter_by(client_id=client_id).first()
    else:
        return None


def valid_status(client, status_data):
    print(status_data)
    status = Status.query.filter_by(date_print=status_data[0]).first()
    if not status:
        status = Status(
            client_id=client.id_client,
            date_print=status_data[0],
            sync_status=True,
            collect_status=bool(status_data[1]),
            collect_date=status_data[2],
            xk_create_at=status_data[3],
            xk_update_at=status_data[4],
        )
        db.session.add(status)
        db.session.commit()
        db.session.flush()
        return status
    else:
        return status


@pond.route("/", methods=["POST"])
def home():
    if request.method == "POST":
        username = request.form.get("user")
        user = OAuth2User.query.filter_by(username=username).first()
        session["id"] = user.id_user

        client_id = request.form.get("client_id")
        client = OAuth2Client.query.filter_by(client_id=client_id).first()
        if not client:
            session["client"] = client_id

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
        else:
            session["client"] = client.client_id

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
            json_string = request.form.get("data").replace("'", '"')
            data = json.loads(json_string)
            client = current_client(request.form.get("client"))

            if data["status"] is not None:
                status = valid_status(client, data["status"])

                if data["journal"] is not None and status:
                    journal = list()
                    for l in data["journal"]:
                        journal.append(
                            dict(
                                client_id=client.id_client,
                                xark_status_id=status.id_status,
                                activity=l[0],
                                activity_id=l[1],
                                checksum=l[2],
                                creation_time=l[3],
                                file_size=l[4],
                                icon_color=l[5],
                                keep=l[6],
                                launch_times=l[7],
                                mime_type=l[8],
                                mountpoint=l[9],
                                mtime=l[10],
                                share_scope=l[11],
                                spent_times=l[12],
                                time_stamp=l[13],
                                title=l[14],
                                title_set_by_user=l[15],
                                uid=l[16],
                                xk_create_at=l[17],
                                xk_update_at=l[18],
                            )
                        )
                    db.session.bulk_insert_mappings(JournalXO, journal)

                if data["device"] is not None and status:
                    db.session.add(
                        DataXO(
                            client_id=client.id_client,
                            xark_status_id=status.id_status,
                            activities_history=data["device"][0],
                            ram=data["device"][1],
                            rom=data["device"][2],
                            kernel=data["device"][3],
                            arqc=data["device"][4],
                            mac=data["device"][5],
                            xk_create_at=data["device"][6],
                            xk_update_at=data["device"][7],
                        )
                    )

                if data["excepts"] is not None and status:
                    excepts = list()
                    for l in data["excepts"]:
                        excepts.append(
                            dict(
                                client_id=client.id_client,
                                except_type=l[0],
                                except_messg=l[1],
                                file_name=l[2],
                                file_line=l[3],
                                except_code=l[4],
                                tb_except=l[5],
                                server_name=os.uname()[1],
                                user_name=l[6],
                                xk_create_at=l[7],
                                xk_update_at=l[8],
                            )
                        )
                    db.session.bulk_insert_mappings(Excepts, excepts)

                db.session.commit()
            else:
                return jsonify(False), 500

        authorization.create_endpoint_response("revocation")
        # del session

        return jsonify(True), 200
    else:
        return jsonify(False), 500

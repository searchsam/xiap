#!/usr/bin/python3

import os
import re
import avro
import json
import time
import pyudev
import datetime
import subprocess

# Import Flask dependencies
from flask import Blueprint, request, session, jsonify, redirect, url_for
from .models import (
    db,
    Dump,
    DataXO,
    Status,
    Excepts,
    JournalXO,
    OAuth2User,
    OAuth2Client,
)

# Import OAuth2.0 dependencies
from authlib.oauth2 import OAuth2Error
from .oauth2 import authorization

# Import Avro dependencies
import avro.schema
from avro.datafile import DataFileWriter
from avro.io import DatumWriter


# Define the blueprint: 'pond', set its url prefix: app.url/pond
pond = Blueprint("pond", __name__, url_prefix="/pond")


def current_client(client_id):
    if client_id:
        return OAuth2Client.query.filter_by(client_id=client_id).first()
    else:
        return None


def valid_status(client, status_data):
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
                db.session.flush()
            else:
                return jsonify(False), 500

        authorization.create_endpoint_response("revocation")
        # del session

        return jsonify(True), 500
    else:
        return jsonify(False), 500


@pond.route("/checkusb", methods=["GET"])
def checkusb():
    if request.method == "GET":
        context = pyudev.Context()
        monitor = pyudev.Monitor.from_netlink(context)
        monitor.filter_by("block")
        device_num = list()
        for device in context.list_devices(
            subsystem="block", DEVTYPE="partition"
        ):
            if device.get("ID_FS_LABEL") is not None:
                device_num.append(device.device_node)

        if len(device_num) > 1 or len(device_num) < 1:
            return (
                jsonify("Mas de uno o ningun dispocitivo USB conectado."),
                500,
            )

        if not os.path.isdir("/tmp/usb"):
            subprocess.Popen(
                "mkdir /tmp/usb", shell=True, stdout=subprocess.PIPE
            ).stdout.readlines()

        subprocess.Popen(
            "sudo mount {} /tmp/usb".format(device_num[0]),
            shell=True,
            stdout=subprocess.PIPE,
        ).stdout.readlines()

        try:
            subprocess.Popen(
                "lsblk | grep {}".format(device_num[0][5:]),
                shell=True,
                stdout=subprocess.PIPE,
            ).stdout.readlines()
        except ():
            return (
                jsonify("La usb no se a montado adecuadamente o esta dañada."),
                500,
            )

        files = subprocess.Popen(
            "ls /tmp/usb | grep .avro", shell=True, stdout=subprocess.PIPE
        ).stdout.readlines()

        if len(files) >= 1:
            avro_valid_files = list()
            for i in files:
                m = re.search(
                    r"[A-Z0-9]+_[a-z]+_[0-9]+.avro",
                    "/tmp/usb/" + i.decode().strip(),
                )
                if m is not None:
                    avro_valid_files.append(i.decode().strip())

            if len(avro_valid_files) >= 1:
                time_print_valid = list()
                for n in avro_valid_files:
                    d = datetime.datetime.fromtimestamp(
                        os.stat("/tmp/usb/{}".format(n)).st_mtime
                    )
                    if (datetime.datetime.now() - d).days < 30:
                        time_print_valid.append(n)

                if len(time_print_valid) < 1:
                    subprocess.Popen(
                        "sudo umount /tmp/usb",
                        shell=True,
                        stdout=subprocess.PIPE,
                    ).stdout.readlines()
                    subprocess.Popen(
                        "mkfs -t ntfs -F -Q -L 'DATA' {}".format(
                            device_num[0]
                        ),
                        shell=True,
                        stdout=subprocess.PIPE,
                    ).stdout.readlines()
                    subprocess.Popen(
                        "sudo mount {} /tmp/usb".format(device_num[0]),
                        shell=True,
                        stdout=subprocess.PIPE,
                    ).stdout.readlines()

        else:
            subprocess.Popen(
                "sudo umount /tmp/usb", shell=True, stdout=subprocess.PIPE
            ).stdout.readlines()
            subprocess.Popen(
                "mkfs -t ntfs -F -Q -L 'DATA' {}".format(device_num[0]),
                shell=True,
                stdout=subprocess.PIPE,
            ).stdout.readlines()
            subprocess.Popen(
                "sudo mount {} /tmp/usb".format(device_num[0]),
                shell=True,
                stdout=subprocess.PIPE,
            ).stdout.readlines()

        return redirect(url_for("pond.dump"))
    else:
        return jsonify(False), 500


@pond.route("/dump", methods=["GET"])
def dump():
    data = dict()
    # Read Schema for data order
    datastore = None
    with open("app/schema.avsc", "r") as f:
        datastore = json.load(f)
    datastore = datastore["fields"]

    # Tabla de clientes, obtener todo el catalogo.
    client = OAuth2Client.query.with_entities(
        OAuth2Client.id_client,
        OAuth2Client.user_id,
        OAuth2Client.client_id,
        OAuth2Client.client_name,
        OAuth2Client.client_secret,
        OAuth2Client.grant_type,
        OAuth2Client.response_type,
        OAuth2Client.token_endpoint_auth_method,
        OAuth2Client.scope,
        OAuth2Client.user,
    ).all()

    if not client:
        data["clients"] = None
    else:
        # Ordered data
        pond = list()
        for r in client:
            tmp = dict()
            for i, n in enumerate(datastore[0]["type"][0]["items"]["fields"]):
                tmp[n["name"]] = r[i]
            pond.append(tmp)
        data["clients"] = pond

    # Verificar si es la primera ves que se realiza un bulk select.
    dump = (
        Dump.query.with_entities(Dump.id_dump, Dump.dp_from, Dump.dp_to)
        .order_by(Dump.id_dump.desc())
        .first()
    )

    # Verificar el status con respecto al dump.
    date_print = None
    if not dump:
        date_print = int(datetime.datetime.now().strftime("%Y%m%d"))
        status = (
            Status.query.with_entities(
                Status.id_status,
                Status.client_id,
                Status.date_print,
                Status.sync_status,
                Status.collect_status,
                Status.sync_date,
                Status.collect_date,
                Status.xk_create_at,
                Status.xk_update_at,
                Status.create_at,
                Status.update_at,
            )
            .filter(Status.date_print <= date_print)
            .all()
        )
    else:
        if dump.dp_to >= int(datetime.datetime.now().strftime("%Y%m%d")):
            return (
                jsonify(
                    "No hay registro nuevos para volvar al dispocitivo USB."
                ),
                500,
            )

        status = (
            Status.query.with_entities(
                Status.id_status,
                Status.client_id,
                Status.date_print,
                Status.sync_status,
                Status.collect_status,
                Status.sync_date,
                Status.collect_date,
                Status.xk_create_at,
                Status.xk_update_at,
                Status.create_at,
                Status.update_at,
            )
            .filter(
                Status.date_print > dump.dp_from,
                Status.date_print <= dump.dp_to,
            )
            .all()
        )

    if not status:
        data["state"] = None
        return (
            jsonify("No hay registro nuevos para volvar al dispocitivo USB."),
            500,
        )
    else:
        # Ordered data
        pond = list()
        identers = list()
        for r in status:
            tmp = dict()
            for i, n in enumerate(datastore[1]["type"][0]["items"]["fields"]):
                if n["name"] == "id_status":
                    identers.append(r[i])
                if n["name"] == "date_print":
                    date_print = r[i]
                tmp[n["name"]] = r[i]
            pond.append(tmp)
        data["state"] = pond

    # Diario de la XO.
    journal = (
        JournalXO.query.with_entities(
            JournalXO.id_journal_xo,
            JournalXO.client_id,
            JournalXO.xark_status_id,
            JournalXO.activity,
            JournalXO.activity_id,
            JournalXO.checksum,
            JournalXO.creation_time,
            JournalXO.file_size,
            JournalXO.icon_color,
            JournalXO.keep,
            JournalXO.launch_times,
            JournalXO.mime_type,
            JournalXO.mountpoint,
            JournalXO.mtime,
            JournalXO.share_scope,
            JournalXO.spent_times,
            JournalXO.time_stamp,
            JournalXO.title,
            JournalXO.title_set_by_user,
            JournalXO.uid,
            JournalXO.xk_create_at,
            JournalXO.xk_update_at,
            JournalXO.create_at,
            JournalXO.update_at,
        )
        .filter(JournalXO.xark_status_id.in_(tuple(identers)))
        .all()
    )

    if not journal:
        data["journals"] = None
    else:
        # Ordered data
        pond = list()
        for r in journal:
            tmp = dict()
            for i, n in enumerate(datastore[2]["type"][0]["items"]["fields"]):
                tmp[n["name"]] = r[i]
            pond.append(tmp)
        data["journals"] = pond

    # Informacion de la XO.
    data_xo = (
        DataXO.query.with_entities(
            DataXO.id_data_xo,
            DataXO.client_id,
            DataXO.xark_status_id,
            DataXO.activities_history,
            DataXO.ram,
            DataXO.rom,
            DataXO.kernel,
            DataXO.arqc,
            DataXO.mac,
            DataXO.xk_create_at,
            DataXO.xk_update_at,
            DataXO.create_at,
            DataXO.update_at,
        )
        .filter(DataXO.xark_status_id.in_(tuple(identers)))
        .all()
    )

    if not data_xo:
        data["datas"] = None
    else:
        # Ordered data
        pond = list()
        for r in data_xo:
            tmp = dict()
            for i, n in enumerate(datastore[3]["type"][0]["items"]["fields"]):
                tmp[n["name"]] = r[i]
            pond.append(tmp)
        data["datas"] = pond

    # Informacion de las Excepciones.
    if not dump:
        utild = int(time.mktime(datetime.datetime.now().timetuple()))
        dp_from = date_print
        dp_to = date_print
    else:
        utild = dump.create_at
        dp_from = dump.dp_from
        dp_to = dump.dp_to
    excepts = (
        Excepts.query.with_entities(
            Excepts.id_excepts,
            Excepts.client_id,
            Excepts.except_type,
            Excepts.except_messg,
            Excepts.file_name,
            Excepts.file_line,
            Excepts.except_code,
            Excepts.tb_except,
            Excepts.server_name,
            Excepts.user_name,
            Excepts.xk_create_at,
            Excepts.xk_update_at,
            Excepts.create_at,
            Excepts.update_at,
        )
        .filter(Excepts.create_at <= utild)
        .all()
    )

    if not excepts:
        data["excepts"] = None
    else:
        # Ordered data
        pond = list()
        for r in excepts:
            tmp = dict()
            for i, n in enumerate(datastore[4]["type"][0]["items"]["fields"]):
                tmp[n["name"]] = r[i]
            pond.append(tmp)
        data["excepts"] = pond

    dump = Dump(
        user_id=1, dp_from=dp_from, dp_to=dp_to, latitude=0, longitude=0
    )
    db.session.add(dump)
    db.session.commit()
    db.session.flush()

    # Ordered data
    pond = list()
    tmp = dict()
    tmp["id_dump"] = dump.id_dump
    tmp["user_id"] = dump.user_id
    tmp["dp_from"] = dump.dp_from
    tmp["dp_to"] = dump.dp_to
    tmp["latitude"] = dump.latitude
    tmp["longitude"] = dump.longitude
    tmp["create_at"] = dump.create_at
    tmp["update_at"] = dump.update_at
    pond.append(tmp)
    data["dumps"] = pond

    # Parse the AVRO SCHEMA file
    SCHEMA = avro.schema.Parse(open("app/schema.avsc", "rb").read())
    # Create a data file using AVRO DataFileWriter
    dataFile = open(
        "/tmp/usb/"
        + "SchoolCode"
        + "_"
        + os.uname()[1]
        + "_"
        + str(int(time.time()))
        + ".avro",
        "wb",
    )
    writer = DataFileWriter(dataFile, DatumWriter(), SCHEMA)
    # Write data using DatumWriter
    writer.append(data)
    writer.close()

    subprocess.Popen(
        "sudo umount /tmp/usb", shell=True, stdout=subprocess.PIPE
    ).stdout.readlines()

    return jsonify("Volcado al dispocitivo USB exitoso."), 200

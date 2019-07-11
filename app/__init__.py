#!/usr/bin/python3

import avro
import json
import time
import click
import hashlib
import datetime

import avro.schema

# from avro.datafile import DataFileReader, DataFileWriter
from avro.datafile import DataFileWriter

# from avro.io import DatumReader, DatumWriter}
from avro.io import DatumWriter

from flask import Flask, jsonify

# Import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy

# Define the WSGI application object
app = Flask(__name__)

# Configurations
app.config.from_object("config")

# Define the database object which is imported by modules and controllers
db = SQLAlchemy(app)

# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return "404", 404


# Import a module / component using its blueprint handler variable (pool)
from app.pond.controllers import pond as pond_module
from app.pond.oauth2 import config_oauth


config_oauth(app)
# Register blueprint(s)
app.register_blueprint(pond_module)


# Build the database:
# This will create the database file using SQLAlchemy
@app.cli.command("initdb")
def initdb():
    """Populate XIAP database."""
    db.create_all()

    from app.pond.models import OAuth2User

    db.session.add(OAuth2User(username="olpc"))
    db.session.commit()

    click.echo("Initialized DataBase")


@app.cli.command("breakdb")
def breakdb():
    """Delete all tables and repopulate XAIP database."""
    db.drop_all()
    click.echo("Interrupted DataBase")


@app.cli.command("ncrypt")
@click.argument("string")
def ncrypt(string):
    """Sha256 ncrypt a string."""
    click.echo(hashlib.sha256(string.encode()).hexdigest())


@app.cli.command("dumpb")
def dumpb():
    """Dump to Bus. Bulk select of all database"""
    from app.pond.models import (
        OAuth2Client,
        Dump,
        Status,
        JournalXO,
        DataXO,
        Excepts,
    )

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
            click.echo("No hay registro nuevos.")
            return jsonify(False), 500

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
        click.echo("No hay registro nuevos.")
        return jsonify(False), 500
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
    dataFile = open("puddle.avro", "wb")
    writer = DataFileWriter(dataFile, DatumWriter(), SCHEMA)
    # Write data using DatumWriter
    writer.append(data)
    writer.close()

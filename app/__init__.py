#!/usr/bin/python3

import avro
import json
import click
import hashlib
import datetime

import avro.schema

# from avro.datafile import DataFileReader, DataFileWriter
from avro.datafile import DataFileWriter

# from avro.io import DatumReader, DatumWriter}
from avro.io import DatumWriter

from flask import Flask

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
    from app.pond.models import OAuth2Client, Dump, Status, JournalXO

    data = dict()
    # Read Schema for data order
    datastore = None
    with open("app/schema.avsc", "r") as f:
        datastore = json.load(f)
    datastore = datastore["fields"]

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

    # Ordered data
    pond = list()
    for r in client:
        tmp = dict()
        for i, n in enumerate(datastore[0]["type"]["items"]["fields"]):
            tmp[n["name"]] = r[i]
        pond.append(tmp)
    data["clients"] = pond

    dump = (
        Dump.query.with_entities(Dump.id_dump, Dump.dp_from, Dump.dp_to)
        .order_by(Dump.id_dump.desc())
        .first()
    )
    status = None
    if not dump:
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
                Status.date_print
                <= int(datetime.datetime.now().strftime("%Y%m%d"))
            )
            .all()
        )
    else:
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

    # Ordered data
    pond = list()
    identers = list()
    for r in status:
        tmp = dict()
        for i, n in enumerate(datastore[1]["type"]["items"]["fields"]):
            if n["name"] == "id_status":
                identers.append(r[i])
            print(n["name"] + "=" + str(r[i]))
            tmp[n["name"]] = r[i]
        pond.append(tmp)
    data["state"] = pond
    print(data)

    # Parse the AVRO SCHEMA file
    SCHEMA = avro.schema.Parse(open("app/schema.avsc", "rb").read())
    # Create a data file using AVRO DataFileWriter
    dataFile = open("puddle.avro", "wb")
    writer = DataFileWriter(dataFile, DatumWriter(), SCHEMA)
    # Write data using DatumWriter
    writer.append(data)
    writer.close()

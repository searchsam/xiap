#!/usr/bin/python3

# Import the database object (db) from the main application module
import time
from app import db
from authlib.flask.oauth2.sqla import OAuth2ClientMixin, OAuth2TokenMixin


class OAuth2User(db.Model):
    __tablename__ = "xp_oauth2_user"

    id_user = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True)

    def __str__(self):
        return self.username

    def get_user_id(self):
        return self.id

    def check_password(self, password):
        return password == "valid"


class OAuth2Client(db.Model, OAuth2ClientMixin):
    __tablename__ = "xp_oauth2_client"

    id_client = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("xp_oauth2_user.id_user", ondelete="CASCADE")
    )
    user = db.relationship("OAuth2User")


class OAuth2Token(db.Model, OAuth2TokenMixin):
    __tablename__ = "xp_oauth2_token"

    id_token = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("xp_oauth2_user.id_user", ondelete="CASCADE")
    )
    user = db.relationship("OAuth2User")

    def is_refresh_token_expired(self):
        expires_at = self.issued_at + self.expires_in * 2
        return expires_at < time.time()


class JournalXO(db.Model):
    __tablename__ = "xp_journal_xo"

    id_journal_xo = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(
        db.Integer,
        db.ForeignKey("xp_oauth2_client.id_client", ondelete="CASCADE"),
    )
    activity = db.Column(db.String)
    activity_id = db.Column(db.String)
    checksum = db.Column(db.String)
    creation_time = db.Column(db.String)
    file_size = db.Column(db.String)
    icon_color = db.Column(db.String)
    keep = db.Column(db.String)
    launch_times = db.Column(db.String)
    mime_type = db.Column(db.DateTime)
    mountpoint = db.Column(db.String)
    mtime = db.Column(db.String)
    share_scope = db.Column(db.String)
    spent_times = db.Column(db.String)
    spent_times = db.Column(db.String)
    time_stamp = db.Column(db.String)
    title = db.Column(db.String)
    title_set_by_user = db.Column(db.String)
    uid = db.Column(db.String)
    create_at = db.Column(db.DateTime)
    update_at = db.Column(db.DateTime)

    def __repr__(self):
        return "<Journal_Id %r>" % self.id_journal_xo


class DataXO(db.Model):
    __tablename__ = "xp_data_xo"

    id_data_xo = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(
        db.Integer,
        db.ForeignKey("xp_oauth2_client.id_client", ondelete="CASCADE"),
    )
    activities_history = db.Column(db.String)
    ram = db.Column(db.String)
    rom = db.Column(db.String)
    kernel = db.Column(db.String)
    arqc = db.Column(db.String)
    mac = db.Column(db.String)
    mac = db.Column(db.String)
    create_at = db.Column(db.DateTime)
    update_at = db.Column(db.DateTime)

    def __repr__(self):
        return "<Data_Id %r>" % self.id_data_xo


class Excepts(db.Model):
    __tablename__ = "xp_excepts"

    id_excepts = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(
        db.Integer,
        db.ForeignKey("xp_oauth2_client.id_client", ondelete="CASCADE"),
    )
    except_type = db.Column(db.String)
    except_messg = db.Column(db.String)
    file_name = db.Column(db.String)
    file_line = db.Column(db.String)
    except_code = db.Column(db.String)
    tb_except = db.Column(db.String)
    server_name = db.Column(db.String)
    user_name = db.Column(db.String)
    create_at = db.Column(db.DateTime)
    update_at = db.Column(db.DateTime)

    def __repr__(self):
        return "<Excepts %r>" % self.id_data_xo


class Status(db.Model):
    __tablename__ = "xp_status"

    id_status = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(
        db.Integer,
        db.ForeignKey("xp_oauth2_client.id_client", ondelete="CASCADE"),
    )
    date_print = db.Column(db.Integer)
    sync_status = db.Column(db.Boolean)
    collect_status = db.Column(db.Boolean)
    sync_date = db.Column(db.DateTime)
    collect_date = db.Column(db.DateTime)
    create_at = db.Column(db.DateTime)
    update_at = db.Column(db.DateTime)

    def __repr__(self):
        return "<Status %r>" % self.id_status


class Dump(db.Model):
    __tablename__ = "xp_dump"

    id_status = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("xp_oauth2_user.id_user", ondelete="CASCADE")
    )
    dp_from = db.Column(db.Integer)
    dp_to = db.Column(db.Integer)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    create_at = db.Column(db.DateTime)
    update_at = db.Column(db.DateTime)

    def __repr__(self):
        return "<Dump %r>" % self.id_dump

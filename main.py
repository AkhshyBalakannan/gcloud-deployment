from flask import Flask, request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import upgrade, Migrate, downgrade, merge
from datetime import datetime
import os
import uuid
import json


def get_env_variable(name):
    try:
        return os.environ[name]
    except KeyError:
        message = "Expected environment variable '{}' not set.".format(name)
        raise Exception(message)

# the values of those depend on your setup
DB_HOST = get_env_variable("DB_HOST")
POSTGRES_USER = get_env_variable("POSTGRES_USER")
POSTGRES_PW = get_env_variable("POSTGRES_PW")
POSTGRES_DB = get_env_variable("POSTGRES_DB")
PROJECT_ID = get_env_variable("PROJECT_ID")
INSTANCE_NAME = get_env_variable("INSTANCE_NAME")
CONNECTION=get_env_variable("CONNECTION")
DEBUG = get_env_variable("DEBUG")

# GOOGLE_APPLICATION_CREDENTIALS = get_env_variable("GOOGLE_APPLICATION_CREDENTIALS")

def is_localhost_env():
    return True if DEBUG=='True' else False

app = Flask(__name__)

if is_localhost_env():
    DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}:5432/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PW,url=DB_HOST,db=POSTGRES_DB)
else:
    DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}:5432/{db}?host=/cloudsql/{connect}'.format(user=POSTGRES_USER,pw=POSTGRES_PW,url=DB_HOST,db=POSTGRES_DB,connect=CONNECTION)



app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # silence the deprecation warning

db = SQLAlchemy(app)

migrate = Migrate(app, db)


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.Text)
    done = db.Column(db.Boolean)
    dateAdded = db.Column(db.DateTime, default=datetime.now())


def create_note(text):
    note = Note(id=uuid.uuid4(), text=text)
    db.session.add(note)
    db.session.commit()
    db.session.refresh(note)


def read_notes():
    return db.session.query(Note).all()


def update_note(note_id, text, done):
    db.session.query(Note).filter_by(id=note_id).update({
        "text": text,
        "done": True if done == "on" else False
    })
    db.session.commit()


def delete_note(note_id):
    db.session.query(Note).filter_by(id=note_id).delete()
    db.session.commit()

@app.route("/", methods=["POST", "GET"])
def view_index():
    if request.method == "POST":
        create_note(request.form['text'])
    return render_template("index.html", notes=read_notes())


@app.route("/edit/<note_id>", methods=["POST", "GET"])
def edit_note(note_id):
    if request.method == "POST":
        update_note(note_id, text=request.form['text'], done=request.form['done'])
    elif request.method == "GET":
        delete_note(note_id)
    return redirect("/", code=302)



@app.route("/admin/db/<migration_command>", methods=['GET'])
def database_migration(migration_command):
    """
    To run migration files for upgrade and downgrade

    Parameters:
    migration_command (string): migration command as upgrade and downgrade

    Returns:
    json

    """
    allowed_commands = ["upgrade", "downgrade", "merge"]
    if migration_command not in allowed_commands:
        return (
            json.dumps(
                {"message": "{} command not allowed".format(migration_command)}
            ),
            400,
        )
    # if is_localhost_env():
    #     migrations_directory = os.path.join("spc-app", "migrations")
    # else:
    migrations_directory = os.path.join("migrations")
    migrate = Migrate(app, db, directory=migrations_directory)
    if migration_command == "upgrade":
        upgrade(directory=migrate.directory)
    elif migration_command == "downgrade":
        downgrade(directory=migrate.directory)
    elif migration_command == "merge":
        merge(migrate.directory, revisions="heads", message="Merge Heads")
    return json.dumps(
        {"message": "{} done on migrations.".format(migration_command)}
    )

# Imports the Google Cloud client library
# from google.cloud import storage

# Instantiates a client
# storage_client = storage.Client()

# storage_client = storage.Client.from_service_account_json(GOOGLE_APPLICATION_CREDENTIALS)

# # The name for the new bucket
# bucket_name = "my-new-bucket"

# # Creates the new bucket
# bucket = storage_client.create_bucket(bucket_name)

# print(f"Bucket {bucket.name} created.")


# buckets = list(storage_client.list_buckets())

# print(buckets)


if __name__ == "__main__":
    # db.create_all()
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

from flask import Flask
from jobs import job

app = Flask(__name__)
app.cli.add_command(job)

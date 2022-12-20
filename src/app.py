"""
Startpoint of the flask app.
"""
from flask import Flask, render_template, request, redirect, session, flash, jsonify
import pandas as pd

from Smartphone import Smartphone
from util import *
from User import User
from Study import Study
from Sensor import Sensor
from Participant import Participant, Gender
from datetime import datetime
from dateutil.relativedelta import relativedelta


def create_app():
    app = Flask(__name__, template_folder='./html/', static_folder='./static/')
    app.secret_key = "hier ist ein geheimer Schlüssel, der verwendet wird, um sessions zu verschlüsseln"

    @app.route('/')
    def landing_page():
        return render_template("landing_page.html")

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            if not User(username, password).is_valid():
                flash("Benutzername oder Passwort falsch", "error")
                return redirect('/login')
            else:
                session['username'] = username
                session['password'] = password
                session['logged_in'] = True
                session['login_time'] = str(datetime.now())
                flash("Sie haben sich erfolgreich angemeldet", "success")
                return redirect('/study_overview')
        else:
            return render_template('login.html')

    @app.route("/logout")
    def logout():
        session['username'] = None
        session['password'] = None
        session['logged_in'] = None
        flash("Sie wurden erfolgreich ausgeloggt", "success")
        return redirect('/')

    @require_login
    @app.route('/study_overview')
    def study_overview():
        return render_template(
            'study_overview.html',
            pending_studies=Study.list_all_pending_studies(),
            current_studies=Study.list_all_current_studies(),
            ended_studies=Study.list_all_ended_studies()
        )

    @require_login
    @app.route('/new_study', methods=['GET', 'POST'])
    def new_study():
        if request.method == 'GET':
            # give the user a form to fill out what the new study should be
            return render_template(
                'new_study.html',
                sensors=Sensor.list_all_sensors(),
                start_time=(datetime.now() + relativedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
                end_time=(datetime.now() + relativedelta(hours=1) + relativedelta(months=1)).strftime(
                    "%Y-%m-%d %H:%M:%S")
            )
        else:
            # read the input which the user sent and create a new study
            name = request.form['name']
            description = request.form['description']
            start_time = datetime.strptime(request.form['start_time'], '%Y-%m-%dT%H:%M:%S')
            end_time = datetime.strptime(request.form['end_time'], '%Y-%m-%dT%H:%M:%S')
            sensors = [Sensor.from_name(sensor.name)
                       for sensor in Sensor.list_all_sensors()
                       if request.form.get(f"sensor.{sensor.name}") == "on"
                       ]
            study = Study(name, description, start_time, end_time, sensors)
            study.create()
            return redirect('/study_overview')

    @require_login
    @app.route('/edit_study/<study_id>', methods=['POST'])
    def edit_study(study_id):
        study = Study.from_id(study_id)
        study.name = request.form.get('name') or "no name"
        study.description = request.form.get('description') or "no description"
        study.start = datetime.strptime(request.form.get('start_time') or str(datetime.now()), '%Y-%m-%dT%H:%M:%S')
        study.end = datetime.strptime(request.form.get('end_time') or str(datetime.now()), '%Y-%m-%dT%H:%M:%S')
        study.sensors = [Sensor.from_name(sensor.name)
                         for sensor in Sensor.list_all_sensors()
                         if request.form.get(f"sensor.{sensor.name}") == "on"
                         ]
        study.update()
        flash("Die Studie wurde erfolgreich bearbeitet", "success")
        return redirect(f'/study/{study_id}')

    @require_login
    @app.route('/delete_study/<study_id>', methods=['POST'])
    def delete_study(study_id):
        study = Study.from_id(study_id)
        study.delete()
        flash("Die Studie wurde erfolgreich gelöscht", "success")
        return redirect('/study_overview')

    @require_login
    @app.route('/study/<study_id>')
    def inspect_study(study_id):
        study = Study.from_id(study_id)
        return render_template(
            'study.html',
            study=study,
            sensors=Sensor.list_all_sensors(),
        )

    @require_login
    @app.route('/study/<study_id>/add_participant', methods=['GET', 'POST'])
    def add_participant(study_id):
        study = Study.from_id(study_id)
        if request.method == 'GET':
            return render_template(
                'add_participant.html',
                study=study,
            )
        else:
            participant = Participant(
                surname=request.form.get("surname") or "",
                forename=request.form.get('forename') or "",
                birthday=datetime.strptime(request.form['birthday'], '%Y-%m-%d'),
                gender=request.form.get("gender") or "other"
            )
            study.add_participant(participant)
            return redirect(f'/study/{study_id}')

    @require_login
    @app.route('/study/<study_id>/participant/<participant_id>')
    def inspect_participant(study_id, participant_id):
        study = Study.from_id(study_id)
        participant = study.get_participant(participant_id)
        return render_template(
            'participant.html',
            study=study,
            participant=participant,
        )

    @require_login
    @app.route('/study/<study_id>/participant/<participant_id>/edit_participant', methods=['POST'])
    def edit_participant(study_id, participant_id):
        study = Study.from_id(study_id)
        participant = study.get_participant(participant_id)
        participant.surname = request.form.get('surname') or ""
        participant.forename = request.form.get('forename') or ""
        participant.birthday = datetime.strptime(request.form.get('birthday') or str(datetime.now()), '%Y-%m-%d')
        participant.gender = request.form.get('gender') or "other"
        study.update_participant(participant)
        flash(f'Benutzer wurde erfolgreich bearbeitet', 'success')
        return redirect(f'/study/{study_id}/participant/{participant_id}')

    @require_login
    @app.route('/study/<study_id>/participant/<participant_id>/delete_participant', methods=['POST'])
    def delete_participant(study_id, participant_id):
        """
        Lösche einen Teilnehmer aus einer Studie.
        """
        study = Study.from_id(study_id)
        participant = study.get_participant(participant_id)
        study.delete_participant(participant)
        flash(f'Benutzer wurde erfolgreich gelöscht', 'success')
        return redirect(f'/study/{study_id}')

    @app.route('/api/studies/<study_id>/participants/<participant_id>/devices', methods=['POST'])
    def api_register_devices(study_id, participant_id):
        """
        Füge ein Smartphone zu einem Teilnehmer hinzu. Das Smartphone wird bekommt die nötigen Informationen,
        also <study_id> und <participant_id> übergeben und wird daraufhin mit allen Informationen über sich,
        welche benötigt sind, eine Anfrage an diese Funktion stellen.
        """
        study = Study.from_id(study_id)
        if study is None:
            raise Exception(f"Study {study_id} not found")
        participant = study.get_participant(participant_id)
        if participant is None:
            raise Exception(f"Participant {participant_id} not found")
        smartphone = Smartphone.from_request_form(request.form)
        study.register_smartphone_to_participant(participant, smartphone)
        return ''

    @app.route('/api/studies/<study_id>/duration', methods=['POST', 'get'])
    def api_study_duration(study_id):
        """
        Gebe die Start- und Endzeit einer Studie zurück.
        Das ist nützlich, damit Teilnehmer in der Monti App sehen können, wie lange Sie noch an Ihrer Studie teilnehmen
        müssen.
        """
        study = Study.from_id(study_id)
        if study is None:
            raise Exception(f"Study {study_id} not found")
        return jsonify({
            'start': study.start,
            'end': study.end,
        })

    @app.route('/api/studies/<study_id>/participants/<participant_id>/upload_sensor_data', methods=['POST'])
    def api_upload_sensor_data(study_id, participant_id):
        """
        Lade die aufgenommenen Sensordaten eines Teilnehmers hoch.
        Die Anfrage an den Server muss dabei folgende Daten enthalten:
        - In der URL
            - <study_id>: Die ID der Studie, zu der die Sensordaten gehören
            - <participant_id>: Die ID des Teilnehmers, zu dem die Sensordaten gehören
        - im Header
            - 'Content-Type': 'application/csv'
            - 'Authorisation': token # TODO: Muss noch implementiert werden
        - im Body
            - Die Sensordaten als CSV-Datei (siehe [Sensor.py])
        """
        study = Study.from_id(study_id)
        if study is None:
            raise Exception(f"Study {study_id} not found")
        participant = study.get_participant(participant_id)
        if participant is None:
            raise Exception(f"Participant {participant_id} not found")
        sensor = Sensor.from_name(request.headers.get('sensor-type'))
        print(f"Received {sensor.name}-data from {participant_id}")
        sensor.parse_csv(request.data)
        study.add_sensor_data_to_participant(participant, sensor)
        print(f"Added {sensor.name}-data to {participant_id}")
        return ''

    return app

if __name__ == '__main__':
    app = create_app()
    app.run()

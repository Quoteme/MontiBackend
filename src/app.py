"""
Startpoint of the flask app.
"""
import os

import bleach
from flask import Flask, render_template, request, redirect, session, flash, jsonify, send_from_directory
import pandas as pd

from PatientReportedOutcomeQuestion import PatientReportedOutcomeQuestion
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
            name = bleach.clean(request.form['name'])
            description = bleach.clean(request.form['description'])
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
        study.name = bleach.clean(request.form.get('name') or "no name")
        study.description = bleach.clean(request.form.get('description') or "no description")
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
            pros=study.list_all_patient_reported_outcomes
        )

    @require_login
    @app.route('/study/<study_id>/show_patient_reported_outcome/<pro_id>', methods=['GET'])
    def show_patient_reported_outcome(study_id, pro_id):
        study = Study.from_id(study_id)
        pro = study.get_patient_reported_outcome_by_id(pro_id)
        return render_template(
            'show_patient_reported_outcome.html',
            study=study,
            patient_reported_outcome=pro,
        )

    @app.route('/study/<study_id>/add_patient_reported_outcome', methods=['GET', 'POST'])
    def add_patient_reported_outcome(study_id):
        study = Study.from_id(study_id)
        if request.method == 'GET':
            return render_template(
                'add_patient_reported_outcome.html',
                study=study,
                PatientReportedOutcomeQuestion = PatientReportedOutcomeQuestion,
                # the value of start_time must be in a format for "datetime-local" input fields
                # for example: 2018-06-12T19:30
                start_date = datetime.now().strftime("%Y-%m-%dT%H:%M"),
                # the value of end_date must be in a format for "datetime-local" input fields
                end_date = (datetime.now() + relativedelta(hours=10)).strftime("%Y-%m-%dT%H:%M"),
            )
        else:
            # Read all the questions from the form and create a new PatientReportedOutcome
            # questions are given in the form of "result.form['question'+number]"
            # where number is the number of the question
            # the type of the question is given in the form of "result.form['question_type'+number]"
            # where number is the number of the question
            questions = []
            questionNumber = 0
            while request.form.get(f"question{questionNumber}") is not None:
                question = PatientReportedOutcomeQuestion.from_type(
                    bleach.clean(request.form.get(f"question{questionNumber}")),
                    "",
                    request.form.get(f"question_type{questionNumber}"),
                )
                questions.append(question)
                questionNumber += 1
            start_date = datetime.strptime(request.form.get('start_date') or str(datetime.now()), '%Y-%m-%dT%H:%M')
            end_date = datetime.strptime(request.form.get('end_date') or str(datetime.now()), '%Y-%m-%dT%H:%M')
            pro_name = bleach.clean(request.form.get('pro_name') or "no name")
            study = Study.from_id(study_id)
            from PatientReportedOutcome import PatientReportedOutcome
            pro = PatientReportedOutcome(pro_name, study, questions, start_date, end_date)
            pro.save()
            return redirect(f'/study/{study.id}/show_patient_reported_outcome/{pro.id}')


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
                surname=bleach.clean(request.form.get("surname") or ""),
                forename=bleach.clean(request.form.get('forename') or ""),
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

    @app.route('/api/studies/<study_id>/sensors', methods=['POST', 'get'])
    def api_study_sensors(study_id):
        """
        Gebe die Liste von Sensoren aus, welche in der entsprechenden Studie getrackt werden sollen.
        """
        study = Study.from_id(study_id)
        if study is None:
            raise Exception(f"Study {study_id} not found")
        return jsonify(study.sensors)

    @app.route('/api/studies/<study_id>/sensor_names', methods=['POST', 'get'])
    def api_study_sensor_names(study_id):
        """
        Gebe die Namensiste von Sensoren aus, welche in der entsprechenden Studie getrackt werden sollen.
        """
        study = Study.from_id(study_id)
        if study is None:
            raise Exception(f"Study {study_id} not found")
        return jsonify([s.name for s in study.sensors])

    @app.route('/api/studies/<study_id>/participants/<participant_id>/upload_sensor_data', methods=['POST'])
    def api_upload_sensor_data(study_id, participant_id):
        """
        Lade die aufgenommenen Sensordaten eines Teilnehmers hoch.
        Die Anfrage an den Server muss dabei folgende Daten enthalten:
        - In der URL
            - <study_id>: Die ID der Studie, zu der die Sensordaten gehören
            - <participant_id>: Die ID des Teilnehmers, zu dem die Sensordaten gehören
        - im Header
            - 'Authorisation': token # TODO: Muss noch implementiert werden
            - 'lastModifiedDate': timestamp, an welchem die Daten in der Handydatenbank gespeichert wurden
        - im Body
            - Die Sensordaten als REALM-Datenbank
        """
        study = Study.from_id(study_id)
        if study is None:
            raise Exception(f"Study {study_id} not found")
        participant = study.get_participant(participant_id)
        if participant is None:
            raise Exception(f"Participant {participant_id} not found")
        if request.headers.get('last_modified_date') is None:
            last_modified_date = datetime.now()
        else:
            last_modified_date = datetime.strptime(request.headers.get('last_modified_date'), '%Y-%m-%d %H:%M:%S')
        last_uploaded_modification = study.get_participant_last_database_modification(participant)
        if last_modified_date is None :
            raise ValueError(f"lastModifiedDate is None")
        if last_uploaded_modification is not None and last_uploaded_modification >= last_modified_date:
            raise ValueError(f"lastModifiedDate is not newer than last uploaded modification")
        else:
            study.upload_participant_sensor_data(participant, request.files['file'], last_modified_date)
            return 'OK'

    @app.route('/api/studies/<study_id>/participants/<participant_id>/upload_sleep_data', methods=['POST'])
    def api_upload_sleep_data(study_id, participant_id):
        """
        Lade die aufgenommenen Schlafdaten eines Teilnehmers hoch. Diese sind jeweils `.wiff` Datein und müssen
        gesondert geparst werden.
        """
        study = Study.from_id(study_id)
        if study is None:
            raise Exception(f"Study {study_id} not found")
        participant = study.get_participant(participant_id)
        if participant is None:
            raise Exception(f"Participant {participant_id} not found")
        # save all files of the request
        for file in request.files:
            study.upload_participant_sleep_data(participant, request.files[file])
        return 'OK'

    @app.route('/api/studies/<study_id>/participants/<participant_id>/upload_ppg2_data', methods=['POST'])
    def api_upload_ppg2_data(study_id, participant_id):
        """
        Lade die aufgenommenen PPG2-Daten eines Teilnehmers hoch. Diese sind jeweils `.wiff` Datein und müssen
        gesondert geparst werden.
        """
        study = Study.from_id(study_id)
        if study is None:
            raise Exception(f"Study {study_id} not found")
        participant = study.get_participant(participant_id)
        if participant is None:
            raise Exception(f"Participant {participant_id} not found")
        # save all files of the request
        for file in request.files:
            study.upload_participant_ppg2_data(participant, request.files[file])
        return 'OK'

    @app.route('/api/studies/<study_id>/participants/<participant_id>/upload_acc_data', methods=['POST'])
    def api_upload_acc_data(study_id, participant_id):
        """
        Lade die aufgenommenen Accelerometer-Daten eines Teilnehmers hoch. Diese sind jeweils `.wiff` Datein und müssen
        gesondert geparst werden.
        Diese Funktionalität ist besonders an Version 2 der Corsano-Bänder, da ab dieser Version Accelerometer-Daten
        nicht mehr über die Sensordatenbank (`.realm`) gespeichert werden, sondern als eigene `.wiff` Dateien.
        """
        study = Study.from_id(study_id)
        if study is None:
            raise Exception(f"Study {study_id} not found")
        participant = study.get_participant(participant_id)
        if participant is None:
            raise Exception(f"Participant {participant_id} not found")
        # save all files of the request
        for file in request.files:
            study.upload_participant_acc_data(participant, request.files[file])
        return 'OK'

    @app.route('/download_realm/<study_id>/<participant_id>/<file>', methods=['GET'])
    def download_realm(study_id, participant_id, file):
        """
        Lade eine Realm Datenbank herunter.
        """
        study = Study.from_id(study_id)
        if study is None:
            raise Exception(f"Study {study_id} not found")
        participant = study.get_participant(participant_id)
        if participant is None:
            raise Exception(f"Participant {participant_id} not found")
        # get the base directory of the application
        basedir = os.path.abspath(os.path.dirname(__file__))
        # join the base directory with the relative path to the file
        filedirectory = os.path.join(basedir, '..', study.get_participant_database_directory(participant))
        # get current path of this executable
        return send_from_directory(
            directory=filedirectory,
            path=file,
            as_attachment=True
        )

    return app

if __name__ == '__main__':
    app = create_app()
    app.run()

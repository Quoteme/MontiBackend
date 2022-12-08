import os

from _pytest import monkeypatch

import src.Participant

def test_participant_init():
    participant = src.Participant.Participant()
    assert participant is not None

def test_create_new_participant_creates_directory(mocker):
    # Set up the mock
    mocker.patch.object(os, 'mkdir', return_value=None)

    # Call the function being tested
    study_participant_path = "./data/testStudie/participants"
    participant = src.Participant.Participant()
    participant.create(study_participant_path)

    # Verify that os.mkdir was called with the correct arguments
    os.mkdir.assert_called_with(f"{study_participant_path}/{participant.id}")
import io
import os

from _pytest import monkeypatch

import src.Participant

def test_participant_init():
    participant = src.Participant.Participant()
    assert participant is not None

def test_create_new_participant(mocker, tmp_path):
    # Set up the mock
    mocker.patch.object(os, 'mkdir', return_value=None)
    mock_file = io.StringIO()
    mocker.patch.object(mock_file, 'close', return_value=None)
    mocker.patch('builtins.open', return_value=mock_file)

    # Call the function being tested
    participant = src.Participant.Participant()
    participant.create(tmp_path)

    # Verify that os.mkdir was called with the correct arguments
    os.mkdir.assert_called_with(f"{tmp_path}/{participant.id}")
    # TODO: Verify that the file was written to
    mock_file.seek(0)
    assert mock_file.read() == participant.to_json()
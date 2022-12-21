db.auth('root', 'rootpassword')

studies = db.getSiblingDB('studies')

studies.createUser({
  user: "study-editor",
  pwd: "studiesservicepassword",
  roles: [{role: "readWrite", db: "studies"}],
  comment: "User for changing study data"
});

participants = db.getSiblingDB('participants')

participants.createUser({
  user: "participant-editor",
  pwd: "participantpassword",
  roles: [{role: "readWrite", db: "participants"}],
  comment: "User for changing participant data"
});

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


association_table = db.Table(
    "association_table_role",
    db.Column("user", db.Integer, db.ForeignKey("user.id")),
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    lastname = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    createdAt = db.Column(db.DateTime, nullable=False)



    def init(self, name, lastname, email, password):
        self.name = name
        self.lastname = lastname
        self.email = email
        self.password = password

    def repr(self):
        return '<User %r>' % self.username

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "lastname": self.lastname,
            "email": self.email,
            # do not serialize the password, its a security breach
        }

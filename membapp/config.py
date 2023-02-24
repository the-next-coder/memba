SECRET_KEY="Tg62$&ju93"
SQLALCHEMY_DATABASE_URI='mysql+mysqlconnector://root@localhost/memba_db'

class Config:
    ADMIN_EMAIL="test@memba.com"
    SECRET_KEY="45P$!f71#&k"

class LiveConfig(Config):
    ADMIN_EMAIL="admin@memba.com"
    SERVER_ADDRESS="https://server.memba.com"

class TestConfig(Config):
    SERVER_ADDRESS="https://127.0.0.1:5000"
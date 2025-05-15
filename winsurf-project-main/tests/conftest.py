import pytest
from quote_system.app import create_app
from quote_system.database.models import db as _db

@pytest.fixture(scope='session')
def app():
    app = create_app('config.TestConfig')
    return app

@pytest.fixture(scope='session')
def db(app):
    with app.app_context():
        _db.create_all()
        yield _db
        _db.drop_all()

@pytest.fixture(scope='function')
def session(db):
    connection = db.engine.connect()
    transaction = connection.begin()
    
    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)
    
    db.session = session
    
    yield session
    
    transaction.rollback()
    connection.close()
    session.remove()

@pytest.fixture(scope='function')
def client(app, session):
    return app.test_client()

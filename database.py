from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from server.database.base import Base


class Session:
    def __init__(self, session):
        self._session = session

    def __getattr__(self, key):
        if hasattr(self._session, key):
            return getattr(self._session, key)
        raise AttributeError(key)

    def execute(self, statement):
        self._session.execute(statement)
        self._session.commit()

    def save(self, model):
        self._session.add(model)
        self._session.commit()

    def delete(self, model):
        self._session.delete(model)
        self._session.commit()

    def bulk_save_objects(self, models):
        self._session.bulk_save_objects(models)
        self._session.commit()


class Database:
    def __init__(self, configuration=None):
        if configuration:
            self.configure(configuration)

    def configure(self, configuration):
        self.engine = create_engine(configuration.SQLALCHEMY_URI)
        self.session_provider = sessionmaker(bind=self.engine)

    def make_session(self):
        raw_session = self.session_provider()
        return Session(raw_session)

    def create_database(self):
        Base.metadata.create_all(self.engine)

    def delete_database(self):
        Base.metadata.drop_all(self.engine)

    def store_model(self, model, session=None):
        session = session or self.make_session()

        session.add(model)
        session.commit()

        return model

    @contextmanager
    def session(self, commit_on_exit=True, *args, **kwargs):
        session = self.make_session()

        try:
            yield session
        except:
            session.rollback()
            raise
        else:
            if commit_on_exit:
                session.commit()
        finally:
            session.close()

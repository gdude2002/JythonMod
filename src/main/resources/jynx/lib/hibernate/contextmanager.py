__all__ = ["hn_session", "hn_transact", "buildSessionFactory"]

from sessionfactory import buildSessionFactory

class hn_session(object):
    '''
    Context manager which opens/closes hibernate sessions.
    '''
    def __init__(self, *classes):
        sessionFactory = buildSessionFactory(*classes)
        self.session   = sessionFactory.openSession()

    def __enter__(self):
        return self.session

    def __exit__(self, *exc_info):
        self.session.close()

class hn_transact(object):
    '''
    Context manager which begins and performs commits/rollbacks hibernate transactions.
    '''
    def __init__(self, session):
        self.tx = session.beginTransaction()

    def __enter__(self):
        return self.tx

    def __exit__(self, type, value, traceback):
        if type is None:
            self.tx.commit()
        else:
            self.tx.rollback()



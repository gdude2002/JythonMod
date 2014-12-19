__all__ = ["buildSessionFactory"]

import java.io.File as File
from org.hibernate import SessionFactory
from org.hibernate.cfg import AnnotationConfiguration
import config

def buildSessionFactory(*classes):
    '''
    Creates a new session factory.
    :param classes: peristence annotated classes which correspond to DB tables
    '''
    configuration = AnnotationConfiguration()
    for cls in classes:
        configuration.addAnnotatedClass(cls)
    c = configuration.configure(File(config.hibernate_cfg_xml))
    return c.buildSessionFactory()




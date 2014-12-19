import os
import sys
import jynx

__all__ = ["buildSessionFactory", "Serializable", "hn_session", "hn_transact", "bean_property"]

##############   logging? ############################################

LOGGING = False

sys.classpath.append(os.path.join(jynx.orgpath, "slf4j", "slf4j-api-1.5.8.jar"))

if LOGGING:
    sys.classpath.append(os.path.join(jynx.orgpath, "slf4j", "slf4j-simple-1.5.8.jar"))
else:
    sys.classpath.append(os.path.join(jynx.orgpath, "slf4j", "slf4j-nop-1.5.8.jar"))

##############   define system dependent root paths ##################

HIBERNATE_PATH      = r"c:\lang\Java\hibernate-3.3.2"

assert os.path.isdir(HIBERNATE_PATH), "Set HIBERNATE_PATH to the root directory of your Hibernate package"

HIBERNATE_ANNO_PATH = r"c:\lang\Java\hibernate-3.3.2"

assert os.path.isdir(HIBERNATE_ANNO_PATH), "Set HIBERNATE_ANNO_PATH to the root directory of your Hibernate Annotations package"

##############   define hibernate.cfg.xml   ##########################

hibernate_cfg_xml = os.path.join(jynx.jynxpath, "lib", "hibernate", "hibernate.cfg.xml")

##############   Database Settings    ############################

DB_PATH = r"c:\lang\Java\derby\lib"

assert os.path.isdir(DB_PATH), "Incorrect path to database packages. Set your own path."

##############   set database class paths  ################

sys.classpath.append(os.path.join(DB_PATH, "derby.jar"))
sys.classpath.append(os.path.join(DB_PATH, "derbytools.jar"))

##############   set hibernate class paths  ##########################

sys.classpath.append(os.path.join(HIBERNATE_PATH, "hibernate3.jar"))
sys.classpath.append(os.path.join(HIBERNATE_PATH, "hibernate-testing.jar"))
sys.classpath.append(os.path.join(HIBERNATE_ANNO_PATH, "hibernate-annotations.jar"))

sys.classpath.append(os.path.join(HIBERNATE_ANNO_PATH, "lib", "ejb3-persistence.jar"))
sys.classpath.append(os.path.join(HIBERNATE_ANNO_PATH, "lib", "hibernate-commons-annotations.jar"))
sys.classpath.append(os.path.join(HIBERNATE_PATH, "lib", "required", "commons-collections-3.1.jar"))
sys.classpath.append(os.path.join(HIBERNATE_PATH, "lib", "required", "jta-1.1.jar"))
sys.classpath.append(os.path.join(HIBERNATE_PATH, "lib", "required", "antlr-2.7.6.jar"))
sys.classpath.append(os.path.join(HIBERNATE_PATH, "lib", "dom4j.jar"))
sys.classpath.append(os.path.join(HIBERNATE_PATH, "lib", "bytecode", "javassist", "javassist-3.9.0.GA.jar"))




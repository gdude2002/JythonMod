##############   setting jynx on Java classpath   ################

import sys
import os

import sentinel
import jclasspath

jynxpath = os.path.dirname(sentinel.__file__)
basepath = os.path.dirname(jynxpath)
orgpath  = os.path.join(basepath, "org")
genpath  = os.path.join(orgpath, "jynx", "gen")

import java.lang.System

sys.classpath.append(basepath)
sys.classpath.append(orgpath)
sys.classpath.append(genpath)


##############   extending python path   #########################
if '"' in os.environ["JAVA_HOME"]:
    sys.path.append(os.path.join(os.environ["JAVA_HOME"][1:-1],"lib", "tools.jar"))
else:
    sys.path.append(os.path.join(os.environ["JAVA_HOME"],"lib", "tools.jar"))


##################################################################



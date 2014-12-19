import sys
import os
import urllib

from java.lang import ClassLoader

from java.net import URL

import sys

# operating system dependent classpath separators

import java.lang.System
classpathsep = java.lang.System.getProperty("path.separator")
classpath = java.lang.System.getProperty("java.class.path")
javahome  = java.lang.System.getProperty("java.home")



def pathname2url(pth):
    '''
    Transform file system path into URL using urllib.pathname2url().

    Additional changes:

    Undo replacement of ':' by '|' on WinNT. Append '/' to URLs stemming from directories.
    '''
    url = urllib.pathname2url(pth)
    if classpathsep == ";": # NT
        url = url.replace("|", ":", 1)
    if os.path.isdir(pth) and url[-1]!="/":
        url+="/"
    return url

class InstallationError(Exception):pass

class ClassPath(object):
    _instance = None
    def __init__(self):
        if ClassPath._instance:
            self.__dict__.update(ClassPath._instance.__dict__)
        else:
            if 'CLASSPATH' in os.environ:
                self._path = classpath.split(classpathsep)
            else:
                raise InstallationError("Cannot find CLASSPATH environmment variable")
            self._stdloader = ClassLoader.getSystemClassLoader()
            ClassPath._instance = self

    def append(self, pth):
        try:
            self._stdloader.addURL(URL("file:"+pathname2url(pth)))
        except AttributeError:
            raise InstallationError("Make sure that Jython registry file is in the directory of jython.jar\n"
                                    "                   Also set registry option 'python.security.respectJavaAccessibility' to false.")
        self._path.append(pth)
        sys.path.append(pth)

    def __repr__(self):
        return classpathsep.join(self._path)

# define new system variable
sys.classpath = ClassPath()




##############   setting jynx on Java classpath   ################
import sys
import os
import jynx
import java.io.StringBufferInputStream

sys.classpath.append(os.path.join(jynx.orgpath, "javaparser", "javaparser-1.0.7.jar"))

import japa.parser.JavaParser
import org.javaparser.TypeVisitor as TypeVisitor


def parse(string):
    inputstream = java.io.StringBufferInputStream(string)
    return japa.parser.JavaParser.parse(inputstream)

class ImportData(object):
    def __init__(self, path, asterisk):
        self.path = path
        self.asterisk = asterisk
        if asterisk:
            self.package = path
            self.module  = ""
        else:
            k = path.rfind(".")
            if k>0:
                self.package, self.module = path[:k], path[k+1:]

    def __repr__(self):
        if self.module:
            return "ImportData<%s, %s, %s>"%(self.package, self.module, self.asterisk)
        else:
            return "ImportData<%s, %s>"%(self.package, self.asterisk)

def package_name(T):
    name = T.__module__
    return (name if not name.startswith("[L") else name[2:])

def module_name(T):
    name = T.__name__
    return (name if not name[-1] == ";" else name[:-1])


class ImportFinder(object):
    javalang = set(dir(java.lang))
    def __init__(self, cls, code):
        self.cu = parse(code)
        self.cls = cls
        self.readImported()

    def readImported(self):
        self.imported = {}
        m = sys.modules[package_name(self.cls)]
        for key, T in m.__dict__.items():
            if isinstance(T, java.lang.Class):
                pkg_name = package_name(T)
                if pkg_name == "__builtin__":
                    continue
                self.imported[key] = pkg_name+"."+module_name(T)


    def getTypeNames(self):
        tv = TypeVisitor()
        tv.visit(self.cu, None)
        names = set()
        for n in set(map(str, tv.getNodes())):
            k = max(n.find("<"),n.find("["))
            if k>=0:
                names.add(n[:k])
            else:
                names.add(n)
        return names

    def getImportStatements(self):
        imports = []
        for item in [] if not self.cu.imports else self.cu.imports:
            imports.append(ImportData(str(item.name), item.asterisk))
        return imports

    def missingTypes(self):
        missing  = set()
        modules  = set([imdata.module for imdata in self.getImportStatements() if imdata.module])
        packages = set([imdata.package for imdata in self.getImportStatements() if imdata.asterisk])
        for pkg in packages:
            try:
                modules.update(dir(__import__(pkg, fromlist=[""])))
            except ImportError:
                pass
        for name in self.getTypeNames():
            if not (name in ImportFinder.javalang or name in modules):
                missing.add(name)
        return missing

    def findPackages(self):
        missing  = set()
        packages = set()
        for m in self.missingTypes():
            if m in self.imported:
                packages.add(self.imported[m])
            else:
                missing.add(m)
        return packages, missing



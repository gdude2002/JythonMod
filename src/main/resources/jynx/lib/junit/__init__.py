import sys
import os
import traceback

import jynx

junitpath = os.path.join(jynx.orgpath, "junit", "junit-4.6.jar")
sys.classpath.append(junitpath)

from org.junit import*
from org.junit.Assert import*
from org.junit.runner.notification import RunListener
import org.junit.runner.JUnitCore as JUnitCore

from jynx.jannotations import annotation, signature, jproperty
import time

class Reporter(RunListener):
    def __init__(self):
        self.fail = False
        self.cnt  = 0

    def testRunStarted(self, descr):
        self.t0 = time.time()

    def testStarted(self, descr):
        self.fail = False
        self.cnt += 1

    def testFinished(self, descr):
        if self.fail:
            print str(descr)+" ... FAIL"
        else:
            print str(descr)+" ... ok"

    def testFailure(self, failure):
        self.fail = True

    def testRunFinished(self, descr):
        t1 = time.time()
        print
        T = "%f"%(t1-self.t0)
        k = T.find(".")
        print "----------------------------------------------------------------------"
        if self.cnt!=1:
            print "Ran %s tests in %ss"%(self.cnt, T[:k+4])
        else:
            print "Ran %s test in %ss"%(self.cnt, T[:k+4])



def runClasses(*testclass):
    '''
    Testrunner which
    '''
    core = JUnitCore()
    core.addListener(Reporter())
    result = core.run(testclass)
    n = result.getFailureCount()
    if n:
        print
        print "There were %s failures:\n"%n
        for i, F in enumerate(result.getFailures()):
            exc = F.getException()
            try:
                file, line, funcName, lineContent = traceback.extract_tb(exc.traceback)[0]
                print "   %s) %s"%(i+1,F.getDescription())
                print
                print "      %s"%'      '.join([s for s in str(exc.cause).split("\n") if s])
                print "      ..."
                print "      "+lineContent
                print "      ..."
                print "      at %s : %s"%(file, line)
                print
                print
            except AttributeError:
                print exc


# define decorator valued Jython annotations
Test   = annotation.extract(Test)(signature("public void _()"))
After  = annotation.extract(After)(signature("public void _()"))
Before = annotation.extract(Before)(signature("public void _()"))
BeforeClass = annotation.extract(BeforeClass)(signature("public static void _()"))
AfterClass  = annotation.extract(AfterClass)(signature("public static void _()"))
Ignore = annotation.extract(Ignore)




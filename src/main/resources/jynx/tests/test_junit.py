from jynx.lib.junit import*
from java.lang import Object
from jynx.jannotations import JavaClass

@JavaClass
class TestClass(Object):

    x = jproperty("private static int")

    @BeforeClass
    def once(cls):
        print "\nRun 'TestClass' tests ..."
        print "----------------------------------------------------"
        print "This JUnit test tests the use of JUnit."
        print
        print "It will check JUnit 4 annotations and it reports"
        print "two faiures which have to confirmed manually"
        print "----------------------------------------------------"


    @Test
    def test_report_test_failure(self):
        assertTrue("length of empty list is 0", len([]) != 0)

    @Test
    def test_report_exception(self):
        1/0
        assertTrue("length of empty list is not 0", len([]) == 0)

    @Test() # parentheses are optional
    def test_good_case(self):
        assertTrue(True)

    @signature("public int x(char, String)")
    def something_else(self, a, b):
        pass

    @signature("public static int _(short, String)")
    def check_signature(self, a, b):
        pass

    @Before
    def setUp(self):
        print "run before test..."

    @signature("public int _(int)")
    def foo(self, y):
        return self.x + y


if __name__ == '__main__':
    runClasses(TestClass)









import jynx
from jynx.lib.junit import*
from java.lang import Object
from jynx.jannotations import JavaClass, JavaCompiler


@JavaClass
class TestClass(Object):
    @Before
    def define_classes(self):
        self.Foo_code = '''
        public class Foo {
            public static String greeting;

            public static void main(String args[])
            {
                greeting = "Hello "+args[0];
            }
        }'''

        self.Prime_code = '''
        import java.lang.Math;
        public class Prime {

            public static Boolean isPrime(double n)
            {

                for(int d=2;d<=Math.sqrt(n);d++)
                {
                    if(n%d == 0)
                        return false;
                }
                return true;
            }
        }'''

        self.TestPrime_code = '''

        import org.jynx.gen.Prime;

        public class TestPrime {

            public static Boolean primeTest(int num)
            {
                return Prime.isPrime(9973);
            }
        }'''


    @Test
    def test_compile_simple_class(self):
        Foo = JavaCompiler().createClass("Foo", self.Foo_code)
        Foo.main(["Jython!"])
        assertTrue(Foo.greeting == "Hello Jython!")

    @Test
    def test_subclass_dynamic(self):
        Foo = JavaCompiler().createClass("Foo", self.Foo_code)
        class Bar(Foo):
            pass
        assertTrue(issubclass(Bar, Foo))

    @Test
    def test_store_module(self):
        JavaCompiler(store=True).createClass("Prime", self.Prime_code)
        prime_class = os.path.join(jynx.genpath, "Prime.class")
        assertTrue(os.path.isfile(prime_class))
        import org.jynx.gen.Prime as Prime
        assertTrue(Prime.isPrime(79)==True)
        os.remove(os.path.join(jynx.genpath, "Prime.class"))

    @Test
    def test_load_dynamically_stored(self):
        JavaCompiler(store=True).createClass("Prime", self.Prime_code)
        prime_class = os.path.join(jynx.genpath, "Prime.class")
        TestPrime = JavaCompiler().createClass("TestPrime", self.TestPrime_code)
        assertTrue(TestPrime.primeTest(79) == True)
        os.remove(prime_class)

if __name__ == '__main__':
    runClasses(TestClass)









from java.lang import Override, Object
from java.util import List
from javax.lang.model import SourceVersion
from javax.annotation.processing import SupportedAnnotationTypes
from javax.annotation.processing import SupportedSourceVersion
from javax.annotation.processing import AbstractProcessor
from java.lang.annotation import Retention

from jynx.jannotations import*
from jynx.lib.junit import*

SupportedAnnotationTypes = annotation.extract(SupportedAnnotationTypes)
SupportedSourceVersion   = annotation.extract(SupportedSourceVersion)
Override = annotation.extract(Override)

@JavaClass
@SupportedAnnotationTypes(value = "*")
@SupportedSourceVersion(value = SourceVersion.RELEASE_6)
class CodeAnalyzer(AbstractProcessor):

    elements = jproperty("private List")

    @classmethod
    @signature("String _()")
    def bar(cls):
        return "bar"

    def foo(self, y):
        return str(self.x)+y

    x = jproperty("private char")
    @signature("List _()")
    # @signature("String _()")
    def bar2(cls):
        return "bar"

    @Override
    def process(self, annotations, roundEnvironment):
        for e in roundEnvironment.getRootElements():
            self.elements.append("Element is "+ str(e.getSimpleName()))
        return True


@JavaClass
class TestAnnotationsProcessor(Object):

    @Test
    def test_create_analyzer(self):
        analyzer = CodeAnalyzer()
        analyzer.x = 'x'
        assertTrue(analyzer.foo('y') == "xy")
        assertTrue(analyzer.bar() == "bar")

    @Test
    def test_run_analyzer(self):
        analyzer = CodeAnalyzer()
        analyzer.elements = []
        code = '''
        import org.junit.*;

        public class Foo {
            @Test public void tst(){}
        }
        '''
        JavaCompiler(processors = [analyzer]).createClass("Foo", code)
        assertTrue(analyzer.elements[0] == "Element is Foo")

@JavaClass
class TestAnnotationsGeneration(Object):
    "Field types are restricted to primitives, String, Class, enums, annotations, and arrays of the preceding types."
    annotations = {}

    @BeforeClass
    def createAnnotations(cls):
        code_A = '''
        import java.lang.annotation.*;
        @Retention(RetentionPolicy.RUNTIME)
        public @interface A {
           String field();
        }'''
        A = JavaCompiler(store=True).createAnnotation("A", code_A)
        cls.annotations["A"] = A

        code_B = '''
        public @interface B {
           A[] a();
           String name();
        }'''
        B = JavaCompiler(store=True).createAnnotation("B", code_B)
        cls.annotations["B"] = B

        code_C = '''
        import java.lang.annotation.*;
        @Retention(RetentionPolicy.RUNTIME)
        public @interface C {
            int x() default 7;
            B[] value();
            String name();
        }'''
        C = JavaCompiler(store=True).createAnnotation("C", code_C)
        cls.annotations["C"] = C


    @Test
    def test_nested_annotation_1(self):
        annotations = self.__class__.annotations
        A, B, C = [annotations[X] for X in "ABC"]
        anno_a1 = A(field = "1")
        anno_a2 = A(field = "2")
        anno_a3 = A(field = "3")
        anno_b1 = B(a = [anno_a1, anno_a2])
        assertTrue(''.join(str(anno_b1).split()) == '@B(a={@A(field="1"),@A(field="2")})')
        anno_b2 = B(a = [anno_a3])
        anno_c1 = C(value = [anno_b1, anno_b2])
        assertTrue(''.join(str(anno_c1).split()) == '@C(value={@B(a={@A(field="1"),@A(field="2")}),@B(a={@A(field="3")})})')

    @Test
    def test_nested_annotation_2(self):
        annotations = self.__class__.annotations
        A, B, C = [annotations[X] for X in "ABC"]
        c = C(value = [B(a = A(field = "f1"), name = "a1"),
                   B(name = "n", a = A(field = "a2"))],
              x = 45,
              name = "c")

        @JavaClass(store = True)
        @c
        class D(Object):
            x = jproperty("int")

            @A(field = "!")
            def foo(self):
                pass
        assertTrue(getAnnotations(D)[0].annotationType() == C.getAnnotation())


runClasses(TestAnnotationsProcessor,
           TestAnnotationsGeneration)






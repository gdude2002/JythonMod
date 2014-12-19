from jynx.lib.javaparser import parse
from jynx.lib.junit import*
from jynx.jannotations import*

import java.lang.Object as Object
import java.util.Vector as Vector
from japa.parser.ast.type import*
import japa.parser.ast.visitor.VoidVisitorAdapter as VoidVisitorAdapter
import japa.parser.ast.Node as Node
import japa.parser.ast.TypeParameter as TypeParameter
from japa.parser.ast.expr import*
from java.lang import Override

Override = annotation.extract(Override)

@JavaClass
class TypeVisitor(VoidVisitorAdapter):
    nodes = jproperty("Vector", initializer = "new Vector()")

    @signature("public Vector _()")
    def getNodes(self):
        return self.nodes

    @Override
    @signature("public void _(ReferenceType, Object)", overload = True)
    def visit(self, n, arg):
        self.nodes.add(n)

    @Override
    @signature("public void visit(TypeParameter, Object)", overload = True)
    def visit(self, n, arg):
        self.nodes.add(n)

    @Override
    @signature("public void visit(WildcardType, Object)", overload = True)
    def visit(self, n, arg):
        self.nodes.add(n)

    @Override
    @signature("public void visit(ClassOrInterfaceType, Object)", overload = True)
    def visit(self, n, arg):
        VoidVisitorAdapter.visit(self,n, arg)  # super ???
        self.nodes.add(n)

@JavaClass
class AnnotationVisitor(VoidVisitorAdapter):
    nodes = jproperty("Vector", initializer = "new Vector()")

    @signature("public Vector _()")
    def getNodes(self):
        return self.nodes

    @Override
    @signature("public void _(MarkerAnnotationExpr, Object)", overload = True)
    def visit(self, n, arg):
        self.nodes.add(n)

@JavaClass
class TestParser(Object):
    @Test
    def test_type_visitor(self):
        cu = parse(TypeVisitor.java_source)
        tv = TypeVisitor()
        tv.visit(cu, None)
        assertTrue(ReferenceType in [type(n) for n in tv.getNodes()])
        names = [str(node) for node in tv.getNodes()]
        assertTrue("VoidVisitorAdapter" in names)
        assertTrue("PyObject" in names)
        assertTrue("WildcardType" in names)

    @Test
    def test_annotation_visitor(self):
        cu = parse(TypeVisitor.java_source)
        av = AnnotationVisitor()
        av.visit(cu, None)
        assertTrue(str(av.getNodes()[0]) == "@Override")

    @Test
    def test_multimethod(self):
        assertTrue(hasattr(TypeVisitor().jyobject, "visit__0"))
        assertTrue(hasattr(TypeVisitor().jyobject, "visit__3"))


runClasses(TestParser)


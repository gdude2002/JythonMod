package org.javaparser;

import java.util.Vector;
import japa.parser.ast.TypeParameter;
import japa.parser.ast.type.*;
import japa.parser.ast.visitor.VoidVisitorAdapter;
import japa.parser.ast.Node;

class TypeVisitor extends VoidVisitorAdapter {
    Vector<Node> nodes = new Vector<Node>();

    public Vector<Node> getNodes()
    {
        return nodes;
    }

    @Override
    public void visit(ReferenceType n, Object arg) {
        super.visit(n, arg);
        nodes.add(n);
    }

    @Override
    public void visit(TypeParameter n, Object arg) {
        nodes.add(n);
    }

    @Override
    public void visit(WildcardType n, Object arg) {
        nodes.add(n);
    }

    @Override
    public void visit(ClassOrInterfaceType n, Object arg) {
        super.visit(n, arg);
        nodes.add(n);
    }
}


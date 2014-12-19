from __future__ import with_statement

from jynx.lib.junit import*
from java.lang import Object
from jynx.jannotations import JavaClass
from jynx.lib.hibernate import*
from jynx.jcompile import JavaCompiler

import java.io.Serializable as Serializable

@Entity
class Course(Serializable):
    @Id
    @Column(name="COURSE_ID")
    @bean_property("int")
    def courseId(self): pass

    @Column(name="COURSE_NAME", nullable = False, length=50)
    @bean_property("String")
    def courseName(self): pass



@Entity #(display=True)
class Heart(Serializable):
    @Id
    @bean_property(int)
    def id(self):pass

@Entity
class Body(Serializable):
    @Id
    @bean_property(int)
    def id(self):pass

    @OneToOne(cascade = CascadeType.ALL)
    @PrimaryKeyJoinColumn
    @bean_property(Heart)
    def heart(self):pass

@JavaClass
class OneToOneTest(Object):
    @Test
    def testUnidirectionalTrueOneToOne(self):

        with hn_session(Heart, Body) as session:
            body = Body()
            heart = Heart()
            body.heart = heart
            body.id = 1
            heart.id = body.id
            with hn_transact(session):
                session.saveOrUpdate(body)
                session.saveOrUpdate(heart)

        with hn_session(Heart, Body) as session:
            with hn_transact(session):
                body, heart = session.createQuery("from Body as body join body.heart as heart").list()[0].tolist()
                assertTrue(body.id == heart.id)
                b = session.get(Body, 1)
                assertTrue(b!=None)
                assertTrue(b.heart!=None)
                assertTrue(b.heart.id == 1)


if __name__ == '__main__':
    runClasses(OneToOneTest)




from __future__ import with_statement

from jynx.lib.junit import*
from java.lang import Object
from jynx.jannotations import JavaClass
from jynx.lib.hibernate import*
from jynx.jcompile import JavaCompiler


@Entity #(display = True)
@hn_anno.Table(appliesTo = "foo")
@Table(name = "foox")
class Zeta(Serializable):
    pass

@JavaClass
class TestAnnoExtension(Object):
    @Test
    def checkTwoTables(self):
        assertTrue(Zeta.java_source.find('@Table')>0)
        assertTrue(Zeta.java_source.find('@org.hibernate.annotations.Table')>0)


if __name__ == '__main__':
    runClasses(TestAnnoExtension)




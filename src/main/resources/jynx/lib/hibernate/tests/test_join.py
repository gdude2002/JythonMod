from __future__ import with_statement

from jynx.lib.junit import*
from java.lang import Object
from jynx.jannotations import JavaClass
from jynx.lib.hibernate import*
from jynx.jcompile import JavaCompiler

import java.io.Serializable as Serializable

import java.lang.Integer as Integer
import java.util.Date as Date
import org.hibernate.criterion.Expression as Expression

Table = hn_anno.Table

p_string = bean_property("String")
p_int    = bean_property(Integer)

@Entity #(display = True)
class Employee(Serializable):
    @Id
    @bean_property("String")
    def name(_):pass

    @bean_property(int)
    @Column(name = "DepartmentId")
    def id(_):pass

@Entity
class Department(Serializable):
    @bean_property("String")
    def name(_):pass

    @Id
    @bean_property(int)
    @Column(name = "DepartmentId")
    def id(_):pass


@MappedSuperclass
class A(Object):
    @Column(nullable = False)
    @bean_property(Date)
    def createDate(_):pass

@Entity
@Inheritance( strategy = InheritanceType.SINGLE_TABLE )
class B(A):
    @Id
    @GeneratedValue
    @p_int
    def id(_):pass

    @Column(nullable = False)
    @p_string
    def name(_):pass

@Entity
@DiscriminatorValue("C")
@SecondaryTable(name="C")
class C(B):
    @Column(table = "C")
    @p_int
    def age(_):pass



@Entity
@SecondaryTables((
    SecondaryTable(name = "`Cat nbr1`"),
    SecondaryTable(name = "Cat2", uniqueConstraints = [UniqueConstraint(columnNames = ["storyPart2"])])
        ))
@Tables( (
    Table(appliesTo = "Cat", indexes = Index(name = "secondname",
            columnNames = "secondName"), comment = "My cat table" ),
    Table(appliesTo = "Cat2", foreignKey = ForeignKey(name="FK_CAT2_CAT"), fetch = FetchMode.SELECT,
            sqlInsert=SQLInsert(sql="insert into Cat2(storyPart2, id) values(upper(?), ?)") )
            ) )
class Cat(Serializable):
    @Id
    @GeneratedValue
    @p_int
    def id(_):pass

    @Index(name = "nameindex")
    @p_string
    def name(_):pass

    @p_string
    def secondName(_):pass

    @Column(table = "`Cat nbr1`")
    @Index(name = "story1index")
    @p_string
    def storyPart1(_):pass

    @Column(table = "Cat2", nullable = False)
    @p_string
    def storyPart2(_):pass


@Entity
@SecondaryTable(
        name = "ExtendedDeath",
        pkJoinColumns = PrimaryKeyJoinColumn(name = "DEATH_ID")
)
class Death(Serializable):
    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    @p_int
    def id(_):pass

    @Column(name = "death_date")
    @bean_property(Date)
    def date(_):pass

    @Column(table = "ExtendedDeath")
    @p_string
    def howDoesItHappen(_):pass


@Entity
@SecondaryTable(name = "ExtendedLife")
class Life(Serializable):
    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    @Column(name = "LIFE_ID")
    @p_int
    def id(_):pass

    duration = jproperty("int")

    @Column(table = "ExtendedLife")
    @p_string
    def fullDescription(_):pass

    @ManyToOne(cascade = (CascadeType.PERSIST, CascadeType.MERGE))
    @JoinColumn(name = "CAT_ID", table = "ExtendedLife")
    @bean_property(Cat)
    def owner(_):_


@Embeddable
class DogPk(Serializable):
    name = jproperty("String")
    ownerName = jproperty("String")

    @signature("boolean _(Object)")
    def equals(self, o):
        if id(self) == id(o): return True
        try:
            return self.name == o.name and self.ownerName == o.ownerName
        except AttributeError:
            return False


    @signature("int _()")
    def hashCode(self):
        result = self.name.hashCode()
        result = 29 * result + self.ownerName.hashCode()
        return result


@Entity
@SecondaryTable(
        name = "DogThoroughbred",
        pkJoinColumns = [PrimaryKeyJoinColumn(name = "NAME", referencedColumnName = "name"),
                         PrimaryKeyJoinColumn(name = "OWNER_NAME", referencedColumnName = "ownerName")]
)
class Dog(Object):
    @Id
    @bean_property(DogPk)
    def id(_):_

    weight = jproperty("Integer")

    @Column(table = "DogThoroughbred")
    @p_string
    def thoroughbredName(_):_

    @signature("boolean _(Object)")
    def equals(self, o):
        if id(self) == id(o): return True
        try:
            return self.id == o.id
        except AttributeError:
            return False

    @signature("int _()")
    def hashCode(self):
        return id(self.id)



@JavaClass
class TestJoin(Object):
    @Test
    def testCompositePK(self):
        with hn_session(Dog) as session:
            dog  = Dog()
            dog_pk = DogPk()
            dog_pk.name = "Bomber";
            dog_pk.ownerName = "Geekgirl";
            dog.id = dog_pk;
            dog.weight = 62;
            dog.thoroughbredName = "Mastino";

            with hn_transact(session):
                session.saveOrUpdate( dog )

        with hn_session(Dog) as session:
            with hn_transact(session):
                q = session.createQuery( "from Dog" )
                dog = q.uniqueResult()
                assertEquals( "Mastino", dog.thoroughbredName )
                session.delete(dog)
    @Test
    def testExplicitValue(self):
        with hn_session(Death) as session:
            with hn_transact(session):
                death = Death()
                death.date = Date()
                death.howDoesItHappen = "Well, haven't seen it"
                session.saveOrUpdate(death)
        with hn_session(Death) as session:
            with hn_transact(session):
                q = session.createQuery( "from " + Death.__name__ )
                death = q.uniqueResult()
                assertEquals( "Well, haven't seen it", death.howDoesItHappen )
                session.delete( death )

    @Test
    def testManyToOne(self):

        with hn_session(Life, Cat) as session:
            with hn_transact(session):
                life = Life()
                cat = Cat()
                cat.name = "kitty"
                cat.storyPart2 = "and the story continues"
                life.duration = 15
                life.fullDescription = "Long long description"
                life.owner = cat
                session.saveOrUpdate( cat )
                session.saveOrUpdate( life )

        with hn_session(Life, Cat) as session:
            with hn_transact(session):
                crit = session.createCriteria( Life )
                crit.createCriteria( "owner" ).add( Expression.eq( "name", "kitty" ) )
                life = crit.uniqueResult()
                assertEquals( "Long long description", life.fullDescription );
                session.delete( life.owner )
                session.delete( life );

        with hn_session(C) as s:
            s.getTransaction().begin()
            try:
                c = C()
                c.age = 12
                c.createDate = Date()
                c.name = "Bob"
                s.saveOrUpdate( c )
                s.flush()
                s.clear()
                c = s.get( C, c.id )
                assertNotNull( c.createDate )
                assertNotNull( c.name )
            finally:
                s.getTransaction().rollback()

if __name__ == '__main__':
    runClasses(TestJoin)




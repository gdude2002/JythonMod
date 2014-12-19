from __future__ import with_statement

from jynx.lib.junit import*
from java.lang import Object
from jynx.jannotations import JavaClass
from jynx.lib.hibernate import*
from jynx.jcompile import JavaCompiler

import java.io.Serializable as Serializable

import java.util.Map as Map
import java.util.SortedMap as SortedMap
import java.util.TreeMap as TreeMap
import java.lang.Integer as Integer

import org.hibernate.annotations as hiberanno
from org.hibernate.id import IdentifierGenerator

CollectionOfElements = annotation.extract(hiberanno.CollectionOfElements)
Type     = annotation.extract(hiberanno.Type)
Sort     = annotation.extract(hiberanno.Sort)
MapKey   = annotation.extract(hiberanno.MapKey)
SortType = hiberanno.SortType
GenericGenerator = annotation.extract(hiberanno.GenericGenerator)


@JavaClass(store = True)
class PrimeGenerator(IdentifierGenerator):

    def __init__(self):
        self.prime_source = self.prime_sieve()
        self.primes = []

    def prime_sieve(self):
        n = (self.primes[-1] if self.primes else 1)
        if n == 1:
            yield 2
        if n%2 == 0:
            n+=1
        else:
            n+=2
        while True:
            for p in self.primes:
                if n%p == 0:
                    n+=2
                    break
            else:
                self.primes.add(n)
                yield n
                n+=2

    def generate(self, session, obj):
        if not self.primes:
            self.primes = session.createQuery("select p.id from Person p").list()
        return self.prime_source.next()


@Entity
class AddressType(Serializable):

    @Id
    @GeneratedValue
    @bean_property("Integer")
    def id(self): pass

    @bean_property("String")
    def name(self): pass

@Embeddable
class Country(Serializable):
    @bean_property("String")
    def iso2(self):pass

    @Column(name = "countryName")
    @bean_property("String")
    def name(self):pass


@Embeddable
class Address(Serializable):
    @bean_property("String")
    def address1(_):pass

    @bean_property("Country")
    def country(_): pass

    @Column(name = "fld_city")
    @bean_property("String")
    def city(self): pass

    @ManyToOne
    @bean_property(AddressType)
    def type(self): pass



@Entity
@Table(name = "PersonEmbed")
class Person(Serializable):
    @Id
    @GenericGenerator(name="seq_id", strategy="org.jynx.gen.PrimeGenerator")
    @GeneratedValue(generator="seq_id")
    @bean_property("Integer")
    def id(_):pass

    name = jproperty("String")

    @Embedded
    @bean_property("Address")
    def address(_): pass

    @Embedded
    @AttributeOverrides((
        AttributeOverride(name = "iso2", column = Column(name = "bornIso2")),
        AttributeOverride(name = "name", column = Column(name = "bornCountryName"))
            ))
    @bean_property("Country")
    def bornIn(self): pass

@Embeddable
class FootballerPk(Serializable):
    @bean_property("String")
    def firstname(_):pass

    @bean_property("String")
    def lastname(_):pass

    @signature("boolean _(Object)")
    def equals(self, other):
        if isinstance(other, FootballerPk):
            return self.firstname == other.firstname and self.lastname == other.lastname
        return False

    @signature("int _()")
    def hashCode(self):
        return id(self.firstname) + id(self.lastname)

@Entity
@IdClass(value = FootballerPk)
class Footballer(Serializable):
    @Id
    @bean_property("String")
    def firstname(_):pass

    @Id
    @bean_property("String")
    def lastname(_):pass

    @bean_property("String")
    def club(_):pass

    @signature("boolean _(Object)")
    def equals(self, other):
        if isinstance(other, FootballerPk):
            return self.firstname == other.firstname and \
                   self.lastname == other.lastname and \
                   self.club == other.club
        return False

    @signature("int _()")
    def hashCode(self):
        return id(self.firstname) + id(self.lastname)+ id(self.club)




@JavaClass
class TestEmbedded(Object):
    @Test
    def testEmbedding(self):

        with hn_session(AddressType, Person) as session:
            p = Person()
            a = Address()
            c = Country()
            bornCountry = Country()
            c.iso2 = "DM"
            c.name = "Matt Damon Land"
            bornCountry.iso2 = "US"
            bornCountry.name = "United States of America"
            a.address1 = "colorado street"
            a.city = "Springfield"
            a.country = c
            p.address = a
            p.bornIn = bornCountry
            p.name = "Homer"

            with hn_transact(session):
                session.saveOrUpdate(p)

        with hn_session(Person, AddressType) as session:
            with hn_transact(session):
                p = session.get( Person, p.id )
                assertNotNull( p )
                assertNotNull( p.address )
                assertEquals( "Springfield", p.address.city )
                assertNotNull( p.address.country )
                assertEquals( "DM", p.address.country.getIso2() )
                assertNotNull( p.bornIn );
                assertEquals( "US", p.bornIn.getIso2() )


if __name__ == '__main__':
    runClasses(TestEmbedded)




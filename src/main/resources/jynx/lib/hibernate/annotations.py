import sys
import jynx

__all__ = ["bean_property", "hn_anno"]

import config
import javax.persistence
import java.lang.annotation.Annotation
import org.hibernate.annotations
from jynx.jannotations import*
import jynx.jannotations

class annotation_gen_ext(jynx.jannotations.annotation_gen):
    def new_annotation(self, arg = ''):
        return annotation_ext(self.anno, arg)

class annotation_ext(annotation):
    def anno_repr(self):
        return type_name(self.anno)+self.arg

    @classmethod
    def new_anno_generator(self, anno):
        return annotation_gen_ext(anno)


G = globals()

persistence = set(dir(javax.persistence))

class ExtensionAnno(object): pass

hn_anno = ExtensionAnno()

def set_global_anno(G, name, pkg):
    val = getattr(pkg, name)
    if isinstance(val, type):
        if issubclass(val, java.lang.annotation.Annotation):
            G[name] = annotation.extract(val)
        else:
            G[name] = val
        __all__.append(name)

def set_hn_anno(hn_anno, name, anno_cls = annotation):
    val = getattr(org.hibernate.annotations, name)
    if isinstance(val, type):
        if issubclass(val, java.lang.annotation.Annotation):
            setattr(hn_anno, name, anno_cls.extract(val))
        else:
            setattr(hn_anno, name, val)

for name in persistence:
    set_global_anno(G, name, javax.persistence)

for name in dir(org.hibernate.annotations):
    if name in persistence:
        set_hn_anno(hn_anno, name, annotation_ext)
    else:
        set_hn_anno(hn_anno, name)
        set_global_anno(G, name, org.hibernate.annotations)

def makeHnBeanTranslator(annotation):
    def TranslationDecorator(cls=None, **kwd):
        '''
        Entity decorator. Full replacement for JavaClass decorator for Entity Beans.
        '''
        kwd["store"]=True
        kwd["jaobject_annotation"]="@Transient"
        kwd["jyobject_annotation"]="@Transient"
        kwd["pkg"] = ["javax.persistence.Transient"]
        if cls:
            jmaker = JavaClassMaker(**kwd)
            jmaker.annotations.append(annotation)
            return jmaker(cls)
        else:
            jmaker = JavaClassMaker(**kwd)
            jmaker.annotations.append(annotation)
            return jmaker
    TranslationDecorator.__name__ = annotation.getAnnotation().__name__
    return TranslationDecorator

Entity = makeHnBeanTranslator(Entity)
Embeddable = makeHnBeanTranslator(Embeddable)
MappedSuperclass = makeHnBeanTranslator(MappedSuperclass)





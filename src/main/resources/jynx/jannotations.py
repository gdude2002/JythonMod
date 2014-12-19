import sys

import java.lang.Class
import org.python.core.PyReflectedFunction as reflectedfunction
import org.python.core.PyReflectedField as reflectedfield
import java.lang.reflect.Field as Field
import java.lang.reflect.Method as Method
import java.lang.annotation.Annotation as JavaAnnotation

from java.lang import*
from jcompile import*
from org.jynx import JyGateway
from jynx.lib.javaparser import ImportFinder

__all__ = ["jproperty",
           "JavaCompiler",
           "signature",
           "annotation",
           "JavaClass",
           "JavaClassMaker",
           "type_name",
           "module_name",
           "package_name",
           "createJavaAnnotation",
           "getAnnotations",
           "bean_property"]


javakwds = set(['void','boolean','char','byte','short','int','long','float','double','public',
     'public','protected','private','static','abstract','final','native','synchronized',
     'transient','volatile','strictfp'])

primtype = {"int": "Integer",
            "char": "Character",
            "double": "Double",
            "byte": "Byte",
            "long": "Long",
            "short": "Short",
            "boolean": "Boolean",
            "float": "Float"}


def find_constructors(cls):
    for C in cls.mro():
        if hasattr(C, "getDeclaredConstructors"):
            return C.getDeclaredConstructors()
    return []

def package_name(T):
    name = T.__module__.replace("$", ".")
    return name if not name.startswith("[L") else name[2:]

def isList(T):
    if T.__module__.startswith("[L"):
        return True
    return False


def module_name(T):
    name = T.__name__.replace("$", ".")
    return (name if not name[-1] == ";" else name[:-1])


def type_name(T):
    try:
        pkg = package_name(T)
    except AttributeError:
        pkg = ""
    if pkg:
        return pkg+"."+module_name(T)
    else:
        return module_name(T)


class TypeExtractor(object):
    modules = {}
    blacklist = ["org.python.proxies", "__builtin__"]
    def __init__(self):
        self.classes = set()

    def extract(self, obj, takelast = True):
        '''
        Extract type info from type data.
        '''
        if isinstance(obj, type):
            if issubclass(obj, java.lang.Object):
                name = type_name(obj)
            else:
                return self
        elif isinstance(obj, str):
            if " " in obj:
                name = obj.split(" ")[-1]
            else:
                name = obj
        else:
            raise ValueError("No type or type name")
        if "." in name:
            k = name.rfind(".")
            pre, post = name[:k], name[k+1:]
            if name not in self.blacklist and pre not in self.blacklist:
                S = self.modules.get(post, set())
                if S:
                    if name not in S:
                        self.classes.add(pre+".*")
                    elif takelast:
                        self.classes.add(name)
                    else:
                        self.classes.add(pre)
                elif takelast:
                    self.classes.add(name)
                else:
                    self.classes.add(pre)
                S.add(name)
                self.modules[post] = S
        return self


class jproperty(object):
    def __init__(self, type_info, transfer = None, initializer = None, **kwd):
        self.type_info   = type_info
        self.annotation  = []
        self.initializer = initializer
        if transfer:
            try:
                self.annotation = transfer.java_annotations[:]
                transfer.java_annotations = []
            except AttributeError:
                pass
        self._name = ''

    def get_name(self, obj):
        if not self._name:
            for name, item in obj.__class__.__dict__.items():
                if item == self:
                    self._name = name
                    break
            else:
                raise AttributeError("Cannot access property value of %s"%self)
        return self._name

    def __get__(self, obj, objtype = None):
        name = self.get_name(obj)
        return getattr(obj.javaobj, name)

    def __set__(self, obj, value):
        name = self.get_name(obj)
        setattr(obj.javaobj, name, value)


def find_base_class(cls):
    for C in cls.mro()[1:]:
        if "org.python.proxies" in C.__module__:
            continue
        if hasattr(C, "isInterface"):
            return C
    else:
        raise ValueError("Cannot create Java class from Jython class '%s'"%cls.__name__)


class Translator(object):
    blacklist = ["org.python.proxies", "__builtin__"]
    def __init__(self, cls, **kwd):
        self.cls = cls
        self.module   = sys.modules[cls.__dict__["__module__"]]
        self.packages = set()
        self.imports  = []
        self.options  = kwd

    def get_all_classes(self):
        for name, value in self.module.__dict__.items():
            if issubclass(type(value), java.lang.Class):
                for C in TypeExtractor().extract(value).classes:
                    self.packages.add("import "+C+";")

    def extract_name(self, T):
        self.packages.add("import "+package_name(T)+"."+module_name(T)+";")

    def extract_package(self, pkg, takelast = True):
        if "." in pkg:
            k = pkg.rfind(".")
            pre, post = pkg[:k], pkg[k+1:]
            if pre == "__builtin__":
                return ''
            if pkg not in self.blacklist and pre not in self.blacklist:
                if takelast:
                    self.packages.add("import "+pkg+";")
                else:
                    self.packages.add("import "+pre+";")
            return post
        return pkg

    def extract_method(self, method, annotations):
        try:
            D = method.argslist[0].data
            data = str(method.argslist[0].data)
        except AttributeError:
            data = str(method)
            D = None
        K = data.find("(")
        head, args = data[:K], data[K:]
        head_splitted = head.split()
        if "abstract" in head_splitted:
            head_splitted.remove("abstract")
        elif "native" in head_splitted:
            head_splitted.remove("native")

        if len(head_splitted)>2:
            funcname    = head_splitted[-1]
            return_type = head_splitted[-2]
            prefix = head_splitted[:-2]
        elif head_splitted[0] in ("public", "private", "protected"):
            funcname = head_splitted[-1]
            prefix   = [head_splitted[0]]
            return_type = ''
        else:
            funcname    = head_splitted[-1]
            return_type = head_splitted[-2]
            prefix = ["public"]
        if D:
            RT = D.getReturnType()
            return_type = module_name(RT)
            self.extract_package(type_name(RT))
            funcname = D.getName()
            argtypes = [self.extract_package(type_name(T)) for T in D.getParameterTypes()]
            n = len(argtypes)
            funcargs = [argtypes[i]+" "+"arg"+str(i) for i in range(n)]
            callargs = ["arg"+str(i) for i in range(n)]
            ET = D.getExceptionTypes()
            ET = (ET[0] if len(ET) else None)
            if ET:
                self.extract_package(type_name(ET))
                exc_type = " throws "+module_name(ET)+" "
            else:
                exc_type = ""
            self.extract_package(type_name(D.clazz))
            return " ".join(prefix)+" "+return_type, return_type,  funcargs, callargs, funcname, argtypes, exc_type
        else:
            argtypes = [T.strip() for T in args.strip()[1:-1].split(",") if T]
            funcname = self.extract_package(funcname, takelast = False)
            return_type = self.extract_package(return_type)
            argtypes = [self.extract_package(T) for T in argtypes]
            n = len(argtypes)
            funcargs = [argtypes[i]+" "+"arg"+str(i) for i in range(n)]
            callargs = ["arg"+str(i) for i in range(n)]
            return " ".join(prefix)+" "+return_type, return_type, funcargs, callargs, funcname, argtypes, ""


    def build_member(self, data, annotations):
        prefix, return_type, funcargs, callargs, funcname, types, exc_type = self.extract_method(data+"()", annotations)
        anno = ''
        if annotations:
            anno = ' '.join(annotations)+" "
        return anno+data+";"

    def build_method(self, method, annotations, overload):
        prefix, return_type, funcargs, callargs, funcname, types, exc_type = self.extract_method(method, annotations)
        args = "("+", ".join(funcargs)+")"
        prefix = "\n    ".join([str(anno) for anno in annotations])+"\n    "+prefix
        if return_type == "void":
            body = "{ jaobject."+funcname+"("+",".join(callargs)+"); }"
        else:
            body = "{ return jaobject."+funcname+"("+",".join(callargs)+"); }"
        return "    "+prefix+" "+(overload if overload else funcname)+args+exc_type+body+"\n"

    def build_jy_method_sig(self, method, name, annotations, overload):
        prefix, return_type, funcargs, callargs, funcname, types, exc_type = self.extract_method(method, annotations)
        funcname = name
        args = "("+", ".join(funcargs)+")"
        prefix = "\n    ".join([str(anno) for anno in annotations])+"\n    "+prefix
        n = len(callargs)
        body = ['']
        return_cast = return_type
        if return_type in primtype:
            return_cast = primtype[return_type]
        if n:
            body.append("PyObject args[] = new PyObject[%s];"%n)
            #body.append("for(int i=0;i<%s;i++) {"%n)
            for i in range(n):
                body.append("args[%s] = Py.java2py(arg%s);"%(i,i))
            #body.append("}")
            if return_type == "void":
                body.append('jyobject.invoke("'+funcname+'"'+", args);")
            else:
                body.append('return (%s)jyobject.invoke("'%return_cast+funcname+'"'+', args).__tojava__(%s.class);'%return_type)
        else:
            if return_type == "void":
                body.append('jyobject.invoke("'+funcname+'"'+");")
            else:
                body.append('return (%s)jyobject.invoke("'%return_cast+funcname+'"'+").__tojava__(%s.class);"%return_type)
        return "  "+prefix+" "+(overload if overload else funcname)+args+"{" +"\n        ".join(body)+"\n    }\n"

    def build_jy_class_method(self, clsname, method, name, annotations, overload):
        prefix, return_type, funcargs, callargs, funcname, types, exc_type = self.extract_method(method, annotations)
        funcname = name
        args = "("+", ".join(funcargs)+")"
        prefix = "\n    ".join([str(anno) for anno in annotations])+"\n    "+prefix
        n = len(callargs)
        body = ['']
        return_cast = return_type
        if return_type in primtype:
            return_cast = primtype[return_type]
        if n:
            call = 'JyGateway.callStatic("%s", "%s", args)'%(clsname, funcname)
            body.append("PyObject args[] = new PyObject[%s];"%n)
            #body.append("for(int i=0;i<%s;i++) {"%n)
            for i in range(n):
                body.append("args[%s] = Py.java2py(arg%s);"%(i,i))
            #body.append("}")
        else:
            call = 'JyGateway.callStatic("%s", "%s", null)'%(clsname, funcname)
        if return_type == "void":
            body.append(call+";")
        else:
            body.append('return (%s)%s.__tojava__(%s.class);'%(return_cast, call, return_type))
        return "    "+prefix+" "+(overload if overload else funcname)+args+"{" +"\n        ".join(body)+"\n    }\n"

    def build_jy_method(self, method, name, annotations, overload):
        prefix, return_type, funcargs, callargs, funcname, types, exc_type = self.extract_method(method, annotations)
        funcname = name
        prefix = "\n    ".join([str(anno) for anno in annotations])+"\n    "+prefix
        if return_type == "PyObject":
            args = "(PyObject[] args)"
            if "void" in prefix:
                body = "{ "+'jyobject.invoke("'+funcname+'"'+", args); }"
            else:
                body = "{ return "+'jyobject.invoke("'+funcname+'"'+", args); }"
        else:
            args = "()"
            if "void" in prefix:
                body = "{ "+'jyobject.invoke("'+funcname+'"'+"); }"
            else:
                body = "{ return "+'jyobject.invoke("'+funcname+'"'+"); }"
        return "    "+prefix+" "+(overload if overload else funcname)+args+body+"\n"


    def build_constructor(self, method, annotations, jatype, jytype):
        prefix, return_type, funcargs, callargs, funcname, partypes, exc_type = self.extract_method(method, annotations)
        n = len(partypes)
        # print "CONS", method, prefix, funcargs, callargs, funcname, partypes
        args = ",".join([partypes[i]+" "+"arg"+str(i) for i in range(n)])
        head = prefix+" "+jytype+"("+args+") {"
        body = []
        arglist = ",".join("arg"+str(i) for i in range(n))
        body.append("super("+arglist+")")
        if n:
            body.append("Object values[] = {%s}"%arglist)
            body.append('jyobject = JyGateway.newInstance("%s", this, values)'%jytype)
            body.append('jaobject = (%s)jyobject.__tojava__(%s.class)'%(jatype, jatype))
        else:
            body.append('jyobject = JyGateway.newInstance("%s", this, null)'%jytype)
            body.append('jaobject = (%s)jyobject.__tojava__(%s.class)'%(jatype, jatype))
        B = ";\n        ".join(body)
        return "    "+head+"\n        "+B+";\n    }\n"

    def default_imports(self):
        self.imports.append("import org.jynx.JyGateway;")
        self.imports.append("import org.jynx.gen.*;")
        self.imports.append("import org.python.core.PyObject;")
        self.imports.append("import org.python.core.Py;")


    def add_package(self, packagename):
        self.packages.add("import %s;"%packagename)

    def add_jajyobjects(self, base, classdef):
        jaanno = self.options.get("jaobject_annotation", "")
        if jaanno:
            jaanno = " "+jaanno
        jyanno = self.options.get("jyobject_annotation", "")
        if jyanno:
            jyanno = " "+jyanno
        classdef.append("   %s private PyObject jyobject;\n"%jyanno)
        classdef.append("   %s private "%jaanno+module_name(base)+" jaobject;\n")

    def build_class(self):
        self.get_all_classes()
        cls = self.cls
        attrs   = cls.__dict__
        clsname = module_name(cls)
        methods = []
        members = []
        base = find_base_class(self.cls)
        anno_imports = set()
        try:
            for anno in cls.java_annotations:
                anno_imports.update(anno.anno_imports)
        except AttributeError:
            pass

        for name, value in cls.__dict__.items():
            # print self.packages
            # print "---------------------------"
            # print name, value
            overload = (value.overload if hasattr(value, "overload") else "")
            if hasattr(value, "java_annotations"):
                annotations = value.java_annotations
            else:
                annotations = []
            for anno in annotations:
                anno_imports.update(anno.anno_imports)
            if isinstance(value, jproperty):
                annos = []
                for anno in value.annotation:
                    annos.append(str(anno))
                    anno_imports.update(anno.anno_imports)
                if value.initializer:
                    members.append(self.build_member(value.type_info+" "+name+" = "+value.initializer, annos))
                else:
                    members.append(self.build_member(value.type_info+" "+name, annos))
            elif name == "plain_methods":
                methods+=value
            elif name == "mapping_attributes":
                continue
            elif hasattr(value, "__call__"):
                if name == "__init__":
                    continue                   # ?
                elif name in base.__dict__:
                    methods.append(self.build_method(base.__dict__[name], annotations, overload))
                    continue
                if hasattr(value, "java_signature"):
                    if "static" in value.java_signature:
                        setattr(cls, name, classmethod(value))
                        methods.append(self.build_jy_class_method(module_name(cls),
                                                                  value.java_signature,
                                                                  name,
                                                                  annotations, overload))
                    else:
                        methods.append(self.build_jy_method_sig(value.java_signature,
                                                                name,
                                                                annotations, overload))
                else:
                    methods.append(self.build_jy_method("public PyObject "+name+"()",
                                                        name,
                                                        annotations, overload))
            elif isinstance(value, (classmethod, staticmethod)):
                F = getattr(cls, name)
                if hasattr(F, "java_annotations"):
                    annotations = F.java_annotations
                else:
                    annotations = []
                if hasattr(F, "java_signature"):
                    methods.append(self.build_jy_class_method(module_name(cls),
                                                              F.java_signature,
                                                              name,
                                                              annotations, overload))
                else:
                    methods.append(build_jy_class_method(module_name(cls),
                                                         "public static PyObject "+name+"()",
                                                         name,
                                                         annotations, overload))


        cons = [self.build_constructor(c, [], module_name(base), module_name(cls)) for c in find_constructors(cls)]
        self.imports += ["import "+cl+";" for cl in anno_imports]
        self.default_imports()
        annotations = ([str(anno) for anno in cls.java_annotations] if hasattr(cls, "java_annotations") else [])
        if base.isInterface():
            self.extract_name(base)
            classdef = self.imports+[""]+annotations+["public class "+module_name(cls)+" implements "+base.__name__+" {"]
        else:
            classdef = self.imports+[""]+annotations+["public class "+module_name(cls)+" extends "+base.__name__+" {"]
        for mem in members:
            classdef.append("    "+mem)
        self.add_jajyobjects(base, classdef)
        for c in cons:
            classdef.append(c)
        for m in methods:
            classdef.append(m)
        classdef.append("}")
        for pkg in self.options.get("pkg",[]):
            self.add_package(pkg)
        classcode = "\n".join(list(self.packages)+[""]+classdef)
        return classcode


class signature(object):
    multimethod = {}
    def __init__(self, sig, overload = False):
        self.java_signature   = sig
        self.java_annotations = []
        self.overload = overload

    @classmethod
    def overload_handler(cls, C):
        for name in cls.multimethod:
            try:
                delattr(C, name)
                cnt, L = cls.multimethod[name]
                for f in L:
                    setattr(C, f.__name__, f)
            except AttributeError:
                pass
        cls.multimethod = {}

    def __call__(self, f):
        try:
            f.java_signature = self.java_signature
            if self.java_annotations:
                f.java_annotations = self.java_annotations
            if self.overload:
                f.overload = f.__name__
        except AttributeError:
            f.im_func.java_signature = self.java_signature
            if self.java_annotations:
                f.im_func.java_annotations = self.java_annotations
            if self.overload:
                f.im_func.overload = f.__name__
        if self.overload:
            name = f.__name__
            cnt, L  = signature.multimethod.get(name, (-1, []))
            cnt+=1
            f.__name__ = f.__name__+"__"+str(cnt)
            L.append(f)
            signature.multimethod[name] = (cnt, L)
        return f


def add_imports(source, packages):
    source = source.strip()
    if source.startswith("package "):
        source.split("\n")
        return "\n".join(source[0]+["import "+pkg+";" for pkg in packages]+source[1:])
    else:
        return "\n".join(["import "+pkg+";" for pkg in packages])+"\n"+source


class annotation_gen(object):
    def __init__(self, anno):
        self.anno = anno
        self.name = module_name(anno)
        self.java_signature = None
        self.anno_imports = set()
        self.fill_imports()

    def fill_imports(self):
        self.arg_cnt = 0
        # print "ANNO", self.anno
        for key, value in self.anno.__dict__.items():
            if isinstance(value, reflectedfunction):
                try:
                    T = value.argslist[0].data.returnType
                    self.anno_imports.update(TypeExtractor().extract(T).classes)
                    self.arg_cnt+=1
                except AttributeError:
                    pass
        self.anno_imports.update(TypeExtractor().extract(self.anno).classes)


    def has_arguments(self):
        return bool(self.arg_cnt)

    def getAnnotation(self):
        return self.anno

    def add_signature(self, anno):
        if self.java_signature:
            anno.java_signature = self.java_signature
        return anno

    def new_annotation(self, arg = ''):
        return annotation(self.anno, arg)

    def create_annotation(self, **kwds):
        args = []
        add_imports = set()
        allowed_kwds = self.anno.__dict__.keys()
        for key, value in kwds.items():
            if not key in allowed_kwds:
                raise TypeError("Unknown keyword argument '%s' for annotation %s"%(key, type_name(self.anno)))
            if hasattr(value, "__iter__"):
                Value = []
                for item in value:
                    if isinstance(item, (annotation, annotation_gen)):
                        add_imports.update(item.anno_imports)
                        Value.append(str(item))
                    elif isinstance(item, java.lang.Enum):
                        Value.append(type_name(type(item))+"."+str(item))
                    elif isinstance(item, str):
                        Value.append('"'+item+'"')
                    else:
                        Value.append(str(item))
                value = '{'+','.join(Value)+'}'
            elif isinstance(value, basestring):
                value = '"'+value+'"'
            elif isinstance(value, bool):
                value = str(value).lower()
            elif isinstance(value, java.lang.Class):
                add_imports.add(type_name(value))
                value = module_name(value)+".class"
            elif not isinstance(value, (int, float, str, annotation)):
                try:
                    T = type(value)
                    value = package_name(T)+"."+module_name(T)+"."+str(value)
                except AttributeError:
                    pass
            args.append("%s = %s"%(key, value))
        if args:
            anno = self.new_annotation("("+",".join(args)+")")
        else:
            anno = self.new_annotation()
        anno.anno_imports = self.anno_imports | add_imports
        # print "ANNO", anno, anno.anno_imports
        if self.java_signature:
            anno.java_signature = self.java_signature
        return anno



    def __call__(self, __obj = None, **kwds):
        if kwds:
            return self.create_annotation(**kwds)
        elif __obj:
            if isinstance(__obj, signature):
                self.java_signature = __obj.java_signature
                return self
            elif hasattr(__obj, "__call__"):
                anno = self.new_annotation()
                anno.anno_imports = self.anno_imports
                return self.add_signature(anno)(__obj)
            else:
                kwds["value"] = __obj
                return self.create_annotation(**kwds)
        else:
            anno = self.new_annotation()
            anno.anno_imports = self.anno_imports
            return self.add_signature(anno)

    def __repr__(self):
        return "@"+self.name


class annotation(object):
    def __init__(self, anno, arg = ''):
        '''
        :param anno: Java annotation class.
        :param arg: additional arguments used to construct the annotation.
        '''
        self.anno = anno
        self.arg  = arg
        self.sub_annotations  = []
        self.java_annotations = []
        self.java_signature   = []
        self.anno_imports = set()

    def anno_repr(self):
        return module_name(self.anno)+self.arg

    def getAnnotation(self):
        return self.anno

    @classmethod
    def new_anno_generator(self, anno):
        return annotation_gen(anno)

    @classmethod
    def extract(cls, *jannoclasses):
        assert jannoclasses
        _annotations = []
        for anno in jannoclasses:
            annogen = cls.new_anno_generator(anno)
            if annogen.has_arguments():
                _annotations.append(annogen)
            else:
                _annotations.append(annogen())
        return (_annotations[0] if len(_annotations) == 1 else _annotations)


    def __call__(self, obj):
        if isinstance(obj, signature):
            self.java_signature = obj.java_signature
            return self
        elif hasattr(obj, "__iter__"):
            lst = []
            for item in obj:
                if isinstance(item, (annotation, annotation_gen)):
                    self.anno_imports.update(item.anno_imports)
                lst.append(obj)
            self.sub_annotations = lst
            return self
        elif isinstance(obj, annotation):
            obj.java_annotations+=self.java_annotations+[self]
            obj.anno_imports.update(self.anno_imports)
            if self.java_signature:
                obj.java_signature = self.java_signature
        elif hasattr(obj, "java_annotations"):
            obj.java_annotations.append(self)
            if self.java_signature:
                try:
                    obj.java_signature = self.java_signature
                except AttributeError:
                    obj.im_func.java_signature = self.java_signature
        else:
            try:
                obj.java_annotations = [self]
                if self.java_signature:
                    obj.java_signature = self.java_signature
            except AttributeError:
                obj.im_func.java_annotations = [self]
                if self.java_signature:
                    obj.im_func.java_signature = self.java_signature
        return obj

    def __repr__(self):
        if self.sub_annotations:
            if len(self.sub_annotations) == 1:
                return "@"+self.anno_repr()+"("+str(self.sub_annotations)[1:-1]+")"
            else:
                return "@"+self.anno_repr()+"( {"+str(self.sub_annotations)[1:-1]+"} )"
        else:
            return "@"+self.anno_repr()


class JavaClassMaker(object):
    def __init__(self, store = False, display = False, **options):
        self.store   = store
        self.display = display
        self.options = options
        self.annotations  = []
        self.preprocessor = [self.make_bean]
        self.postprocessor = []

    def make_bean(self, cls):
        setattr(cls, "plain_methods", [])
        setattr(cls, "mapping_attributes",[])
        for key, val in cls.__dict__.items():
            if hasattr(val, "bean_property"):
                cls.mapping_attributes.append(key)
                if isinstance(val.bean_property, str):
                    T = val.bean_property
                else:
                    T = module_name(val.bean_property)
                setattr(cls, key, jproperty("private "+T, val))
                Name = key.capitalize()
                cls.plain_methods.append("    public %s get%s() { return %s; }"%(T, Name, key))
                cls.plain_methods.append("    public void set%s(%s value) { %s = value; }"%(Name, T, key))
        return cls

    def __call__(self, cls):
        signature.overload_handler(cls)
        for trans in self.preprocessor:
            cls = trans(cls)
        for anno in self.annotations:
            cls = anno(cls)
        source  = Translator(cls, **self.options).build_class()

        if self.options.get("display_before"):
            print source

        packages, missing = ImportFinder(cls, source).findPackages()
        if packages:
            source = add_imports(source, packages)
        if self.display:
            print source
        javacls = JavaCompiler(store=self.store).createClass(module_name(cls), source)
        javacls.java_source = source

        for trans in self.postprocessor:
            trans(cls, javacls)

        def newInstance(javaobj, *args):
            jyobj = cls(*args)
            jyobj.javaobj = javaobj
            return jyobj

        def callStatic(funcname, *args):
            f = getattr(cls,funcname)
            return f(*args)

        JyGateway.registry[module_name(cls)] = {"newInstance":newInstance, "callStatic":callStatic}
        return javacls


def getAnnotations(obj):
    '''
    Returns list of Java annotations of ``obj``.
    '''
    if isinstance(obj, reflectedfunction):
        return obj.argslist[0].data.getAnnotations()
    elif isinstance(obj, java.lang.Class):
        return java.lang.Class.getAnnotations(obj)
    elif isinstance(obj, reflectedfield):
        return Field.getAnnotations(obj.field)
    return []

def bean_property(sig):
    '''
    Decorator used to mark simple functions as Entity Bean properties.
    '''
    def annotate(f):
        setattr(f, "bean_property", sig)
        return f
    return annotate


def JavaClass(cls=None, **kwd):
    if cls:
        return JavaClassMaker(**kwd)(cls)
    else:
        return JavaClassMaker(**kwd)




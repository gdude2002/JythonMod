# Table representation code

SEP = 0

class Row(dict):
    def __init__(self,other=None,order=()):
        dict.__init__(self)
        self.names = []
        if other:
            self.__dict__.update(other.__dict__)
            for entry in self:
                self[entry] = ""

    def order(self,*names):
        self.names = list(names)

    def keys(self):
        if self.names:
            return self.names
        else:
            return dict.keys(self)

    def values(self):
        return [self[key] for key in self.keys()]

    def items(self):
        return zip(self.keys(),self.values())


class Table(list):
    def __init__(self,*args,**kw):
        list.__init__(self,*args)
        self.sqltab = kw.get("sql")

    def width(self):
        if hasattr(self, "_width"):
            return self._width
        self.__out()
        return self._width

    @classmethod
    def from_cursor(self, cursor):
        fieldDescr = tuple([fieldDesr[0] for fieldDesr in cursor.description])
        t = Table(sql=True)
        r = Row()
        r.order(*fieldDescr)
        for row in cursor.fetchall():
            for i,item in enumerate(row):
                if isinstance(item, unicode):
                    r[fieldDescr[i]] = str(item)
                else:
                    r[fieldDescr[i]] = item
            t.append(r)
            r = Row()
            r.order(*fieldDescr)
        return t

    @classmethod
    def display(cls, cursor):
        T = cls.from_cursor(cursor)
        print T



    def __repr__(self):
        lgt = len(self)
        if lgt==0:
            return "[]"
        else:
            format   = {}
            boundary = ""
            row   = self[0]
            if not row:
                return ""
            keys = self[0].keys()
            for name in keys:
                w = len(name)
                for r in self:
                    if r == SEP:
                        continue
                    w = max(w,len(str(r[name])))
                if len(keys)>8:
                    format[name] = "%-"+str(w)+"s|"
                    boundary    += "+"+w*"-"
                else:
                    format[name] = " %-"+str(w)+"s |"
                    boundary    += "+"+(w+2)*"-"
            boundary +="+\n"
            table  = []
            header = boundary+"|"
            for key in row.keys():
                header+=format[key]%key
            _line_ =  header.split("\n")[0]
            self._width = len(_line_)
            header+="\n"
            for r in self:
                if r == SEP:
                    table.append(_line_+"\n")
                    continue
                table.append("|")
                for key,val in r.items():
                    table.append(format[key]%val)
                table.append("\n")
            s_table = header+boundary+"".join(table)+boundary
            if self.sqltab:
                s_table+="\n%d rows in set\n"%len(self)
            return s_table


if __name__ == '__main__':
    t = Table(sql=True)
    r = Row()
    r.order("foo","bar")
    r["foo"] = "2"
    r["bar"] = ""
    t.append(r)
    #t.append(SEP)
    r = Row()
    r["foo"] = "8277383727"
    r["bar"] = "837837387373733898393838"
    t.append(r)
    print t




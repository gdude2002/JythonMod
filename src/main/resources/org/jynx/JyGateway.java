package org.jynx;

import java.util.HashMap;
import java.lang.reflect.Constructor;
import java.lang.reflect.Method;
import java.lang.*;
import org.python.core.*;
import org.python.core.Py;
import org.python.core.PyInstance;
import org.python.core.PyClass;
import org.python.core.PyTuple;

public class JyGateway
{
    public static HashMap<String, PyDictionary> registry = new HashMap<String, PyDictionary>();


    private static PyObject call(String mode, String classname, Object javaobj, Object arglist[])
    {
        int n = (arglist!=null ? arglist.length : 0);
        PyFunction fn = (PyFunction)registry.get(classname).get(mode);
        PyObject args[] = new PyObject[n+1];
        args[0] = Py.java2py(javaobj);
        if(n>0)
        {
            for(int i=0;i<n;i++)
            {
                args[i+1] = Py.java2py(arglist[i]);
            }
        }
        PyObject obj = fn.__call__(args);
        return obj;

    }

    public static PyObject callStatic(String classname, Object javaobj, Object arglist[])
    {
        return call("callStatic", classname, javaobj, arglist);
    }

    public static PyObject newInstance(String classname, Object javaobj, Object arglist[])
    {
        return call("newInstance", classname, javaobj, arglist);
    }
}



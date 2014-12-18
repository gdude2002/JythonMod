package me.gserv.jython.python;

public class ModFactory {

    private static ModFactory instance;

    private ModFactory() {

    }

    public static ModFactory get() {
        if (ModFactory.instance == null) {
            ModFactory.instance = new ModFactory();
        }

        return ModFactory.instance;
    }
}

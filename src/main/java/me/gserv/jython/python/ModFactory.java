package me.gserv.jython.python;

import cpw.mods.fml.common.event.*;
import me.gserv.jython.enums.ForgeEventType;
import org.python.core.PyException;
import org.python.core.PyObject;
import org.python.core.PyType;
import org.python.util.PythonInterpreter;

import java.util.HashMap;

public class ModFactory {

    private static ModFactory instance;
    public HashMap<String, Mod> mods;

    private ModFactory() {
        this.mods = new HashMap<String, Mod>();
    }

    public static ModFactory get() {
        if (ModFactory.instance == null) {
            ModFactory.instance = new ModFactory();
        }

        return ModFactory.instance;
    }

    public void loadScript(String module) {
        PythonInterpreter interpreter = new PythonInterpreter();
        String cmd = String.format("from pymods.%s import PyMod", module);

        interpreter.exec("import sys\nsys.path.append(\".\")");
        interpreter.exec(cmd);
        PyObject modClass = interpreter.get("PyMod");
        PyObject mod = modClass.__call__(new PyObject(PyType.fromClass(this.getClass())));

        Mod finalMod = (Mod) mod.__tojava__(Mod.class);

        String scriptName = finalMod.getModName();

        while (this.mods.containsKey(scriptName)) {
            scriptName += "_";
        }

        this.mods.put(scriptName, finalMod);

        System.out.println(String.format("JythonMod |  INFO | Loaded mod: %s", scriptName));
    }

    public void fireEvents(ForgeEventType eventType, FMLEvent eventObject) {
        for (Mod mod : this.mods.values()) {
            try {
                switch (eventType) {
                    case CONSTRUCTION:
                        mod.onConstructionEvent((FMLConstructionEvent) eventObject);
                        break;
                    case FINGERPRINT_VIOLATION:
                        mod.onFingerprintViolationEvent((FMLFingerprintViolationEvent) eventObject);
                        break;
                    case INITIALIZATION:
                        mod.onInitializationEvent((FMLInitializationEvent) eventObject);
                        break;
                    case INTER_MOD_COMMS:
                        mod.onInterModCommsEvent((FMLInterModComms.IMCEvent) eventObject);
                        break;
                    case LOAD_COMPLETE:
                        mod.onLoadCompleteEvent((FMLLoadCompleteEvent) eventObject);
                        break;
                    case MISSING_MAPPING:
                        mod.onMissingMappingsEvent((FMLMissingMappingsEvent) eventObject);
                        break;
                    case MOD_DISABLED:
                        mod.onModDisabledEvent((FMLModDisabledEvent) eventObject);
                        break;
                    case MOD_ID_MAPPING:
                        mod.onModIdMappingEvent((FMLModIdMappingEvent) eventObject);
                        break;
                    case POST_INITIALIZATION:
                        mod.onPostInitializationEvent((FMLPostInitializationEvent) eventObject);
                        break;
                    case PRE_INITIALIZATION:
                        mod.onPreInitializationEvent((FMLPreInitializationEvent) eventObject);
                        break;
                    case SERVER_ABOUT_TO_START:
                        mod.onServerAboutToStartEvent((FMLServerAboutToStartEvent) eventObject);
                        break;
                    case SERVER_STARTED:
                        mod.onServerStartedEvent((FMLServerStartedEvent) eventObject);
                        break;
                    case SERVER_STARTING:
                        mod.onServerStartingEvent((FMLServerStartingEvent) eventObject);
                        break;
                    case SERVER_STOPPED:
                        mod.onServerStoppedEvent((FMLServerStoppedEvent) eventObject);
                        break;
                    case SERVER_STOPPING:
                        mod.onServerStoppingEvent((FMLServerStoppingEvent) eventObject);
                        break;
                }
            } catch (PyException e) {
                System.out.println(
                        String.format("JythonMod | ERROR | Error firing event \"%s\" for mod %s", eventType.name(), mod.getModName())
                );
                System.out.println(
                        String.format("JythonMod | ERROR | %s: %s", e.type, e.value)
                );
                e.printStackTrace();
            } catch (Exception e) {
                System.out.println(
                        String.format("JythonMod | ERROR | Error firing event \"%s\" for mod %s", eventType.name(), mod.getModName())
                );
                e.printStackTrace();
            }
        }
    }
}

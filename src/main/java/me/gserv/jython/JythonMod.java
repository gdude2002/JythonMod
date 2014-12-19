package me.gserv.jython;

import cpw.mods.fml.common.Mod;
import cpw.mods.fml.common.event.*;
import me.gserv.jython.enums.ForgeEventType;
import me.gserv.jython.python.ModFactory;
import org.python.core.PyException;

import java.io.File;
import java.io.FileFilter;
import java.io.IOException;

@Mod(modid = JythonMod.MODID, version = JythonMod.VERSION)
public class JythonMod {
    public static final String MODID = "JythonMod";
    public static final String VERSION = "0.0.1";

    @Mod.Instance(value = JythonMod.MODID)
    public static JythonMod instance;

    /* Mod-specific stuff */

    public File modsFolder;
    private ModFactory modFactory;

    /* Event handlers */

    public JythonMod() {
        // Constructor, do Jython init here

        System.out.println("JythonMod |  INFO | Setting up..");

        this.modsFolder = new File("./pymods");
        this.modFactory = ModFactory.get();

        if (! this.modsFolder.exists()) {  // Make sure our folders and stuff exist
            boolean result = this.modsFolder.mkdir();

            if (!result) {
                System.out.println("JythonMod | ERROR | Unable to create \"pymods\" folder!");
                return;
            }

            File initPy = new File(this.modsFolder, "__init__.py");

            try {
                result = initPy.createNewFile();

                if (!result) {
                    System.out.println("JythonMod | ERROR | Unable to create \"pymods/__init__.py\" file!");
                    return;
                } else {
                    System.out.println("JythonMod |  INFO | Created folder for python mods successfully.");
                }
            } catch (IOException e) {
                System.out.println("JythonMod | ERROR | Unable to create \"pymods/__init__.py\" file!");
                e.printStackTrace();
                return;
            }
        }

        File[] files = this.modsFolder.listFiles(new FileFilter() {
            @Override
            public boolean accept(File file) {
                return file.getName().endsWith(".py") && !file.getName().startsWith("__init__");
            }
        });

        for (File f : files) {
            String filename = f.getName();
            try {
                this.modFactory.loadScript(filename.substring(0, filename.length() - 3));
            } catch (PyException e) {
                System.out.println(String.format("JythonMod | ERROR | Unable to load mod from file: %s", filename));
                System.out.println(String.format("JythonMod | ERROR | %s %s", e.type, e.value));
                System.out.println("");
                e.printStackTrace();
            } catch (Exception e) {
                System.out.println(String.format("JythonMod | ERROR | Unable to load mod from file: %s", filename));
                e.printStackTrace();
            }
        }

        System.out.println(String.format("JythonMod |  INFO | Loaded %s mods.", this.modFactory.mods.size()));
    }

    @Mod.EventHandler
    public void onConstructionEvent(FMLConstructionEvent event) {
        this.modFactory.fireEvents(ForgeEventType.CONSTRUCTION, event);
    }

    @Mod.EventHandler
    public void onFingerprintViolationEvent(FMLFingerprintViolationEvent event) {
        this.modFactory.fireEvents(ForgeEventType.FINGERPRINT_VIOLATION, event);
    }

    @Mod.EventHandler
    public void onInitializationEvent(FMLInitializationEvent event) {
        this.modFactory.fireEvents(ForgeEventType.INITIALIZATION, event);
    }

    @Mod.EventHandler
    public void onInterModCommsEvent(FMLInterModComms.IMCEvent event) {
        this.modFactory.fireEvents(ForgeEventType.INTER_MOD_COMMS, event);
    }

    @Mod.EventHandler
    public void onLoadCompleteEvent(FMLLoadCompleteEvent event) {
        this.modFactory.fireEvents(ForgeEventType.LOAD_COMPLETE, event);
    }

    @Mod.EventHandler
    public void onMissingMappingsEvent(FMLMissingMappingsEvent event) {
        this.modFactory.fireEvents(ForgeEventType.MISSING_MAPPING, event);
    }

    @Mod.EventHandler
    public void onModDisabledEvent(FMLModDisabledEvent event) {
        this.modFactory.fireEvents(ForgeEventType.MOD_DISABLED, event);
    }

    @Mod.EventHandler
    public void onModIdMappingEvent(FMLModIdMappingEvent event) {
        this.modFactory.fireEvents(ForgeEventType.MOD_ID_MAPPING, event);
    }

    @Mod.EventHandler
    public void onPostInitializationEvent(FMLPostInitializationEvent event) {
        this.modFactory.fireEvents(ForgeEventType.POST_INITIALIZATION, event);
    }

    @Mod.EventHandler
    public void onPreInitializationEvent(FMLPreInitializationEvent event) {
        this.modFactory.fireEvents(ForgeEventType.PRE_INITIALIZATION, event);
    }

    @Mod.EventHandler
    public void onServerAboutToStartEvent(FMLServerAboutToStartEvent event) {
        this.modFactory.fireEvents(ForgeEventType.SERVER_ABOUT_TO_START, event);
    }

    @Mod.EventHandler
    public void onServerStartedEvent(FMLServerStartedEvent event) {
        this.modFactory.fireEvents(ForgeEventType.SERVER_STARTED, event);
    }

    @Mod.EventHandler
    public void onServerStartingEvent(FMLServerStartingEvent event) {
        this.modFactory.fireEvents(ForgeEventType.SERVER_STARTING, event);
    }

    @Mod.EventHandler
    public void onServerStoppedEvent(FMLServerStoppedEvent event) {
        this.modFactory.fireEvents(ForgeEventType.SERVER_STOPPED, event);
    }

    @Mod.EventHandler
    public void onServerStoppingEvent(FMLServerStoppingEvent event) {
        this.modFactory.fireEvents(ForgeEventType.SERVER_STOPPING, event);
    }
}

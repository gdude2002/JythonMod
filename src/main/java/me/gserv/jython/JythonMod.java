package me.gserv.jython;

import cpw.mods.fml.common.Mod;
import cpw.mods.fml.common.event.*;
import me.gserv.jython.python.ModFactory;

import java.io.File;
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

        if (! this.modsFolder.exists()) {
            boolean result = this.modsFolder.mkdir();

            if (!result) {
                System.out.println("JythonMod | ERROR | Unable to create \"pymods\" folder!");
            } else {
                File initPy = new File(this.modsFolder, "__init__.py");

                try {
                    result = initPy.createNewFile();

                    if (!result) {
                        System.out.println("JythonMod | ERROR | Unable to create \"pymods/__init__.py\" file!");
                    } else {
                        System.out.println("JythonMod |  INFO | Created folder for python mods successfully.");
                    }
                } catch (IOException e) {
                    System.out.println("JythonMod | ERROR | Unable to create \"pymods/__init__.py\" file!");
                    e.printStackTrace();
                }
            }
        }
    }

    @Mod.EventHandler
    public void onConstructionEvent(FMLConstructionEvent event) {

    }

    @Mod.EventHandler
    public void onFingerprintViolationEvent(FMLFingerprintViolationEvent event) {

    }

    @Mod.EventHandler
    public void onInitializationEvent(FMLInitializationEvent event) {

    }

    @Mod.EventHandler
    public void onInterModCommsEvent(FMLInterModComms event) {

    }

    @Mod.EventHandler
    public void onLoadCompleteEvent(FMLLoadCompleteEvent event) {

    }

    @Mod.EventHandler
    public void onLoadEvent(FMLLoadEvent event) {

    }

    @Mod.EventHandler
    public void onMissingMappingsEvent(FMLMissingMappingsEvent event) {

    }

    @Mod.EventHandler
    public void onModDisabledEvent(FMLModDisabledEvent event) {

    }

    @Mod.EventHandler
    public void onModIdMappingEvenT(FMLModIdMappingEvent event) {

    }

    @Mod.EventHandler
    public void onPostInitializationEvent(FMLPostInitializationEvent event) {

    }

    @Mod.EventHandler
    public void onPreInitializationEvent(FMLPreInitializationEvent event) {

    }

    @Mod.EventHandler
    public void onServerAboutToStartEvent(FMLServerAboutToStartEvent event) {

    }

    @Mod.EventHandler
    public void onServerStartedEvent(FMLServerStartedEvent event) {

    }

    @Mod.EventHandler
    public void onServerStartingEvent(FMLServerStartingEvent event) {

    }

    @Mod.EventHandler
    public void onServerStoppedEvent(FMLServerStoppedEvent event) {

    }

    @Mod.EventHandler
    public void onServerStoppingEvent(FMLServerStoppingEvent event) {

    }
}

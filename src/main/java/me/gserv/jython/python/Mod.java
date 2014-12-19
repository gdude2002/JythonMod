package me.gserv.jython.python;

import cpw.mods.fml.common.event.*;

public interface Mod {
    public String getModName();

    public void onConstructionEvent(FMLConstructionEvent event);
    public void onFingerprintViolationEvent(FMLFingerprintViolationEvent event);
    public void onInitializationEvent(FMLInitializationEvent event);
    public void onInterModCommsEvent(FMLInterModComms.IMCEvent event);
    public void onLoadCompleteEvent(FMLLoadCompleteEvent event);
    public void onMissingMappingsEvent(FMLMissingMappingsEvent event);
    public void onModDisabledEvent(FMLModDisabledEvent event);
    public void onModIdMappingEvent(FMLModIdMappingEvent event);
    public void onPostInitializationEvent(FMLPostInitializationEvent event);
    public void onPreInitializationEvent(FMLPreInitializationEvent event);
    public void onServerAboutToStartEvent(FMLServerAboutToStartEvent event);
    public void onServerStartedEvent(FMLServerStartedEvent event);
    public void onServerStartingEvent(FMLServerStartingEvent event);
    public void onServerStoppedEvent(FMLServerStoppedEvent event);
    public void onServerStoppingEvent(FMLServerStoppingEvent event);
}

from me.gserv.jython.python import Mod


class BaseMod(Mod):
    def getModName(self):
        return "NamelessMod"

    def onConstructionEvent(self, event):
        pass

    def onFingerprintViolationEvent(self, event):
        pass

    def onInitializationEvent(self, event):
        pass

    def onInterModCommsEvent(self, event):
        pass

    def onLoadCompleteEvent(self, event):
        pass

    def onLoadEvent(self, event):
        pass

    def onMissingMappingsEvent(self, event):
        pass

    def onModDisabledEvent(self, event):
        pass

    def onModIdMappingEvenT(self, event):
        pass

    def onPostInitializationEvent(self, event):
        pass

    def onPreInitializationEvent(self, event):
        pass

    def onServerAboutToStartEvent(self, event):
        pass

    def onServerStartedEvent(self, event):
        pass

    def onServerStartingEvent(self, event):
        pass

    def onServerStoppedEvent(self, event):
        pass

    def onServerStoppingEvent(self, event):
        pass


import os
import logging
import pymel.core as pm


import quickmenus


__all__ = [
]


LOG = logging.getLogger("quickmenus")



class QuickSelectMenu(quickmenus.MarkingMenu):

    def __init__(self):
        super(self.__class__, self).__init__()
        self.popupMenuId = 'QuickMenus_QuickSelectMenu'
        self.mouseButton = 1

    def shouldBuild(self):
        return self.panelType == 'modelPanel'

    def buildMenuItems(self):
        pass




class QuickSelectCollectionsMenu(quickmenus.RMBMarkingMenu):

    def buildMenuItems(self):
        pass

from .. import core
import menus


__all__ = [
    "disable",
    "enable",
    "registerHotkeys",
    "removeHotkeys",
]

def registerHotkeys():
    importCmd = "import maya.mel as mel"
    secondaryCmd = "mel.eval('fitPanel -selectedNoChildren')"
    description = "A dynamic quick select set menu for storing and retrieving selections easily"
    core.registerMenuHotkeys("FMenus", "F", importCmd=importCmd, secondaryCmd=secondaryCmd, annotation=description)

    description2 = "A menu to switch between collections of quick select menus"
    core.registerMenuHotkeys("AltFMenus", "Alt+F", annotation=description2)

    print('Quick Menus: F-Menu hotkeys registered')


def removeHotkeys():
    core.removeMenuHotkeys("FMenus", "F")
    core.removeMenuHotkeys("AltFMenus", "Alt+F")
    print('Quick Menus: F-Menu hotkeys removed')


def enable():
    # TODO: would be nice to define mouse button and hotkey for each here
    # core.registerMenu("FMenus", menus.)
    # core.registerMenu("AltFMenus", menus.)
    print('Quick Menus: F-Menus enabled')


def disable():
    core.unregisterMenu("FMenus", all=True)
    print('Quick Menus: F-Menus disabled')


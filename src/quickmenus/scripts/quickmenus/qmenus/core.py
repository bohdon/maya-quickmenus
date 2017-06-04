
from .. import core
import menus


__all__ = [
    "disable",
    "enable",
    "registerHotkeys",
    "removeHotkeys",
]

def registerHotkeys():
    preBuildCmd = "import maya.mel as mel\nmel.eval('global string $gSelect; setToolTo $gSelect;')"
    description = "Selection and display masking menus, as well as a camera quick switch menu"
    core.registerMenuHotkeys("QMenus", "Q", preBuildCmd=preBuildCmd, annotation=description)
    description2 = "Component selection and resetter menus"
    core.registerMenuHotkeys("AltQMenus", "Alt+Q", annotation=description2)


def removeHotkeys():
    core.removeMenuHotkeys("QMenus", "Q")
    core.removeMenuHotkeys("AltQMenus", "Alt+Q")


def enable():
    core.registerMenu("QMenus", menus.SelectionMaskingMenu)
    core.registerMenu("QMenus", menus.DisplayMaskingMenu)
    core.registerMenu("QMenus", menus.CameraQuickSwitchMenu)


def disable():
    core.unregisterMenu("QMenus", all=True)
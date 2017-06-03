
import os

import pymel.core as pm

__all__ = [
    "getHotkeyKwargs",
    "registerMenuHotkeys",
    "removeMenuHotkeys",
]

BUILD_MENU_CMD = """
{preBuild}

try:
    import quickmenus
    quickmenus.buildMenus('{menuName}')
except:
    {secondary}
"""

REMOVE_MENU_CMD = """
try:
    import quickmenus
    wasInvoked = quickmenus.removeMenus('{menuName}')
except:
    pass
else:
    if not wasInvoked:
        {secondary}
"""


def getHotkeyKwargs(keyString):
    """
    Return kwargs to be given to the maya `hotkey` command given a hotkey string

    Args:
        keyString: A string representing a hotkey, including modifiers, e.g. 'Alt+Shift+Q'
    """
    split = keyString.lower().split('+')
    kwargs = {}
    for s in split:
        if s == 'alt':
            kwargs['alt'] = True
        elif s == 'shift':
            kwargs['sht'] = True
        elif s == 'ctrl':
            kwargs['ctl'] = True
        elif s == 'command':
            kwargs['cmd'] = True
        else:
            if 'k' not in kwargs:
                kwargs['k'] = s
            else:
                raise ValueError('Invalid keyString: ' + keyString)
    return kwargs


def registerMenuHotkeys(menuName, hotkey, preBuildCmd=None, secondaryCmd=None, annotation=None):
    """
    Setup hotkeys for builds and removing marking menus on hotkey press and release.

    Args:
        menuName: A string name of the menu for which to create hotkeys
        buildCmd: A string python snippet called to build the menu
        hotkey: A string representing the hotkey to use for the menu, e.g. 'Alt+Shift+Q'
        preBuildCmd: String formatted python that is called before building the menu
        secondaryCmd: String formatted python to be called on release if the menu is not invoked
        annotation: A string description of the menu to use when building the runTimeCommand
    """
    # the format for runtime command ids
    rtCmdIdFmt = "quickMenus_{0}_{1}"
    # the format for named command ids
    namedCmdIdFmt = "quickMenus_{0}_{1}_nameCmd"
    # get kwargs from hotkey string
    keyKwargs = getHotkeyKwargs(hotkey)

    # shared kwargs for all runtime commands
    runTimeKwargs = {
        "annotation": annotation,
        "category": "Custom Scripts.quickmenus",
        "cl":"python",
    }

    # clean prebuild and secondary commands
    preBuildCmd = preBuildCmd if preBuildCmd else ""
    secondaryCmd = secondaryCmd if secondaryCmd else "pass"

    # create run time commands
    buildCmd = BUILD_MENU_CMD.format(menuName=menuName, preBuild=preBuildCmd, secondary=secondaryCmd)
    removeCmd = REMOVE_MENU_CMD.format(menuName=menuName, preBuild=preBuildCmd, secondary=secondaryCmd)

    buildRtCmdId = rtCmdIdFmt.format("build", menuName)
    if pm.runTimeCommand(buildRtCmdId, q=True, ex=True):
        pm.runTimeCommand(buildRtCmdId, e=True, delete=True)
    pm.runTimeCommand(buildRtCmdId, c=buildCmd, **runTimeKwargs)

    buildNamedCmdId = namedCmdIdFmt.format("build", menuName)
    pm.nameCommand(buildNamedCmdId, c=buildRtCmdId, ann=buildRtCmdId + " Named Command")

    removeRtCmdId = rtCmdIdFmt.format("remove", menuName)
    if pm.runTimeCommand(removeRtCmdId, q=True, ex=True):
        pm.runTimeCommand(removeRtCmdId, e=True, delete=True)
    pm.runTimeCommand(removeRtCmdId, c=removeCmd, **runTimeKwargs)

    removeNamedCmdId = namedCmdIdFmt.format("remove", menuName)
    pm.nameCommand(removeNamedCmdId, c=removeRtCmdId, ann=removeRtCmdId + " Named Command")

    pm.hotkey(name=buildNamedCmdId, **keyKwargs)
    pm.hotkey(releaseName=removeNamedCmdId, **keyKwargs)


def removeMenuHotkeys(menuName, hotkey):
    """
    Remove all hotkeys for the given menu

    Args:
        menuName: A string name of the registered marking menu
        hotkey: A string representing the hotkey to use for the menu, e.g. 'Alt+Shift+Q'
    """
    rtCmdIdFmt = "quickMenus_{0}_{1}"
    namedCmdIdFmt = "quickMenus_{0}_{1}_nameCmd"
    # get kwargs from hotkey string
    keyKwargs = getHotkeyKwargs(hotkey)

    buildRtCmdId = rtCmdIdFmt.format("build", menuName)
    if pm.runTimeCommand(buildRtCmdId, q=True, ex=True):
        pm.runTimeCommand(buildRtCmdId, e=True, delete=True)

    removeRtCmdId = rtCmdIdFmt.format("remove", menuName)
    if pm.runTimeCommand(removeRtCmdId, q=True, ex=True):
        pm.runTimeCommand(removeRtCmdId, e=True, delete=True)

    # clear hotkeys if set
    buildNamedCmdId = namedCmdIdFmt.format("build", menuName)
    removeNamedCmdId = namedCmdIdFmt.format("remove", menuName)
    keyQueryKwargs = keyKwargs.copy()
    key = keyQueryKwargs.pop('k')
    if pm.hotkey(key, query=True, name=True, **keyQueryKwargs) == buildNamedCmdId:
        pm.hotkey(name="", **keyKwargs)
    if pm.hotkey(key, query=True, releaseName=True, **keyQueryKwargs) == removeNamedCmdId:
        pm.hotkey(releaseName="", **keyKwargs)





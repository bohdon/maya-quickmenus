
import os
import logging

import pymel.core as pm

__all__ = [
    "buildMenus",
    "destroyMenus",
    "getAllRegisteredMenus",
    "getHotkeyKwargs",
    "getRegisteredMenus",
    "registerMenu",
    "registerMenuHotkeys",
    "removeMenuHotkeys",
    "unregisterMenu",
]


LOG = logging.getLogger("quickmenus")
LOG.level = logging.INFO


BUILD_MENU_CMD = """
{preBuild}

try:
    import quickmenus
    quickmenus.buildMenus('{menuName}')
except Exception as e:
    raise e
    {secondary}
"""

DESTROY_MENU_CMD = """
try:
    import quickmenus
    wasInvoked = quickmenus.destroyMenus()
except Exception as e:
    raise e
else:
    if not wasInvoked:
        {secondary}
"""

# all menus that have been registered,
# stored as a list of classes indexed by menu name
REGISTERED_MENUS = {}

# list of any active marking menus that
# can / should be destroyed when menu key is released
ACTIVE_MENUS = []


# Hotkey Utils
# ------------

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
    destroyCmd = DESTROY_MENU_CMD.format(menuName=menuName, preBuild=preBuildCmd, secondary=secondaryCmd)

    buildRtCmdId = rtCmdIdFmt.format("build", menuName)
    if pm.runTimeCommand(buildRtCmdId, q=True, ex=True):
        pm.runTimeCommand(buildRtCmdId, e=True, delete=True)
    pm.runTimeCommand(buildRtCmdId, c=buildCmd, **runTimeKwargs)

    buildNameCmdId = namedCmdIdFmt.format("build", menuName)
    pm.nameCommand(buildNameCmdId, c=buildRtCmdId, ann=buildRtCmdId + " Named Command")

    destroyRtCmdId = rtCmdIdFmt.format("destroy", menuName)
    if pm.runTimeCommand(destroyRtCmdId, q=True, ex=True):
        pm.runTimeCommand(destroyRtCmdId, e=True, delete=True)
    pm.runTimeCommand(destroyRtCmdId, c=destroyCmd, **runTimeKwargs)

    destroyNameCmdId = namedCmdIdFmt.format("destroy", menuName)
    pm.nameCommand(destroyNameCmdId, c=destroyRtCmdId, ann=destroyRtCmdId + " Named Command")

    pm.hotkey(name=buildNameCmdId, **keyKwargs)
    pm.hotkey(releaseName=destroyNameCmdId, **keyKwargs)


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

    destroyRtCmdId = rtCmdIdFmt.format("destroy", menuName)
    if pm.runTimeCommand(destroyRtCmdId, q=True, ex=True):
        pm.runTimeCommand(destroyRtCmdId, e=True, delete=True)

    # clear hotkeys if set
    buildNameCmdId = namedCmdIdFmt.format("build", menuName)
    destroyNameCmdId = namedCmdIdFmt.format("destroy", menuName)
    keyQueryKwargs = keyKwargs.copy()
    key = keyQueryKwargs.pop('k')
    if pm.hotkey(key, query=True, name=True, **keyQueryKwargs) == buildNameCmdId:
        pm.hotkey(name="", **keyKwargs)
    if pm.hotkey(key, query=True, releaseName=True, **keyQueryKwargs) == destroyNameCmdId:
        pm.hotkey(releaseName="", **keyKwargs)



# Building / Destroying Menus
# ---------------------------

def buildMenus(menuName):
    """
    Build any marking menus that were registered for a menu name.

    Args:
        menuName: A string name of the registered marking menu
    """
    # perform destroy before building because sometimes
    # the release-hotkey gets skipped if the current
    # key modifiers change while the menu is active
    destroyMenus()

    # find any registered menus by name
    classes = getRegisteredMenus(menuName)
    LOG.debug('Building menu classes {0}: {1}'.format(menuName, classes))
    for menuCls in classes:
        inst = menuCls()
        if inst.shouldBuild():
            LOG.debug('Building: {0}'.format(inst))
            ACTIVE_MENUS.append(inst)
            inst.build()


def destroyMenus():
    """
    Destroy any marking menus that are currently built.

    Returns:
        True if any of the menus that were destroyed were
        shown at least once.
    """
    wasAnyInvoked = False
    
    global ACTIVE_MENUS
    for m in ACTIVE_MENUS:
        wasAnyInvoked = wasAnyInvoked or m.wasInvoked
        LOG.debug('Destroying menu: {0}'.format(m))
        m.destroy()
    ACTIVE_MENUS = []

    return wasAnyInvoked



# Menu Registration
# -----------------

def registerMenu(menuName, cls):
    """
    Register a MarkingMenu class by name

    Args:
        menuName: A string name of the registered marking menu
        cls: A MarkingMenu subclass to register for being built later
    """
    global REGISTERED_MENUS
    # get existing list of registered menus of same name
    existing = REGISTERED_MENUS.get(menuName, [])
    # prevent duplicates
    REGISTERED_MENUS[menuName] = list(set(existing + [cls]))


def unregisterMenu(menuName, cls=None, all=False):
    """
    Unregister a MarkingMenu that was previously registered by name.

    Args:
        menuName: A string name of the registered marking menu
        cls: A MarkingMenu subclass to unregister
        all: A bool, when True, all menus registered with the given
            menu name are unregistered.
    """
    if not cls and not all:
        raise ValueError("`cls` argument must be given when not unregistering all menus")
    global REGISTERED_MENUS
    if menuName in REGISTERED_MENUS:
        if all:
            REGISTERED_MENUS[menuName] = []
        elif cls in REGISTERED_MENUS[menuName]:
            REGISTERED_MENUS[menuName].remove(cls)
        # remove list if empty
        if not REGISTERED_MENUS[menuName]:
            del REGISTERED_MENUS[menuName]


def getRegisteredMenus(menuName):
    """
    Return the menu class that is registered under
    the given name

    Args:
        menuName: A string name of the registered marking menu
    """
    global REGISTERED_MENUS
    if menuName in REGISTERED_MENUS:
        return REGISTERED_MENUS[menuName][:]
    return []


def getAllRegisteredMenus():
    """
    Return all registered menus
    """
    global REGISTERED_MENUS
    return REGISTERED_MENUS.items()




class MarkingMenu(object):
    """
    The base class for any quick marking menu that can
    be registered. Provides core functionality of building
    and destroying a popup menu appropriately.
    """

    def __init__(self):
        # variable to keep track of if this menu ever showed
        self.wasInvoked = False
        # the panel that the popup menu will be attached to
        self.panel = pm.getPanel(up=True)
        # the panel type, can be used when building to determine the menu's contents
        self.panelType = pm.getPanel(typeOf=self.panel)
        LOG.debug("Panel: " + self.panel + ", Panel Type: " + self.panelType)

        # the unique id for this popup menu, must be overridden in subclasses
        self.popupMenuId = None
        # the mouse button that triggers this popup menu, 1=lmb, 2=mmb, 3=rmb
        self.mouseButton = 1
        # when True, build menu items each time the menu is displayed
        self.buildItemsOnShow = False

    def shouldBuild(self):
        """
        Override to implement custom logic for whether or not this
        menu should be built
        """
        return True

    def build(self):
        """
        Build the popup menu that all menu items will be attached to
        """
        if not self.popupMenuId:
            raise NotImplementedError("popupMenuId must be set on MarkingMenu classes")
        # calling destroy as a failsafe so that duplicate
        # menus dont get created
        self.destroy()
        self.menu = pm.popupMenu(self.popupMenuId, b=self.mouseButton, mm=True, aob=True, parent="viewPanes")
        self.menu.postMenuCommand(self.onMenuWillShow)
        # if not set to build on show, build items now
        if not self.buildItemsOnShow:
            pm.setParent(self.menu, m=True)
            self.buildMenuItems()

    def destroy(self):
        """
        Remove and destroy this menu
        """
        if pm.popupMenu(self.popupMenuId, q=True, ex=True):
            pm.deleteUI(self.popupMenuId)

    def onMenuWillShow(self, menu, parent):
        self.wasInvoked = True
        if self.buildItemsOnShow:
            self.menu.deleteAllItems()
            pm.setParent(self.menu, m=True)
            self.buildMenuItems()

    def buildMenuItems(self):
        """
        Build all menu items for the current popup menu.
        Called each time the menu is about to be displayed.
        """
        pass



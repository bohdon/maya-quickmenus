
import os
import logging
import pymel.core as pm

import pymetanode as meta

import quickmenus


__all__ = [
    "getAllCollections",
    "getCollection",
    "getDefaultCollection",
    "QuickSelectCollection",
    "QuickSelectCollectionsMenu",
    "QuickSelectMenu",
    "QuickSelectSet",
]


LOG = logging.getLogger("quickmenus")


# the meta class name for quick select collection data
META_CLASSNAME = "QuickSelectCollection"
# prefix for quick select collection nodes
COLLECTION_PREFIX = "quickSelectCollection_"
# the name of the default auto-created collection
DEFAULT_COLLECTION_NAME = "Default"
# the name of the current quick select collection
CURRENT_COLLECTION = None


# Quick Select Core
# -----------------


def getAllCollections():
    """
    Return a list of all quick select collections
    """
    nodes = meta.findMetaNodes(META_CLASSNAME)
    if nodes:
        return [QuickSelectCollection.fromNode(n) for n in nodes]
    # no sets, create the default one and return it in a list
    return [getDefaultCollection()]


def getCollection(name):
    """
    Return a QuickSelectCollection from the scene by name
    """
    nodes = meta.findMetaNodes(META_CLASSNAME)
    for n in nodes:
        if n.nodeName()[len(COLLECTION_PREFIX):] == name:
            return QuickSelectCollection.fromNode(n)


def getDefaultCollection():
    """
    Return the default QuickSelectCollection from the scene.
    If it does not exist, create it.
    """
    coll = getCollection(DEFAULT_COLLECTION_NAME)
    if not coll:
        coll = QuickSelectCollection(DEFAULT_COLLECTION_NAME)
        coll.save()
    return coll


class QuickSelectCollection(object):
    """
    Acts as the data model for all quick select menus.
    Can load and save quick select sets and collections.
    """
    @classmethod
    def fromNode(cls, node):
        inst = QuickSelectCollection()
        inst.load(node)
        return inst

    def __init__(self, name=None):
        self.name = name
        self.sets = []

    def getNode(self):
        """
        Return the collection node from the scene with the
        same name, if one exists
        """
        nodes = meta.findMetaNodes(META_CLASSNAME)
        for n in nodes:
            if n.nodeName()[len(COLLECTION_PREFIX):] == self.name:
                return n

    def getOrCreateNode(self):
        """
        Return the collection node from the scene with the
        same name, or create one if it doesn't exist
        """
        node = self.getNode()
        if node:
            return node
        else:
            return pm.createNode('network', name=COLLECTION_PREFIX + self.name)

    def load(self, node=None):
        if not node:
            node = self.getNode()
        if node:
            data = meta.getMetaData(node, META_CLASSNAME)
            self.name = node.nodeName()[len(COLLECTION_PREFIX):]
            self.sets = [QuickSelectSet(**kwargs) for kwargs in data.get('sets', [])]

    def save(self):
        data = {
            'sets': [s.asDict() for s in self.sets]
        }
        node = self.getOrCreateNode()
        meta.setMetaData(node, META_CLASSNAME, data)

    def setName(self, newName):
        # TODO: sanitize name
        # TODO: make sure name is available
        self.name = newName
        self.save()

    def addSet(self, quickSet):
        if not isinstance(quickSet, QuickSelectSet):
            raise TypeError("set must be a QuickSelectSet")
        for s in self.sets:
            if s.position == quickSet.position:
                raise ValueError("cannot add a quick set, position already occupied: {0}".format(s.position))
        self.sets.append(quickSet)
        self.save()

    def removeSetAtPosition(self, position):
        for s in self.sets:
            if s.position == position:
                self.sets.remove(s)
                self.save()
                break

    def removeSetAtIndex(self, index):
        if index >= 0 and index < len(self.sets):
            self.sets.pop(index)
            self.save()



class QuickSelectSet(object):
    """
    Represents one or more objects in the scene that
    can then be easily selected
    """
    def __init__(self, nodes, title=None, position=None):
        # the nodes in this set
        self.setNodes(nodes)
        # title of this sets menu item
        self.title = title
        # the radial position of this set
        self.position = position

    def getTitle(self):
        if self.title:
            return self.title
        else:
            return self.abbreviate(self.nodes)

    def __len__(self):
        return self.nodes.__len__()

    def asDict(self):
        """
        Return this QuickSelectSet as a simple python object
        """
        result = {
            'nodes': self.nodes,
            'title': self.title,
        }
        return result

    def setNodes(self, newNodes):
        self.nodes = []
        for n in newNodes:
            if isinstance(n, pm.nt.DependNode):
                self.nodes.append(n.longName())
            else:
                self.nodes.append(str(n))

    def abbreviate(self, nodes, maxLen=15):
        str = ', '.join([n.split('|')[-1] for n in nodes])
        if len(str) > maxLen:
            return '{0}...'.format(str[:10])
        return str

    def select(self, add=True):
        pm.select(self.nodes, add=add)






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
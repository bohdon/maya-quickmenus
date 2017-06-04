
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

RADIAL_POSITIONS = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']



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
            sel = pm.selected()
            node = pm.createNode('network', name=COLLECTION_PREFIX + self.name)
            pm.select(sel)
            return node

    def load(self, node=None):
        if not node:
            node = self.getNode()
        if node:
            data = meta.getMetaData(node, META_CLASSNAME)
            self.name = node.nodeName()[len(COLLECTION_PREFIX):]
            self.sets = [QuickSelectSet(**kwargs) for kwargs in data.get('sets', [])]

    def save(self):
        # TODO: handle locked nodes
        data = {
            'sets': [s.asDict() for s in self.sets]
        }
        node = self.getOrCreateNode()
        meta.setMetaData(node, META_CLASSNAME, data)

    def isReadOnly(self):
        return False

    def setName(self, newName):
        # TODO: sanitize name
        # TODO: make sure name is available
        self.name = newName
        self.save()

    def addSet(self, quickSet):
        if not isinstance(quickSet, QuickSelectSet):
            raise TypeError("set must be a QuickSelectSet")
        if quickSet.position:
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

    def clearSets(self):
        self.sets = []
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
            'position': self.position,
        }
        return result

    def setNodes(self, newNodes):
        self.nodes = []
        for n in newNodes:
            if isinstance(n, pm.nt.DependNode):
                self.nodes.append(n.longName())
            else:
                self.nodes.append(str(n))

    def addNodes(self, newNodes):
        pyNodes = [pm.PyNode(n) for n in self.nodes]
        self.setNodes(set(pyNodes + newNodes))

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
        self.collection = getDefaultCollection()
        self.isReadOnly = self.collection.isReadOnly()
        self.showCounts = False

    def shouldBuild(self):
        return self.panelType == 'modelPanel'

    def getVacancies(self):
        result = RADIAL_POSITIONS[:]
        for s in self.collection.sets:
            if s.position in result:
                result.remove(s.position)
        return result

    def buildMenuItems(self):
        # build menu items for each set
        for i, s in enumerate(self.collection.sets):
            itemKwargs = {
                'l':s.getTitle(),
            }
            if self.showCounts:
                itemKwargs['l'] += ' ({1})'.format(len(s))
            if s.position:
                itemKwargs['rp'] = s.position
            pm.menuItem(c=pm.Callback(pm.select, s.nodes, add=True), **itemKwargs)
            if not self.isReadOnly:
                pm.menuItem(ob=True, c=pm.Callback(self.editSet, s, i))

        # put in slots for vacancies
        if not self.isReadOnly:
            vacantPositions = self.getVacancies()
            for rp in vacantPositions:
                pm.menuItem(l='...', rp=rp, c=pm.Callback(self.addSetFromSelection, position=rp))
            # always include slot at end of extras list
            pm.menuItem(l='...', c=pm.Callback(self.addSetFromSelection))

        # collection title
        pm.menuItem(d=True)
        pm.menuItem(l=self.collection.name, c=pm.Callback(self.selectAll))
        pm.menuItem(ob=True, c=pm.Callback(self.editCollection))


    def addSetFromSelection(self, position=None):
        s = QuickSelectSet(pm.selected(), position=position)
        if len(s):
            self.collection.addSet(s)


    def editSet(self, quickSet, quickSetIndex):
        kw = dict(
            t='Edit Quick Select Set:',
            m=quickSet.getTitle(),
            db='Cancel',
            cb='Cancel',
            ds='dismiss',
            b=['Add', 'Replace', 'Rename', 'Delete', 'Cancel'],
        )
        action = pm.confirmDialog(**kw)
        if action == 'Add':
            self.addSelection(quickSet)
        elif action == 'Replace':
            self.replaceWithSelection(quickSet)
        elif action == 'Rename':
            self.renamePrompt(quickSet)
        elif action == 'Delete':
            self.delete(quickSetIndex)

    def addSelection(self, quickSet):
        quickSet.addNodes(pm.selected())
        self.collection.save()

    def replaceWithSelection(self, quickSet):
        quickSet.setNodes(pm.selected())
        self.collection.save()

    def renamePrompt(self, quickSet):
        name = promptBox('Rename Set', 'Enter a name:', 'Rename', 'Cancel', tx=quickSet['title'])
        if name:
            quickSet['title'] = name
            self.collection.save()

    def delete(self, quickSetIndex):
        self.collection.removeSetAtIndex(quickSetIndex)

    def selectAll(self):
        for s in self.collection.sets:
            s.select(add=True)

    def editCollection(self):
        kw = dict(
            t='Edit Collection: {0}'.format(self.collection.name),
            m='{0} set(s)'.format(len(self.collection.sets)),
            db='Cancel',
            cb='Cancel',
            ds='dismiss',
            b=['Clear All', 'Delete Collection', 'Cancel'],
        )
        action = pm.confirmDialog(**kw)
        if action == 'Clear All':
            self.collection.clearSets()
        elif action == 'Delete Collection':
            node = self.collection.getNode()
            if node:
                pm.delete(node)





class QuickSelectCollectionsMenu(quickmenus.RMBMarkingMenu):

    def buildMenuItems(self):
        pass
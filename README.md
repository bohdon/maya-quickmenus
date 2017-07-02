# Maya Quick Menus

A set of marking menus for making common tasks more eficient.

There are currently 2 sets of menus, F-Menus, and Q-Menus, named by the default hotkeys that they are assigned to.


## F-Menus

F-menus allow you to create quick selection sets that are assigned to slots in a radial marking menu. They are designed for workflows like animation, where it is faster to use the gestural nature of marking menus instead of having to use a picker UI or select controls interactively.

#### Usage

- Hold `f` and use `left-mouse-button` to summon the main quick selection menu.
- Hold `f` and use `right-mouse-button` to summon a manager menu for switching between different collections of quick select sets.


## Q-Menus

Q-menus are a set of selection and display related marking menus. Menus include a selection masking radial menu, display masking radial menu, and improved component selection mode switching. The Q-Menus are assigned to Q because of the relationship with the Q (selection) tool itself.

#### Usage

- Hold `q` and use `left-mouse-button` to summon the selection masking menu
- Hold `q` and use `middle-mouse-button` to summon the display masking menu
- Hold `q` and use `right-mouse-button` to summon a camera quick switching menu
- Hold `alt+q` and use `left-mouse-button` to summon the component selection menu
- Hold `alt+q` and use `middle-mouse-button` to summon a [resetter](https://github.com/bohdon/maya-resetter) menu for quickly resetting object transforms, etc


## Installation

**Requires [maya-rmbmenuhook](https://github.com/bohdon/maya-rmbmenuhook)**

Download the [latest release](https://github.com/bohdon/maya-quickmenus/releases/latest) and unzip the contents into your `~/Documents/maya/modules` folder.

Add the following to `userSetup.py`:

```python
# enable Quick Menus
import quickmenus
quickmenus.qmenus.enable()
quickmenus.fmenus.enable()
```

A one-time setup is required for registering the hotkeys, run this in the Script Editor:

```python
# register Quick Menu hotkeys
quickmenus.qmenus.registerHotkeys()
quickmenus.fmenus.registerHotkeys()
```

NOTE: in Maya 2017, some issues still exist with custom Hotkey sets, and you may have to run this each session
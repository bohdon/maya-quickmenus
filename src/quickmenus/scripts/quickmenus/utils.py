
import pymel.core as pm


__all__ = [
    "getRadialMenuPositions",
]


def getRadialMenuPositions(count):
    """
    Return a list of radial positions for the given number of items.
    Positions are distributed when count is lower than 8

    Args:
        count: An int representing number of items in the menu
    """
    if count < 0:
        raise ValueError("count cannot be negative")
    defaults = [
        [], ['N'], ['N', 'S'], ['N', 'E', 'W'], ['N', 'E', 'S', 'W'],
    ]
    ordered = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    if count < len(defaults):
        return defaults[count]
    else:
        results = []
        for i in range(count):
            if i < len(ordered):
                results.append(ordered[i])
            else:
                results.append(None)
        return results
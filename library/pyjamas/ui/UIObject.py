# Copyright 2006 James Tauber and contributors
# Copyright (C) 2009 Luke Kenneth Casson Leighton <lkcl@lkcl.net>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from pyjamas import DOM
import Factory
from pyjamas import Window
from pyjamas.ui import Applier

def setStyleName(element, style, add):

    oldStyle = DOM.getAttribute(element, "className")
    if oldStyle is None:
        oldStyle = ""
    idx = oldStyle.find(style)

    # Calculate matching index
    lastPos = len(oldStyle)
    while idx != -1:
        if idx == 0 or (oldStyle[idx - 1] == " "):
            last = idx + len(style)
            if (last == lastPos) or ((last < lastPos) and (oldStyle[last] == " ")):
                break
        idx = oldStyle.find(style, idx + 1)

    if add:
        if idx == -1:
            DOM.setAttribute(element, "className", oldStyle + " " + style)
    else:
        if idx != -1:
            begin = oldStyle[:idx-1]
            end = oldStyle[idx + len(style):]
            DOM.setAttribute(element, "className", begin + end)

class UIObject(Applier):

    def __init__(self, **kwargs):
        # do not initialise element, here, to None, whatever you do.
        # there are circumstances where UIObject.__init__ is the last
        # thing that is done in derived classes, where self.setElement
        # will _already_ have been called.
        Applier.__init__(self, **kwargs)

    def getAbsoluteLeft(self):
        return DOM.getAbsoluteLeft(self.getElement())

    def getAbsoluteTop(self):
        return DOM.getAbsoluteTop(self.getElement())

    def getElement(self):
        """Get the DOM element associated with the UIObject, if any"""
        return self.element

    def getOffsetHeight(self):
        return DOM.getIntAttribute(self.element, "offsetHeight")

    def getOffsetWidth(self):
        return DOM.getIntAttribute(self.element, "offsetWidth")

    def getStyleName(self):
        return DOM.getAttribute(self.element, "className")

    def getStylePrimaryName(self):
        """Return with the first className if there are multiples"""
        fullClassName = self.getStyleName()
        if fullClassName: return fullClassName.split()[0]

    def getTitle(self):
        return DOM.getAttribute(self.element, "title")

    def setElement(self, element):
        """Set the DOM element associated with the UIObject."""
        self.element = element

    def setHeight(self, height):
        """Set the height of the element associated with this UIObject.  The
           value should be given as a CSS value, such as 100px, 30%, or 50pi"""
        DOM.setStyleAttribute(self.element, "height", str(height))

    def getHeight(self):
        return DOM.getStyleAttribute(self.element, "height")

    def setPixelSize(self, width, height):
        """Set the width and height of the element associated with this UIObject
           in pixels.  Width and height should be numbers."""
        if width >= 0:
            self.setWidth("%dpx" % width)
        if height >= 0:
            self.setHeight("%dpx" % height)

    def setSize(self, width, height):
        """Set the width and height of the element associated with this UIObject.  The
           values should be given as a CSS value, such as 100px, 30%, or 50pi"""
        self.setWidth(width)
        self.setHeight(height)

    def addStyleName(self, style):
        """Append a style to the element associated with this UIObject.  This is
        a CSS class name.  It will be added after any already-assigned CSS class for
        the element."""
        self.setStyleName(self.element, style, True)

    def addStyleDependentName(self, styleSuffix):
        """Adds a secondary or dependent style name to this element.
        For example if the primary stylename is gwt-TextBox, 
        self.addStyleDependentName("readonly") will return gwt-TextBox-readonly."""
        self.addStyleName(self.getStylePrimaryName()+"-"+styleSuffix)

    def removeStyleName(self, style):
        """Remove a style from the element associated with this UIObject.  This is
        a CSS class name."""
        self.setStyleName(self.element, style, False)
    
    def removeStyleDependentName(self, styleSuffix):
        """Remove a dependent style name by specifying the style name's suffix."""
        self.removeStyleName(self.getStylePrimaryName()+"-"+styleSuffix)

    # also callable as: setStyleName(self, style)
    def setStyleName(self, element, style=None, add=True):
        """When called with a single argument, this replaces all the CSS classes
        associated with this UIObject's element with the given parameter.  Otherwise,
        this is assumed to be a worker function for addStyleName and removeStyleName."""
        # emulate setStyleName(self, style)
        if style is None:
            style = element
            DOM.setAttribute(self.element, "className", style)
            return
        setStyleName(element, style, add)

    def setTitle(self, title):
        DOM.setAttribute(self.element, "title", title)

    def setWidth(self, width):
        """Set the width of the element associated with this UIObject.  The
           value should be given as a CSS value, such as 100px, 30%, or 50pi"""
        DOM.setStyleAttribute(self.element, "width", str(width))

    def getWidth(self):
        return DOM.getStyleAttribute(self.element, "width")

    def sinkEvents(self, eventBitsToAdd):
        """Request that the given events be delivered to the event handler for this
        element.  The event bits passed are added (using inclusive OR) to the events
        already "sunk" for the element associated with the UIObject.  The event bits
        are a combination of values from class L{Event}."""
        if self.element:
            DOM.sinkEvents(self.getElement(), eventBitsToAdd | DOM.getEventsSunk(self.getElement()))

    def setzIndex(self, index):
        DOM.setIntStyleAttribute(self.element, "zIndex", index)

    def isVisible(self, element=None):
        """Determine whether this element is currently visible, by checking
            the CSS property 'display'
        """
        if not element:
            element = self.element
        try: # yuk!
            return element.style.display != "none"
        except AttributeError: # not been set (yet?)
            return True

    # also callable as: setVisible(visible)
    def setVisible(self, element, visible=None):
        """Set whether this element is visible or not.  If a single parameter is
        given, the self.element is used.  This modifies the CSS property 'display',
        which means that an invisible element not only is not drawn, but doesn't
        occupy any space on the page."""
        if visible is None:
            visible = element
            element = self.element

        if visible:
            DOM.setStyleAttribute(element, 'display', "")
        else:
            DOM.setStyleAttribute(element, 'display', "none")

    def unsinkEvents(self, eventBitsToRemove):
        """Reverse the operation of sinkEvents.  See L{UIObject.sinkevents}."""
        DOM.sinkEvents(self.getElement(), ~eventBitsToRemove & DOM.getEventsSunk(self.getElement()))

Factory.registerClass('pyjamas.ui.UIObject', UIObject)


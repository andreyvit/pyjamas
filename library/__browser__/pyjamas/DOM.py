
# Copyright 2006 James Tauber and contributors
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

def init():
    JS("""
    // Set up capture event dispatchers.
    $wnd.__dispatchCapturedMouseEvent = function(evt) {
        if ($wnd.__dispatchCapturedEvent(evt)) {
            var cap = DOM.getCaptureElement();
            if (cap && cap.__listener) {
                DOM.dispatchEvent(evt, cap, cap.__listener);
                evt.stopPropagation();
            }
        }
    };

    $wnd.__dispatchCapturedEvent = function(evt) {
        if (!DOM.previewEvent(evt)) {
            evt.stopPropagation();
            evt.preventDefault();
            return false;
        }

        return true;
        };

    $wnd.addEventListener(
        'mouseout',
        function(evt){
            var cap = DOM.getCaptureElement();
            if (cap) {
                if (!evt.relatedTarget) {
                    // When the mouse leaves the window during capture, release capture
                    // and synthesize an 'onlosecapture' event.
                    DOM.sCaptureElem = null;
                    if (cap.__listener) {
                        var lcEvent = $doc.createEvent('UIEvent');
                        lcEvent.initUIEvent('losecapture', false, false, $wnd, 0);
                        DOM.dispatchEvent(lcEvent, cap, cap.__listener);
                    }
                }
            }
        },
        true
    );


    $wnd.addEventListener('click', $wnd.__dispatchCapturedMouseEvent, true);
    $wnd.addEventListener('dblclick', $wnd.__dispatchCapturedMouseEvent, true);
    $wnd.addEventListener('mousedown', $wnd.__dispatchCapturedMouseEvent, true);
    $wnd.addEventListener('mouseup', $wnd.__dispatchCapturedMouseEvent, true);
    $wnd.addEventListener('mousemove', $wnd.__dispatchCapturedMouseEvent, true);
    $wnd.addEventListener('keydown', $wnd.__dispatchCapturedEvent, true);
    $wnd.addEventListener('keyup', $wnd.__dispatchCapturedEvent, true);
    $wnd.addEventListener('keypress', $wnd.__dispatchCapturedEvent, true);
    
    $wnd.__dispatchEvent = function(evt) {
    
        var listener, curElem = this;
        
        while (curElem && !(listener = curElem.__listener)) {
            curElem = curElem.parentNode;
        }
        if (curElem && curElem.nodeType != 1) {
            curElem = null;
        }
    
        if (listener) {
            DOM.dispatchEvent(evt, curElem, listener);
        }
    };
    """)

def addEventPreview(preview):
    sEventPreviewStack.append(preview)

def buttonClick(button):
    JS("""
    button.click();
    """)

def compare(elem1, elem2):
    JS("""
    return (elem1 == elem2);
    """)

def createElement(tag):
    JS("""
    return $doc.createElement(tag);
    """)

def createInputElement(elementType):
    JS("""
    var e = $doc.createElement("INPUT");
    e.type = elementType;
    return e;
    """)

def createInputRadio(group):
    JS("""
    var elem = $doc.createElement("INPUT");
    elem.type = 'radio';
    elem.name = group;
    return elem;
    """)

def eventGetFromElement(evt):
    JS("""
    return evt.fromElement ? evt.fromElement : null;
    """)

def eventGetKeyCode(evt):
    JS("""
    return evt.which ? evt.which : (evt.keyCode ? evt.keyCode : 0);
    """)

def eventGetTarget(event):
    JS("""
    return event.target ? event.target : null;
    """)

def eventGetToElement(evt):
    JS("""
    return evt.relatedTarget ? evt.relatedTarget : null;
    """)

def eventGetTypeInt(event):
    JS("""
    switch (event.type) {
      case "blur": return 0x01000;
      case "change": return 0x00400;
      case "click": return 0x00001;
      case "dblclick": return 0x00002;
      case "focus": return 0x00800;
      case "keydown": return 0x00080;
      case "keypress": return 0x00100;
      case "keyup": return 0x00200;
      case "load": return 0x08000;
      case "losecapture": return 0x02000;
      case "mousedown": return 0x00004;
      case "mousemove": return 0x00040;
      case "mouseout": return 0x00020;
      case "mouseover": return 0x00010;
      case "mouseup": return 0x00008;
      case "scroll": return 0x04000;
      case "error": return 0x10000;
      case "contextmenu": return 0x20000;
    }
    """)

def eventToString(evt):
    JS("""
    return evt.toString();
    """)

def getAbsoluteLeft(elem):
    JS("""
    var left = 0;
    while (elem) {
      left += elem.offsetLeft - elem.scrollLeft;
      elem = elem.offsetParent;
    }
    return left + $doc.body.scrollLeft;
    """)

def getAbsoluteTop(elem):
    JS("""
    var top = 0;
    while (elem) {
      top += elem.offsetTop - elem.scrollTop;
      elem = elem.offsetParent;
    }
    return top + $doc.body.scrollTop;
    """)

def getAttribute(elem, attr):
    JS("""
    var ret = elem[attr];
    return (ret == null) ? null : String(ret);
    """)

def getElemAttribute(elem, attr):
    return elem.getAttribute(attr)

def getBooleanAttribute(elem, attr):
    JS("""
    return !!elem[attr];
    """)

def getCaptureElement():
    return sCaptureElem

def getChild(elem, index):
    """
    Get a child of the DOM element by specifying an index.
    """
    JS("""
    var count = 0, child = elem.firstChild;
    while (child) {
      var next = child.nextSibling;
      if (child.nodeType == 1) {
        if (index == count)
          return child;
        ++count;
      }
      child = next;
    }

    return null;
    """)

def getChildCount(elem):
    """
    Calculate the number of children the given element has.  This loops
    over all the children of that element and counts them.
    """
    JS("""
    var count = 0, child = elem.firstChild;
    while (child) {
      if (child.nodeType == 1)
      ++count;
      child = child.nextSibling;
    }
    return count;
    """)

def getChildIndex(parent, toFind):
    """
    Return the index of the given child in the given parent.
    
    This performs a linear search.
    """
    JS("""
    var count = 0, child = parent.firstChild;
    while (child) {
        if (child == toFind)
            return count;
        if (child.nodeType == 1)
            ++count;
        child = child.nextSibling;
    }

    return -1;
    """)

def getElementById(id):
    """
    Return the element in the document's DOM tree with the given id.
    """
    JS("""
    var elem = $doc.getElementById(id);
    return elem ? elem : null;
    """)

def getEventListener(element):
    """
    See setEventListener for more information.
    """
    JS("""
    return element.__listener;
    """)

def getEventsSunk(element):
    """
    Return which events are currently "sunk" for a given DOM node.  See
    sinkEvents() for more information.
    """
    JS("""
    return element.__eventBits ? element.__eventBits : 0;
    """)

def getFirstChild(elem):
    JS("""
    var child = elem.firstChild;
    while (child && child.nodeType != 1)
      child = child.nextSibling;
    return child ? child : null;
    """)

def getInnerHTML(element):
    JS("""
    var ret = element.innerHTML;
    return (ret == null) ? null : ret;
    """)

def getInnerText(element):
    JS("""
    // To mimic IE's 'innerText' property in the W3C DOM, we need to recursively
    // concatenate all child text nodes (depth first).
    var text = '', child = element.firstChild;
    while (child) {
      if (child.nodeType == 1){ // 1 == Element node
        text += DOM.getInnerText(child);
      } else if (child.nodeValue) {
        text += child.nodeValue;
      }
      child = child.nextSibling;
    }
    return text;
    """)

def getIntAttribute(elem, attr):
    JS("""
    var i = parseInt(elem[attr]);
    if (!i) {
        return 0;
    }
    return i;
    """)

def getIntStyleAttribute(elem, attr):
    JS("""
    var i = parseInt(elem.style[attr]);
    if (!i) {
        return 0;
    }
    return i;
    """)

def getNextSibling(elem):
    JS("""
    var sib = elem.nextSibling;
    while (sib && sib.nodeType != 1)
      sib = sib.nextSibling;
    return sib ? sib : null;
    """)

def getParent(elem):
    JS("""
    var parent = elem.parentNode;
    if(parent == null) {
        return null;
    }
    if (parent.nodeType != 1)
        parent = null;
    return parent ? parent : null;
    """)

def getStyleAttribute(elem, attr):
    JS("""
    var ret = elem.style[attr];
    return (ret == null) ? null : ret;
    """)

def insertChild(parent, toAdd, index):
    JS("""
    var count = 0, child = parent.firstChild, before = null;
    while (child) {
      if (child.nodeType == 1) {
        if (count == index) {
          before = child;
          break;
        }
        ++count;
      }
      child = child.nextSibling;
    }

    parent.insertBefore(toAdd, before);
    """)

def iterChildren(elem):
    """
    Returns an iterator over all the children of the given
    DOM node.
    """
    JS("""
    var parent = elem;
    var child = elem.firstChild;
    var lastChild = null;
    return {
        'next': function() {
            if (child == null) {
                throw pyjslib.StopIteration;
            }
            lastChild = child;
            child = DOM.getNextSibling(child);
            return lastChild;
        },
        'remove': function() {        
            parent.removeChild(lastChild);
        },
        __iter__: function() {
            return this;
        }
    };
    """)

def walkChildren(elem):
    """
    Walk an entire subtree of the DOM.  This returns an
    iterator/iterable which performs a pre-order traversal
    of all the children of the given element.
    """
    JS("""
    var parent = elem;
    var child = DOM.getFirstChild(elem);
    var lastChild = null;
    var stack = [];
    var parentStack = [];
    return {
        'next': function() {
            if (child == null) {
                throw pyjslib.StopIteration;
            }
            lastChild = child;
            var firstChild = DOM.getFirstChild(child);
            var nextSibling = DOM.getNextSibling(child);
            if(firstChild != null) {
               if(nextSibling != null) {
                   stack.push(nextSibling);
                   parentStack.push(parent);
                }
                parent = child;
                child = firstChild;
            } else if(nextSibling != null) {
                child = nextSibling;
            } else if(stack.length > 0) {
                child = stack.pop();
                parent = parentStack.pop();
            } else {
                child = null;
            }
            return lastChild;
        },
        'remove': function() {        
            parent.removeChild(lastChild);
        },
        __iter__: function() {
            return this;
        }
    };
    """)
   
def releaseCapture(elem):
    JS("""
    if ((DOM.sCaptureElem != null) && DOM.compare(elem, DOM.sCaptureElem))
        DOM.sCaptureElem = null;
    """)

def removeEventPreview(preview):
    sEventPreviewStack.remove(preview)

def scrollIntoView(elem):
    JS("""
    var left = elem.offsetLeft, top = elem.offsetTop;
    var width = elem.offsetWidth, height = elem.offsetHeight;
    
    if (elem.parentNode != elem.offsetParent) {
        left -= elem.parentNode.offsetLeft;
        top -= elem.parentNode.offsetTop;
    }

    var cur = elem.parentNode;
    while (cur && (cur.nodeType == 1)) {
        if ((cur.style.overflow == 'auto') || (cur.style.overflow == 'scroll')) {
            if (left < cur.scrollLeft) {
                cur.scrollLeft = left;
            }
            if (left + width > cur.scrollLeft + cur.clientWidth) {
                cur.scrollLeft = (left + width) - cur.clientWidth;
            }
            if (top < cur.scrollTop) {
                cur.scrollTop = top;
            }
            if (top + height > cur.scrollTop + cur.clientHeight) {
                cur.scrollTop = (top + height) - cur.clientHeight;
            }
        }

        var offsetLeft = cur.offsetLeft, offsetTop = cur.offsetTop;
        if (cur.parentNode != cur.offsetParent) {
            offsetLeft -= cur.parentNode.offsetLeft;
            offsetTop -= cur.parentNode.offsetTop;
        }

        left += offsetLeft - cur.scrollLeft;
        top += offsetTop - cur.scrollTop;
        cur = cur.parentNode;
    }
    """)

def removeAttribute(element, attribute):
    JS("""
    delete element[attribute];
    """)

def setAttribute(element, attribute, value):
    JS("""
    element[attribute] = value;
    """)

def setBooleanAttribute(elem, attr, value):
    JS("""
    elem[attr] = value;
    """)

def setCapture(elem):
    JS("""
    DOM.sCaptureElem = elem;
    """)

def setEventListener(element, listener):
    """
    Register an object to receive event notifications for the given
    element.  The listener's onBrowserEvent() method will be called
    when a captured event occurs.  To set which events are captured,
    use sinkEvents().
    """
    JS("""
    element.__listener = listener;
    """)

def setInnerHTML(element, html):
    JS("""
    if (!html) {
        html = "";
    }
    element.innerHTML = html;
    """)

def setInnerText(elem, text):
    JS("""
    // Remove all children first.
    while (elem.firstChild) {
        elem.removeChild(elem.firstChild);
    }
    // Add a new text node.
    elem.appendChild($doc.createTextNode(text));
    """)

def setIntAttribute(elem, attr, value):
    JS("""
    elem[attr] = value;
    """)

def setIntStyleAttribute(elem, attr, value):
    JS("""
    elem.style[attr] = value;
    """)

def setOptionText(select, text, index):
    option = select.options.item(index)
    option.text = text

def setStyleAttribute(element, attr, value):
    JS("""
    element.style[attr] = value;
    """)

def sinkEvents(element, bits):
    """
    Set which events should be captured on a given element and passed to the
    registered listener.  To set the listener, use setEventListener().
    
    @param bits: A combination of bits; see ui.Event for bit values
    """
    JS("""
    element.__eventBits = bits;
    
    element.onclick    = (bits & 0x00001) ? $wnd.__dispatchEvent : null;
    element.ondblclick  = (bits & 0x00002) ? $wnd.__dispatchEvent : null;
    element.onmousedown   = (bits & 0x00004) ? $wnd.__dispatchEvent : null;
    element.onmouseup    = (bits & 0x00008) ? $wnd.__dispatchEvent : null;
    element.onmouseover   = (bits & 0x00010) ? $wnd.__dispatchEvent : null;
    element.onmouseout  = (bits & 0x00020) ? $wnd.__dispatchEvent : null;
    element.onmousemove   = (bits & 0x00040) ? $wnd.__dispatchEvent : null;
    element.onkeydown    = (bits & 0x00080) ? $wnd.__dispatchEvent : null;
    element.onkeypress  = (bits & 0x00100) ? $wnd.__dispatchEvent : null;
    element.onkeyup    = (bits & 0x00200) ? $wnd.__dispatchEvent : null;
    element.onchange      = (bits & 0x00400) ? $wnd.__dispatchEvent : null;
    element.onfocus    = (bits & 0x00800) ? $wnd.__dispatchEvent : null;
    element.onblur      = (bits & 0x01000) ? $wnd.__dispatchEvent : null;
    element.onlosecapture = (bits & 0x02000) ? $wnd.__dispatchEvent : null;
    element.onscroll      = (bits & 0x04000) ? $wnd.__dispatchEvent : null;
    element.onload      = (bits & 0x08000) ? $wnd.__dispatchEvent : null;
    element.onerror    = (bits & 0x10000) ? $wnd.__dispatchEvent : null;
    element.oncontextmenu = (bits & 0x20000) ? $wnd.__dispatchEvent : null;
    """)

def toString(elem):
    JS("""
    var temp = elem.cloneNode(true);
    var tempDiv = $doc.createElement("DIV");
    tempDiv.appendChild(temp);
    outer = tempDiv.innerHTML;
    temp.innerHTML = "";
    return outer;
    """)

# TODO: missing dispatchEventAndCatch
def dispatchEvent(event, element, listener):
    dispatchEventImpl(event, element, listener)

def previewEvent(evt):
    ret = True
    if len(sEventPreviewStack) > 0:
        preview = sEventPreviewStack[len(sEventPreviewStack) - 1]
        
        ret = preview.onEventPreview(evt)
        if not ret:
            eventCancelBubble(evt, True)
            eventPreventDefault(evt)

    return ret

# TODO
def dispatchEventAndCatch(evt, elem, listener, handler):
    pass

def dispatchEventImpl(event, element, listener):
    global sCaptureElem, currentEvent
    if element == sCaptureElem:
        if eventGetType(event) == "losecapture":
            sCaptureElem = None
    prevCurrentEvent = currentEvent
    currentEvent = event
    listener.onBrowserEvent(event)
    currentEvent = prevCurrentEvent

def eventGetCurrentEvent():
    return currentEvent

def insertListItem(select, item, value, index):
    option = createElement("OPTION")
    setInnerText(option, item)
    if value is not None:
        setAttribute(option, "value", value)
    if index == -1:
        appendChild(select, option)
    else:
        insertChild(select, option, index)




"""
* Copyright 2007,2008,2009 John C. Gunther
* Copyright (C) 2009 Luke Kenneth Casson Leighton <lkcl@lkcl.net>
*
* Licensed under the Apache License, Version 2.0 (the
* "License"); you may not use this file except in compliance
* with the License. You may obtain a copy of the License at:
*
*  http:#www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing,
* software distributed under the License is distributed on an
* "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
* either express or implied. See the License for the specific
* language governing permissions and limitations under the
* License.
*
"""




from pyjamas import DOM
from pyjamas import Window



























from pyjamas.ui import Event
from pyjamas.ui.AbsolutePanel import AbsolutePanel
from pyjamas.ui.Composite import Composite
from pyjamas.ui.Grid import Grid
from pyjamas.ui import HasHorizontalAlignment
from pyjamas.ui import HasVerticalAlignment
from pyjamas.ui.HTML import HTML
from pyjamas.ui.Image import Image
from pyjamas.ui.SimplePanel import SimplePanel
from pyjamas.ui.UIObject import UIObject
from pyjamas.ui.Widget import Widget

# XXX HACK!  recursive includes avoidance...
NAI = 2 ** 31


import AnnotationLocation

"""*
* Convenience method that, given a plain text label, returns an
* HTML snippet appropriate for use as an argument to the
* <tt>setHovertextTemplate</tt> or <tt>setAnnotationText</tt>
* methods, that will display the plain text label with
* formatting appropriate for use with hovertext.
*
* @see Symbol#setHovertextTemplate setHovertextTemplate
* @see Curve.Point#setAnnotationText setAnnotationText
* @see Symbol#setHoverAnnotationSymbolType setHoverAnnotationSymbolType
*
* @param plainTextLabel the plain text label that is to be
*  HTML-wrapped to make it look like <tt>setTitle</tt>-based
*  hovertext.
*
*
"""

def formatAsHovertext(plainTextLabel):
    result = \
    "<html><div style='background-color:#FFFFF0; border-color:black; border-style:solid; border-width:1px 1px 1px 1px; padding:2px; text-align:left'>" + str(plainTextLabel) + "</div>"
    return result



def setBackgroundColor(uio, cssColor):
    DOM.setStyleAttribute(uio.getElement(), "backgroundColor", cssColor)


"""
def setBackground(uio, cssColor):
    DOM.setStyleAttribute(uio.getElement(), "background", cssColor)

"""
def setBorderColor(uio, cssColor):
    DOM.setStyleAttribute(uio.getElement(), "borderColor", cssColor)





def setBorderStyle(uio, cssBorderStyle):
    DOM.setStyleAttribute(uio.getElement(), "borderStyle", cssBorderStyle)



def setBorderWidth(uio, borderWidth):
    if borderWidth != NAI:
        cssBorderWidth = str(borderWidth) + "px"
    else:
        cssBorderWidth = ""
    DOM.setStyleAttribute(uio.getElement(), "borderWidth", cssBorderWidth)


def setFontFamily(uio, cssFontFamily):
    DOM.setStyleAttribute(uio.getElement(), "fontFamily", cssFontFamily)


def setFontSize(uio, fontSize):
    DOM.setIntStyleAttribute( uio.getElement(), "fontSize", fontSize)

def setFontStyle(uio, fontStyle):
    DOM.setStyleAttribute(uio.getElement(), "fontStyle", fontStyle)

def setFontWeight(uio, fontWeight):
    DOM.setStyleAttribute(uio.getElement(), "fontWeight", fontWeight)

def setColor(uio, cssColor):
    DOM.setStyleAttribute(uio.getElement(), "color", cssColor)

"""
# valid layout strings are fixed, auto, and inherit
def setTableLayout(uio, layout):
    DOM.setStyleAttribute( uio.getElement(), "table-layout", layout)




def setLineHeight(uio, cssLineHeight):
    DOM.setStyleAttribute(uio.getElement(), "lineHeight", cssLineHeight)



def setTextAlign(uio, cssTextAlign):
    DOM.setStyleAttribute( uio.getElement(), "textAlign", cssTextAlign)

def setMargin(uio, cssMargin):
    DOM.setStyleAttribute( uio.getElement(), "margin", cssMargin)

"""
def setPadding(uio, cssPadding):
    DOM.setStyleAttribute(uio.getElement(), "padding", cssPadding)

# valid choices are block, inline, list-item, or none
"""
def setDisplay(uio, cssDisplay):
    DOM.setStyleAttribute( uio.getElement(), "display", cssDisplay)

"""
# choices are: visible, hidden, scroll or auto
def setOverflow(uio, cssOverflow):
    DOM.setStyleAttribute( uio.getElement(), "overflow", cssOverflow)

"""
def setTextLeading(uio, cssTextLeading):
    DOM.setStyleAttribute( uio.getElement(), "textTrailing", cssTextLeading)

def setVerticalAlign(uio, cssVerticalAlign):
    DOM.setStyleAttribute( uio.getElement(), "verticalAlign", cssVerticalAlign)

"""
# returns the sign of the given number
def sign(x):
    result = (x < 0) and -1 or 1
    return result


# axis types (used to define which y-axis each curve is on)
class YAxisId(object):
    pass

# case-independent index of next "break" tag in string (case of HTML
# returned from HasHTML.getHTML can change with browser)
def indexOfBr(s, iStart=0):
    BR1 = "<br>"
    BR2 = "<BR>"
    BR3 = "<li>";  # recognize <li> as a break.
    BR4 = "<LI>"
    BR5 = "<tr>";  # recognize <tr> as a break.
    BR6 = "<TR>"
    iBr1 = s.indexOf(BR1, iStart)
    iBr2 = s.indexOf(BR2, iStart)
    iBr3 = s.indexOf(BR3, iStart)
    iBr4 = s.indexOf(BR4, iStart)
    iBr5 = s.indexOf(BR5, iStart)
    iBr6 = s.indexOf(BR6, iStart)
    result1 = 0
    result2 = 0
    result3 = 0
    result = 0

    if -1 == iBr1:
        result1 = iBr2

    elif -1 == iBr2:
        result1 = iBr1

    else:
        result1 = min(iBr1, iBr2)


    if -1 == iBr3:
        result2 = iBr4

    elif -1 == iBr4:
        result2 = iBr3

    else:
        result2 = min(iBr3, iBr4)


    if -1 == iBr5:
        result3 = iBr6

    elif -1 == iBr6:
        result3 = iBr5

    else:
        result3 = min(iBr5, iBr6)




    if -1 == result1:
        result = result2

    elif -1 == result2:
        result = result1

    else:
        result = min(result1, result2)



    if -1 == result:
        result = result3

    elif -1 != result3:
        result = min(result, result3)



    return result


# Provides a character-based width estimate when simple tags
# such as <b> and <i> are present in a multi-line,
# "break"-delimited, string. Very approximate, but a useful
# default.
def htmlWidth(sIn):
    iBr = indexOfBr(sIn)
    if (-1 == iBr):
        s = sIn
    else:
        s = sIn.substring(0, iBr)
    LITERAL_PAT = "[&][#a-zA-Z]+[;]"
    s = s.replaceAll(LITERAL_PAT, "X"); # literals count as 1 char
    TAG_PAT = "[<][^>]+[>]"
    s = s.replaceAll(TAG_PAT, "");   # tags don't count at all
    return s.length()


# number of <br> delimited lines in an HTML string
def htmlHeight(s):
    BR_LEN = len("<br>")
    iBr = 0
    result = 1
    if None != s:
        iBr = indexOfBr(s)
        while iBr != -1:
            result += 1
            iBr = indexOfBr(s, iBr+BR_LEN)

    return result





# Validates multipliers used to simplify computing the
# upper left corner location of symbols and labels to
# properly reflect their alignment relative to the
# plotted point or labeled symbol.
def validateMultipliers(widthMultiplier, heightMultiplier):
    if (not (widthMultiplier == 0  or  abs(widthMultiplier)==1)  and  
        not (heightMultiplier == 0  or abs(heightMultiplier)==1)):
        raise IllegalArgumentException(
        "widthMultiplier, heightMultiplier args must both be " +
        "either 0, 1, or -1")



# is value within given limits, inclusive?
def withinRange(x, minLim, maxLim):
    # x!=x is a faster isNaN; NaN is considered in range
    result = (x!=x) and True or (x >= minLim  and  x <= maxLim)
    return result

# Is the symbol type one of the special ANCHOR_MOUSE types,
# whose position varies with the mouse cursor location?
def isMouseAnchored(symbolType):
    return (SymbolType.ANCHOR_MOUSE == symbolType  or
            SymbolType.ANCHOR_MOUSE_SNAP_TO_X == symbolType  or 
            SymbolType.ANCHOR_MOUSE_SNAP_TO_Y == symbolType)



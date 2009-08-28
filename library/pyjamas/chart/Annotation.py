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



import GChart
from GChartUtil import htmlWidth

from GChartConsts import DEFAULT_FONT_COLOR
from GChartConsts import DEFAULT_ANNOTATION_FONTSIZE
from GChartConsts import DEFAULT_WIDGET_WIDTH_UPPERBOUND
from GChartConsts import DEFAULT_WIDGET_HEIGHT_UPPERBOUND
from GChartConsts import CHARHEIGHT_TO_FONTSIZE_UPPERBOUND

"""
* Annotates (labels) a chart symbol. Users access this class via
* wrapper methods of the Point class, and via various tick-label
* related methods of the Axis class.
*
"""

HTML_LEN = len("<html>")
BR_LEN = len("<br>")

# Returns number of chars in first <br>-delimited line of
# given string. A very crude way to estimate (especially
# HTML) width in characters, but user can give explicit
# widths when the width estimates based on this char width
# heuristic fail them.
def getNumberOfCharsWide(s):
    result = 0
    if not s.startswith("<html>"):
        result = len(s)
    
    else:
        result = htmlWidth(s)
    
    return result

class Annotation:
    def __init__(self):
        self.fontColor = DEFAULT_FONT_COLOR
        self.fontSize = DEFAULT_ANNOTATION_FONTSIZE
        self.fontStyle = "normal"
        self.fontWeight = "normal"
        self.location = None
        self.text = None
        self.widget = None;    # may be used in lieu of text or HTML
        self.isVisible = True
        self.xShift = 0
        self.yShift = 0
        self.isHTML = False; # no break tags ==> plain text
        # Estimated number of lines, width in chars, of annotation
        # text (not used by Widgets)
        self.numberOfLinesHigh = 0
        self.numberOfCharsWide = 0
        self.widthUpperBound = GChart.NAI
        self.heightUpperBound = GChart.NAI
        
    """
    * Computes parameters used to estimate the width and height
    * of the (invisible) enclosing 1x1 Grid of an annotation
    * (used to align, center, etc. the annotation) <p>
    *
    """
    def analyzeHTML(self, s):
        result = None
        if None == s:
            self.isHTML = False
            self.numberOfLinesHigh = 0
            self.numberOfCharsWide = 0
        
        elif not s.startswith("<html>"):
            # no html==>plain text
            self.isHTML = False
            self.numberOfLinesHigh = 1
            self.numberOfCharsWide = len(s)
            result = s
        
        else:
            # HTML
            self.isHTML = True
            # <html> is just a flag, not a tag, so strip it out.
            result = s.substring(HTML_LEN)
            if self.widthUpperBound == GChart.NAI:
                self.numberOfCharsWide = htmlWidth(result)
            
            
            if self.heightUpperBound == GChart.NAI:
                self.numberOfLinesHigh = htmlHeight(result)
            
            
        
        return result
        
    
    
    def getFontColor(self):
        return self.fontColor
    
    def getFontSize(self):
        return self.fontSize
    
    
    def getLocation(self):
        return self.location
    
    
    def isHTML(self):
        return self.isHTML
    
    
    def getText(self):
        if self.isHTML:
            return "<html>" + self.text
        return self.text
    
    def getVisible(self):
        return self.isVisible
    
    def getXShift(self):
        return self.xShift
    
    def getYShift(self):
        return self.yShift
    
    
    def setFontColor(self, cssColor):
        self.fontColor = cssColor
    
    def setFontSize(self, fontSize):
        self.fontSize = fontSize
    
    def setFontWeight(self, cssWeight):
        self.fontWeight = cssWeight
    
    def setFontStyle(self, cssStyle):
        self.fontStyle = cssStyle
    
    
    def getFontWeight(self):
        return self.fontWeight
    
    def getFontStyle(self):
        return self.fontStyle
    
    
    def setLocation(self, location):
        self.location = location
    
    
    def setText(self, text, widthUpperBound=GChart.NAI, heightUpperBound=GChart.NAI):
        self.widthUpperBound = widthUpperBound
        self.heightUpperBound = heightUpperBound
        self.text = self.analyzeHTML(text)
        self.widget = None
    
    def setVisible(self, isVisible):
        self.isVisible = isVisible
    
    
    def setWidget(self, widget,
                    widthUpperBound=DEFAULT_WIDGET_WIDTH_UPPERBOUND,
                    heightUpperBound=DEFAULT_WIDGET_HEIGHT_UPPERBOUND):
        self.widthUpperBound = widthUpperBound
        self.heightUpperBound = heightUpperBound
        self.text = None
        self.widget = widget
    
    def getWidget(self):
        return widget
    
    
    def setXShift(self, xShift):
        self.xShift = xShift
    
    def setYShift(self, yShift):
        self.yShift = yShift
    
    
    def getHeightUpperBound(self):
        result = 0
        if heightUpperBound != GChart.NAI:
            result = heightUpperBound
        
        else:
            result = int (ceil(fontSize *
                            numberOfLinesHigh *
                            CHARHEIGHT_TO_FONTSIZE_UPPERBOUND))
        
        return result
    
    
    def getWidthUpperBound(self):
        result = 0
        if widthUpperBound != GChart.NAI:
            result = widthUpperBound
        
        else:
            result = int ( ceil(fontSize *
                                numberOfCharsWide *
                                CHARWIDTH_TO_FONTSIZE_UPPERBOUND))
        
        return result
    
    
 # end of class Annotation



"""
* Copyright 2008 Google Inc.
*
* Licensed under the Apache License, Version 2.0 (the "License"); you may not
* use this file except in compliance with the License. You may obtain a copy of
* the License at
*
* http:#www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
* WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
* License for the specific language governing permissions and limitations under
* the License.
"""


from pyjamas.Canvas.CanvasGradientImplDefault import CanvasGradientImplDefault 

"""*
* Default deferred binding of GradientFactory will create instances of this class.
* This corresponds to a LinearGradient for stroke or fill styles.
"""
class LinearGradientImplDefault(CanvasGradientImplDefault):

    def __init__(self, x0, y0, x1, y1, c):
        CanvasGradientImplDefault.__init__(self)
        self.createNativeGradientObject(x0,y0,x1,y1,c)
  

    def createNativeGradientObject(self, x0, y0, x1, y1, c):
        ctx = c.getContext('2d')
        gradient = ctx.createLinearGradient(x0,y0,x1,y1)
        self.setNativeGradient(gradient)


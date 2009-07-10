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
from pyjamas import DOM

from pyjamas.ui.Widget import Widget

class Frame(Widget):
    def __init__(self, url="", element=None, **kwargs):
        if element is None: 
            element = DOM.createIFrame()
        if url:
            kwargs['Url'] = url
        self.setElement(element)
        Widget.__init__(self, **kwargs)

    def getUrl(self):
        return DOM.getAttribute(self.getElement(), "src")

    def setUrl(self, url):
        return DOM.setAttribute(self.getElement(), "src", url)



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

from CheckBox import CheckBox

class RadioButton(CheckBox):
    def __init__(self, group, label=None, asHTML=False, **kwargs):
        if not kwargs.has_key('StyleName'):kwargs['StyleName']="gwt-RadioButton"
        if label:
            if asHTML:
                kwargs['HTML'] = label
            else:
                kwargs['Text'] = label

        self.initElement(DOM.createInputRadio(group), **kwargs)

Factory.registerClass('pyjamas.ui.RadioButton', RadioButton)


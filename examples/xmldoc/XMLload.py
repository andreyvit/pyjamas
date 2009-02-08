from pyjamas.ui import Button, RootPanel, HTML, DockPanel, HasAlignment, Hyperlink, VerticalPanel, ScrollPanel
from pyjamas import Window
from pyjamas.HTTPRequest import HTTPRequest


class XMLloader:
    def __init__(self, panel):
        self.panel = panel

    def onCompletion(self, doc):
        self.panel.doStuff(doc)

    def onError(self, text, code):
        self.panel.onError(text, code)

    def onTimeout(self, text):
        self.panel.onTimeout(text)

class XMLload:

    def onModuleLoad(self):
        
        HTTPRequest().asyncPost(None, None,
                    "contacts.xml", "",
                    XMLloader(self), 1)

    def onError(self, text, code):
        # FIXME
        pass

    def onTimeout(self, text):
        # FIXME
        pass

    def doStuff(self, xmldoc):

        contacts = xmldoc.getElementsByTagName("contact")
        len = contacts.length;
        for i in range(len):
            contactsDom = contacts.item(i)
            firstNames = contactsDom.getElementsByTagName("firstname")
            firstNameNode = firstNames.item(0)
            firstName = firstNameNode.firstChild.nodeValue
            RootPanel().add(HTML("firstname: %s" % str(firstName)))

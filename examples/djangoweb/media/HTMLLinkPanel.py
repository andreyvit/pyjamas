from pyjamas.ui.HTMLPanel import HTMLPanel
from pyjamas.ui.Hyperlink import Hyperlink

from pyjamas import Window
from pyjamas import DOM

class HTMLLinkPanel(HTMLPanel):
    def __init__(self, sink, html="", title="", **kwargs):
        self.sink = sink
        self.title = title
        HTMLPanel.__init__(self, html, **kwargs)

    def replaceLinks(self, tagname="a"):
        """ replaces <tag href="#pagename">sometext</tag> with:
            Hyperlink("sometext", "pagename")
        """
        tags = self.findTags(tagname)
        pageloc = Window.getLocation()
        pagehref = pageloc.getPageHref()
        for el in tags:
            href = el.href
            l = href.split("#")
            if len(l) != 2:
                continue
            if not l[0].startswith(pagehref):
                continue
            token = l[1]
            if not token:
                continue
            html = DOM.getInnerHTML(el)
            parent = DOM.getParent(el)
            index = DOM.getChildIndex(parent, el)
            hl = Hyperlink(TargetHistoryToken=token,
                           HTML=html,
                           Element=DOM.createSpan())
            DOM.insertChild(parent, hl.getElement(), index)
            self.children.insert(index, hl)
            parent.removeChild(el)


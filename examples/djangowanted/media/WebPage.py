import pyjd

from pyjamas.ui.RootPanel import RootPanel
from pyjamas.ui.DockPanel import DockPanel
from pyjamas.ui.Button import Button
from pyjamas.ui.HTML import HTML
from pyjamas.ui.TextBox import TextBox

from pyjamas.JSONService import JSONProxy

from pyjamas import Window
from pyjamas import History
from pyjamas.django.Form import Form
from pyjamas import log

from WebPageEdit import WebPageEdit
from HTMLLinkPanel import HTMLLinkPanel

from pyjamas import Factory

class WebApp:
    def onFormLoad(self):
        self.fetch = Button("Retrieve", self)
        self.search = TextBox()
        self.submit = Button("Submit", self)
        self.formsvc = FormService()
        self.wanted = WantedService()
        d = {'price': 20, 'name': 'a good car'}
        self.form = Form(getattr(self.formsvc, "itemform"), data=d,
                         listener=self)
        #self.describe(['name', 'description'])
        RootPanel().add(self.form)
        RootPanel().add(self.search)
        RootPanel().add(self.fetch)

    def onRetrieveDone(self, form):
        log.writebr("onRetrieveDone: %s" % repr(form))

    def onDescribeDone(self, form):
        form.add_widget("Submit", self.submit)

    def onClick(self, sender):
        if sender == self.fetch:
            key = self.search.getText()
            if not key:
                log.writebr("Please enter id")
                return
            key = int(key)
            log.writebr("id %d" % key)
            #self.wanted.getItem(key, self)
            self.form.get(id=key)

        if sender == self.submit:
            v = self.form.getValue()
            log.writebr("onClick %s" % repr(v))
            if v.get('id', None):
                self.form.update(v)
            else:
                self.form.save(v)
 
    def onErrors(self, form, response):
        log.writebr("onErrors %s" % repr(response))
        
    def onSaveDone(self, form, response):
        log.writebr("onSave %s" % repr(response))
        
    def onModuleLoad(self):

        self.pages = DataService()

        #Show the initial screen.
        initToken = History().getToken()
        if initToken and len(initToken):
            if initToken == 'admin':
                RootPanel().add(WebPageEdit(self))
                return
        else:
            initToken = 'index'

        self.dock = DockPanel()
        self.dock.setWidth("100%")
        self.pages = {}
        self.current_page = None
        RootPanel().add(self.dock)

        History.addHistoryListener(self)
        self.onHistoryChanged(initToken)

    def createPage(self, ref, html, title):
        htp = HTMLLinkPanel(self, html, title)
        htp.replaceLinks()
        htp.setWidth("100%")
        self.pages[ref] = htp

    def onHistoryChanged(self, token):
        #log.writebr("onHistoryChanged %s" % token)
        if self.pages.has_key(token):
            self.setPage(token)
            return
        self.pages.getPageByName(token, self)

    def setPage(self, ref):
        
        htp = self.pages[ref]
        if htp == self.current_page:
            return
        Window.setTitle(htp.title)
        if self.current_page:
            self.dock.remove(self.current_page)
        self.dock.add(htp, DockPanel.CENTER)
        self.current_page = htp

    def onRemoteResponse(self, response, request_info):
        #if (request_info.method == 'getItem'):
        #    data = {'id': response['pk']}
        #    log.writebr(repr(response))
        #    self.form.update_values(response)

        if (request_info.method == 'getPageByName' or
           request_info.method == 'getPage'):
            item = response[0]
            html = item['fields']['text']
            token = item['fields']['name']
            self.createPage(token, html, token)
            self.setPage(token)

    def onRemoteError(self, code, message, request_info):
        RootPanel().add(HTML("Server Error or Invalid Response: ERROR " + str(code) + " - " + str(message)))


class FormService(JSONProxy):
    def __init__(self):
        JSONProxy.__init__(self, "/services/forms/",
                 ["itemform",
                 ])

class WantedService(JSONProxy):
    def __init__(self):
        JSONProxy.__init__(self, "/services/wanted/",
                 ["getItem", 
                  "getItems"])

class DataService(JSONProxy):
    def __init__(self):
        JSONProxy.__init__(self, "/services/pages/",
                 ["getPage", "updatePage",
                  "getPages", "addPage",
                  "getPageByName",
                  "deletePage"])

if __name__ == "__main__":
    pyjd.setup("http://127.0.0.9/pyjdblank.html")

    #Factory.addPyjamasNameSpace()
    app = WebApp()
    #app.onModuleLoad()
    app.onFormLoad()
    pyjd.run()


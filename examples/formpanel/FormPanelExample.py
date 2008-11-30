from pyjamas.ui import RootPanel, TextArea, Label, Button, HTML, VerticalPanel,\
               HorizontalPanel, ListBox, FormPanel, FileUpload, TextBox
from pyjamas import Window

class FormPanelExample:
    def onModuleLoad(self):
        # Create a FormPanel and point it at a service.
        self.form = FormPanel()
        self.form.setAction("/chat-service/test/")

        # Because we're going to add a FileUpload widget, we'll need to set the
        # form to use the POST method, and multipart MIME encoding.
        self.form.setEncoding(FormPanel.ENCODING_MULTIPART)
        self.form.setMethod(FormPanel.METHOD_POST)

        # Create a panel to hold all of the form widgets.
        panel = VerticalPanel()
        self.form.setWidget(panel)

        # Create a TextBox, giving it a name so that it will be submitted.
        self.tb = TextBox()
        self.tb.setName("textBoxFormElement")
        panel.add(self.tb)

        # Create a ListBox, giving it a name and some values to be associated with
        # its options.
        lb = ListBox()
        lb.setName("listBoxFormElement")
        lb.addItem("foo", "fooValue")
        lb.addItem("bar", "barValue")
        lb.addItem("baz", "bazValue")
        panel.add(lb)

        # Create a FileUpload widget.
        upload = FileUpload()
        upload.setName("uploadFormElement")
        panel.add(upload)

        # Add a 'submit' button.
        panel.add(Button("Submit", self))

        # Add an event handler to the form.
        self.form.addFormHandler(self)

        RootPanel().add(self.form)

    def onClick(self, sender):
        self.form.submit()

    def onSubmitComplete(self, event):
        # When the form submission is successfully completed, this event is
        # fired. Assuming the service returned a response of type text/plain,
        # we can get the result text here (see the FormPanel documentation for
        # further explanation).
        Window.alert(event.getResults())

    def onSubmit(self, event):
        # This event is fired just before the form is submitted. We can take
        # this opportunity to perform validation.
        if (self.tb.getText().length == 0):
            Window.alert("The text box must not be empty")
            event.setCancelled(true)


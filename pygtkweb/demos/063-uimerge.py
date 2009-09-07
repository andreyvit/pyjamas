#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk

class UIMergeExample:
    ui0 = '''<ui>
    <menubar name="MenuBar">
      <menu action="File">
        <menuitem action="Quit"/>
      </menu>
      <menu action="Sound">
        <menuitem action="Mute"/>
      </menu>
      <menu action="RadioBand">
        <menuitem action="AM"/>
        <menuitem action="FM"/>
        <menuitem action="SSB"/>
      </menu>
    </menubar>
    <toolbar name="Toolbar">
      <toolitem action="Quit"/>
      <separator/>
      <toolitem action="Mute"/>
      <separator name="sep1"/>
      <placeholder name="RadioBandItems">
        <toolitem action="AM"/>
        <toolitem action="FM"/>
        <toolitem action="SSB"/>
      </placeholder>
    </toolbar>
    </ui>'''
      
    ui1 = '''<ui>
    <menubar name="MenuBar">
      <menu action="File">
        <menuitem action="Save" position="top"/>
        <menuitem action="New" position="top"/>
      </menu>
      <menu action="Sound">
        <menuitem action="Loudness"/>
      </menu>
      <menu action="RadioBand">
        <menuitem action="CB"/>
        <menuitem action="Shortwave"/>
      </menu>
    </menubar>
    <toolbar name="Toolbar">
      <toolitem action="Save" position="top"/>
      <toolitem action="New" position="top"/>
      <separator/>
      <toolitem action="Loudness"/>
      <separator/>
      <placeholder name="RadioBandItems">
        <toolitem action="CB"/>
        <toolitem action="Shortwave"/>
      </placeholder>
    </toolbar>
    </ui>'''
      
    def __init__(self):
        # Create the toplevel window
        window = gtk.Window()
        window.connect('destroy', lambda w: gtk.main_quit())
        window.set_size_request(800, -1)
        vbox = gtk.VBox()
        window.add(vbox)

        self.merge_id = 0

        # Create a UIManager instance
        uimanager = gtk.UIManager()
        self.uimanager = uimanager

        # Add the accelerator group to the toplevel window
        accelgroup = uimanager.get_accel_group()
        window.add_accel_group(accelgroup)

        # Create the base ActionGroup
        actiongroup0 = gtk.ActionGroup('UIMergeExampleBase')

        actiongroup0.add_actions([('File', None, '_File'),
                                  ('Sound', None, '_Sound'),
                                  ('RadioBand', None, '_Radio Band')])
        uimanager.insert_action_group(actiongroup0, 0)

        # Create an ActionGroup
        actiongroup = gtk.ActionGroup('UIMergeExampleBase')
        self.actiongroup = actiongroup

        # Create a ToggleAction, etc.
        actiongroup.add_toggle_actions([('Mute', None, '_Mute', '<Control>m',
                                         'Mute the volume', self.mute_cb)])

        # Create actions
        actiongroup.add_actions([('Quit', gtk.STOCK_QUIT, '_Quit me!', None,
                                  'Quit the Program', self.quit_cb)])
        actiongroup.get_action('Quit').set_property('short-label', '_Quit')

        # Create some RadioActions
        actiongroup.add_radio_actions([('AM', None, '_AM', '<Control>a',
                                        'AM Radio', 0),
                                       ('FM', None, '_FM', '<Control>f',
                                        'FM Radio', 1),
                                       ('SSB', None, '_SSB', '<Control>b',
                                        'SSB Radio', 2),
                                       ], 0, self.radioband_cb)

        # Add the actiongroup to the uimanager
        uimanager.insert_action_group(actiongroup, 1)

        # Add a UI description
        merge_id = uimanager.add_ui_from_string(self.ui0)

        # Create another actiongroup and add actions
        actiongroup1 = gtk.ActionGroup('UIMergeExampleExtras')
        actiongroup1.add_toggle_actions([('Loudness', None, '_Loudness',
                                          '<Control>l', 'Loudness Control',
                                          self.loudness_cb)])
        actiongroup1.add_actions([('New', gtk.STOCK_NEW, None, None,
                                   'New Settings', self.new_cb),
                                  ('Save', gtk.STOCK_SAVE, None, None,
                                   'Save Settings', self.save_cb)])
        # Adding radioactions to existing radioactions requires setting the
        # group and making sure the values are unique and the actions are
        # not active
        actiongroup1.add_radio_actions([('CB', None, '_CB', '<Control>c',
                                         'CB Radio', 3),
                                       ('Shortwave', None, 'Short_wave',
                                        '<Control>w', 'Shortwave Radio', 4),
                                       ], 3, self.radioband_cb)
        group = actiongroup.get_action('AM').get_group()[0]
        action = actiongroup1.get_action('CB')
        action.set_group(group)
        action.set_active(False)
        action = actiongroup1.get_action('Shortwave')
        action.set_group(group)
        action.set_active(False)

        # Add the extra actiongroup to the uimanager
        uimanager.insert_action_group(actiongroup1, 2)

        # Create a MenuBar
        menubar = uimanager.get_widget('/MenuBar')
        vbox.pack_start(menubar, False)

        # Create a Toolbar
        toolbar = uimanager.get_widget('/Toolbar')
        vbox.pack_start(toolbar, False)

        # Create and pack two Labels
        label = gtk.Label('Sound is not muted')
        vbox.pack_start(label)
        self.mutelabel = label
        label = gtk.Label('Radio band is AM')
        vbox.pack_start(label)
        self.bandlabel = label

        # Create buttons to control visibility and sensitivity of actions
        buttonbox = gtk.HButtonBox()
        sensitivebutton = gtk.CheckButton('Sensitive')
        sensitivebutton.set_active(True)
        sensitivebutton.connect('toggled', self.toggle_sensitivity)
        visiblebutton = gtk.CheckButton('Visible')
        visiblebutton.set_active(True)
        visiblebutton.connect('toggled', self.toggle_visibility)
        mergebutton = gtk.CheckButton('Merged')
        mergebutton.set_active(False)
        mergebutton.connect('toggled', self.toggle_merged)
        # add them to buttonbox
        buttonbox.pack_start(sensitivebutton, False)
        buttonbox.pack_start(visiblebutton, False)
        buttonbox.pack_start(mergebutton, False)
        vbox.pack_start(buttonbox)
        print uimanager.get_ui()
        window.show_all()
        return

    def mute_cb(self, action):
        # action has not toggled yet
        text = ('muted', 'not muted')[action.get_active()==False]
        self.mutelabel.set_text('Sound is %s' % text)
        return

    def loudness_cb(self, action):
        # action has not toggled yet
        print 'Loudness toggled'
        return

    def radioband_cb(self, action, current):
        text = current.get_name()
        self.bandlabel.set_text('Radio band is %s' % text)
        return

    def new_cb(self, b):
        print 'New settings'
        return

    def save_cb(self, b):
        print 'Save settings'
        return

    def quit_cb(self, b):
        print 'Quitting program'
        gtk.main_quit()

    def toggle_sensitivity(self, b):
        self.actiongroup.set_sensitive(b.get_active())
        return

    def toggle_visibility(self, b):
        self.actiongroup.set_visible(b.get_active())
        return

    def toggle_merged(self, b):
        if self.merge_id:
            self.uimanager.remove_ui(self.merge_id)
            self.merge_id = 0
        else:
            self.merge_id = self.uimanager.add_ui_from_string(self.ui1)
            print 'merge id:', self.merge_id
        print self.uimanager.get_ui()
        return

if __name__ == '__main__':
    ba = UIMergeExample()
    gtk.main()

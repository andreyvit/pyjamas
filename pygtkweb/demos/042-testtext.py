#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

import pygtk
pygtk.require('2.0')
import sys, os, errno
import gtk
import pango


RESPONSE_FORWARD = 0
RESPONSE_BACKWARD = 1

book_closed_xpm = [
"16 16 6 1",
"       c None s None",
".      c black",
"X      c red",
"o      c yellow",
"O      c #808080",
"#      c white",
"                ",
"       ..       ",
"     ..XX.      ",
"   ..XXXXX.     ",
" ..XXXXXXXX.    ",
".ooXXXXXXXXX.   ",
"..ooXXXXXXXXX.  ",
".X.ooXXXXXXXXX. ",
".XX.ooXXXXXX..  ",
" .XX.ooXXX..#O  ",
"  .XX.oo..##OO. ",
"   .XX..##OO..  ",
"    .X.#OO..    ",
"     ..O..      ",
"      ..        ",
"                "]

def hsv_to_rgb(h, s, v):
    if s == 0.0:
        return (v, v, v)
    else:
        hue = h * 6.0
        saturation = s
        value = v

        if hue >= 6.0:
            hue = 0.0

        f = hue - int(hue)
        p = value * (1.0 - saturation)
        q = value * (1.0 - saturation * f)
        t = value * (1.0 - saturation * (1.0 - f))

        ihue = int(hue)
        if ihue == 0:
            return(value, t, p)
        elif ihue == 1:
            return(q, value, p)
        elif ihue == 2:
            return(p, value, t)
        elif ihue == 3:
            return(p, q, value)
        elif ihue == 4:
            return(t, p, value)
        elif ihue == 5:
            return(value, p, q)

def hue_to_color(hue):
    if hue > 1.0:
        raise ValueError

    h, s, v = hsv_to_rgb (hue, 1.0, 1.0)
    return (h*65535, s*65535, v*65535)

class FileSel(gtk.FileSelection):
    def __init__(self):
        gtk.FileSelection.__init__(self)
        self.result = False

    def ok_cb(self, button):
        self.hide()
        if self.ok_func(self.get_filename()):
            self.destroy()
            self.result = True
        else:
            self.show()

    def run(self, parent, title, start_file, func):
        if start_file:
            self.set_filename(start_file)

        self.ok_func = func
        self.ok_button.connect("clicked", self.ok_cb)
        self.cancel_button.connect("clicked", lambda x: self.destroy())
        self.connect("destroy", lambda x: gtk.main_quit())
        self.set_modal(True)
        self.show()
        gtk.main()
        return self.result

class Buffer(gtk.TextBuffer):
    N_COLORS = 16
    PANGO_SCALE = 1024

    def __init__(self):
        gtk.TextBuffer.__init__(self)
        tt = self.get_tag_table()
        self.refcount = 0
        self.filename = None
        self.untitled_serial = -1
        self.color_tags = []
        self.color_cycle_timeout_id = 0
        self.start_hue = 0.0

        for i in range(Buffer.N_COLORS):
            tag = self.create_tag()
            self.color_tags.append(tag)
  
        #self.invisible_tag = self.create_tag(None, invisible=True)
        self.not_editable_tag = self.create_tag(editable=False,
                                                foreground="purple")
        self.found_text_tag = self.create_tag(foreground="red")

        tabs = pango.TabArray(4, True)
        tabs.set_tab(0, pango.TAB_LEFT, 10)
        tabs.set_tab(1, pango.TAB_LEFT, 30)
        tabs.set_tab(2, pango.TAB_LEFT, 60)
        tabs.set_tab(3, pango.TAB_LEFT, 120)
        self.custom_tabs_tag = self.create_tag(tabs=tabs, foreground="green")
        TestText.buffers.push(self)

    def pretty_name(self):
        if self.filename:
            return os.path.basename(self.filename)
        else:
            if self.untitled_serial == -1:
                self.untitled_serial = TestText.untitled_serial
                TestText.untitled_serial += 1

            if self.untitled_serial == 1:
                return "Untitled"
            else:
                return "Untitled #%d" % self.untitled_serial

    def filename_set(self):
        for view in TestText.views:
            if view.text_view.get_buffer() == self:
                view.set_view_title()

    def search(self, str, view, forward):
        # remove tag from whole buffer
        start, end = self.get_bounds()
        self.remove_tag(self.found_text_tag, start, end)
  
        iter = self.get_iter_at_mark(self.get_insert())

        i = 0
        if str:
            if forward:
                while 1:
                    res = iter.forward_search(str, gtk.TEXT_SEARCH_TEXT_ONLY)
                    if not res:
                        break
                    match_start, match_end = res
                    i += 1
                    self.apply_tag(self.found_text_tag, match_start, match_end)
                    iter = match_end
            else:
                while 1:
                    res = iter.backward_search(str, gtk.TEXT_SEARCH_TEXT_ONLY)
                    if not res:
                        break
                    match_start, match_end = res
                    i += 1
                    self.apply_tag(self.found_text_tag, match_start, match_end)
                    iter = match_start

        dialog = gtk.MessageDialog(view,
                                   gtk.DIALOG_DESTROY_WITH_PARENT,
                                   gtk.MESSAGE_INFO,
                                   gtk.BUTTONS_OK,
                                   "%d strings found and marked in red" % i)

        dialog.connect("response", lambda x,y: dialog.destroy())
  
        dialog.show()

    def search_forward(self, str, view):
        self.search(str, view, True)

    def search_backward(self, str, view):
        self.search(str, view, False)

    def ref(self):
        self.refcount += 1

    def unref(self):
        self.refcount -= 1
        if self.refcount == 0:
            self.set_colors(False)
            TestText.buffers.remove(self)
            del self

    def color_cycle_timeout(self):
        self.cycle_colors()
        return True

    def set_colors(self, enabled):
        hue = 0.0

        if (enabled and self.color_cycle_timeout_id == 0):
            self.color_cycle_timeout_id = gtk.timeout_add(
                200, self.color_cycle_timeout)
        elif (not enabled and self.color_cycle_timeout_id != 0):
            gtk.timeout_remove(self.color_cycle_timeout_id)
            self.color_cycle_timeout_id = 0
    
        for tag in self.color_tags:
            if enabled:
                color = apply(TestText.colormap.alloc_color,
                              hue_to_color(hue))
                tag.set_property("foreground_gdk", color)
            else:
                tag.set_property("foreground_set", False)
            hue += 1.0 / Buffer.N_COLORS
      
    def cycle_colors(self):
        hue = self.start_hue
  
        for tag in self.color_tags:
            color = apply(TestText.colormap.alloc_color,
                          hue_to_color (hue))
            tag.set_property("foreground_gdk", color)

            hue += 1.0 / Buffer.N_COLORS
            if hue > 1.0:
                hue = 0.0

        self.start_hue += 1.0 / Buffer.N_COLORS
        if self.start_hue > 1.0:
            self.start_hue = 0.0

    def tag_event_handler(self, tag, widget, event, iter):
        char_index = iter.get_offset()
        tag_name = tag.get_property("name")
        if event.type == gtk.gdk.MOTION_NOTIFY:
            print "Motion event at char %d tag `%s'\n" % (char_index, tag_name)
        elif event.type == gtk.gdk.BUTTON_PRESS:
            print "Button press at char %d tag `%s'\n" % (char_index, tag_name)
        elif event.type == gtk.gdk._2BUTTON_PRESS:
            print "Double click at char %d tag `%s'\n" % (char_index, tag_name)
        elif event.type == gtk.gdk._3BUTTON_PRESS:
            print "Triple click at char %d tag `%s'\n" % (char_index, tag_name)
        elif event.type == gtk.gdk.BUTTON_RELEASE:
            print "Button release at char %d tag `%s'\n" % (char_index, tag_name)
        elif (event.type == gtk.gdk.KEY_PRESS or
              event.type == gtk.gdk.KEY_RELEASE):
            print "Key event at char %d tag `%s'\n" % (char_index, tag_name)

        return False

    def init_tags(self):
        colormap = TestText.colormap
        color = colormap.alloc_color(0, 0, 0xffff)
        tag = self.create_tag("fg_blue",
                                foreground_gdk=color,
                                background='yellow',
                                size_points=24.0)
        tag.connect("event", self.tag_event_handler)

        color = colormap.alloc_color(0xffff, 0, 0)
        tag = self.create_tag("fg_red",
                                rise= -4*Buffer.PANGO_SCALE,
                                foreground_gdk=color)
        tag.connect("event", self.tag_event_handler)

        color = colormap.alloc_color(0, 0xffff, 0)
        tag = self.create_tag("bg_green",
                                background_gdk=color,
                                size_points=10.0)
        tag.connect("event", self.tag_event_handler)

        tag = self.create_tag("strikethrough",
                                strikethrough=True)
        tag.connect("event", self.tag_event_handler)

        tag = self.create_tag("underline",
                                underline=pango.UNDERLINE_SINGLE)
        tag.connect("event", self.tag_event_handler)

        tag = self.create_tag("centered",
                                justification=gtk.JUSTIFY_CENTER)

        tag = self.create_tag("rtl_quote",
                                wrap_mode=gtk.WRAP_WORD,
                                direction=gtk.TEXT_DIR_RTL,
                                indent=30,
                                left_margin=20,
                                right_margin=20)

        tag = self.create_tag("negative_indent",
                                indent=-25)

    def fill_example_buffer(self):
        tagtable = self.get_tag_table()
        if not tagtable.lookup("fg_blue"):
            self.init_tags()
        iter = self.get_iter_at_offset(0)
        anchor = self.create_child_anchor(iter)
        self.set_data("anchor", anchor)
        pixbuf = gtk.gdk.pixbuf_new_from_xpm_data(book_closed_xpm)
        #pixbuf = gtk.gdk.pixbuf_new_from_file('book_closed.xpm')

        for i in range(100):
            iter = self.get_iter_at_offset(0)
            self.insert_pixbuf(iter, pixbuf)
          
            str = "%d Hello World! blah blah blah blah blah blah blah blah blah blah blah blah\nwoo woo woo woo woo woo woo woo woo woo woo woo woo woo woo\n" % i
            self.insert(iter, str)

            iter = self.get_iter_at_line_offset(0, 5)
            self.insert(iter,
                          "(Hello World!)\nfoo foo Hello this is some text we are using to text word wrap. It has punctuation! gee; blah - hmm, great.\nnew line with a significant quantity of text on it. This line really does contain some text. More text! More text! More text!\n"
                          "German (Deutsch Süd) Grüß Gott Greek (Ελληνικά) Γειά σας Hebrew(שלום) Hebrew punctuation(\xd6\xbfש\xd6\xbb\xd6\xbc\xd6\xbb\xd6\xbfל\xd6\xbcו\xd6\xbc\xd6\xbb\xd6\xbb\xd6\xbfם\xd6\xbc\xd6\xbb\xd6\xbf) Japanese (日本語) Thai (สวัสดีครับ) Thai wrong spelling (คำต่อไปนื่สะกดผิด พัั้ัั่งโกะ)\n")

            temp_mark = self.create_mark("tmp_mark", iter, True);

            iter = self.get_iter_at_line_offset(0, 6)
            iter2 = self.get_iter_at_line_offset(0, 13)
            self.apply_tag_by_name("fg_blue", iter, iter2)

            iter = self.get_iter_at_line_offset(1, 10)
            iter2 = self.get_iter_at_line_offset(1, 16)
            self.apply_tag_by_name("underline", iter, iter2)

            iter = self.get_iter_at_line_offset(1, 14)
            iter2 = self.get_iter_at_line_offset(1, 24)
            self.apply_tag_by_name("strikethrough", iter, iter2)
          
            iter = self.get_iter_at_line_offset(0, 9)
            iter2 = self.get_iter_at_line_offset(0, 16)
            self.apply_tag_by_name("bg_green", iter, iter2)
  
            iter = self.get_iter_at_line_offset(4, 2)
            iter2 = self.get_iter_at_line_offset(4, 10)
            self.apply_tag_by_name("bg_green", iter, iter2)

            iter = self.get_iter_at_line_offset(4, 8)
            iter2 = self.get_iter_at_line_offset(4, 15)
            self.apply_tag_by_name("fg_red", iter, iter2)

            iter = self.get_iter_at_mark(temp_mark)
            self.insert(iter, "Centered text!\n")
	  
            iter2 = self.get_iter_at_mark(temp_mark)
            self.apply_tag_by_name("centered", iter2, iter)

            self.move_mark(temp_mark, iter)
            self.insert(iter, "Word wrapped, Right-to-left Quote\n")
            self.insert(iter, "وقد بدأ ثلاث من أكثر المؤسسات تقدما في شبكة اكسيون برامجها كمنظمات لا تسعى للربح، ثم تحولت في السنوات الخمس الماضية إلى مؤسسات مالية منظمة، وباتت جزءا من النظام المالي في بلدانها، ولكنها تتخصص في خدمة قطاع المشروعات الصغيرة. وأحد أكثر هذه المؤسسات نجاحا هو »بانكوسول« في بوليفيا.\n")
            iter2 = self.get_iter_at_mark(temp_mark)
            self.apply_tag_by_name("rtl_quote", iter2, iter)

            self.insert_with_tags(iter,
                                    "Paragraph with negative indentation. blah blah blah blah blah. The quick brown fox jumped over the lazy dog.\n",
                                    self.get_tag_table().lookup("negative_indent"))
      
        print "%d lines %d chars\n" % (self.get_line_count(),
                                       self.get_char_count())

        # Move cursor to start
        iter = self.get_iter_at_offset(0)
        self.place_cursor(iter)
        self.set_modified(False)

    def fill_file_buffer(self, filename):
        try:
            f = open(filename, "r")
        except IOError, (errnum, errmsg):
            err = "Cannot open file '%s': %s" % (filename, errmsg)
            view = TestText.active_window_stack.get()
            dialog = gtk.MessageDialog(view, gtk.DIALOG_MODAL,
                                       gtk.MESSAGE_INFO,
                                       gtk.BUTTONS_OK, err);
            result = dialog.run()
            dialog.destroy()
            return False
  
        iter = self.get_iter_at_offset(0)
        buf = f.read()
        f.close()
        self.set_text(buf)
        self.set_modified(False)
        return True

    def save_buffer(self):
        result = False
        have_backup = False
        if not self.filename:
            return False

        bak_filename = self.filename + "~"
        try:
            os.rename(self.filename, bak_filename)
        except (OSError, IOError), (errnum, errmsg):
            if errnum != errno.ENOENT:
                err = "Cannot back up '%s' to '%s': %s" % (self.filename,
                                                           bak_filename,
                                                           errmsg)
                view = TestText.active_window_stack.get()
                dialog = gtk.MessageDialog(view, gtk.DIALOG_MODAL,
                                           gtk.MESSAGE_INFO,
                                           gtk.BUTTONS_OK, err);
                dialog.run()
                dialog.destroy()
                return False

        have_backup = True
        start, end = self.get_bounds()
        chars = self.get_slice(start, end, False)
        try:
            file = open(self.filename, "w")
            file.write(chars)
            file.close()
            result = True
            self.set_modified(False)
        except IOError, (errnum, errmsg):
            err = "Error writing to '%s': %s" % (self.filename, errmsg)
            view = TestText.active_window_stack.get()
            dialog = gtk.MessageDialog(view, gtk.DIALOG_MODAL,
                                       gtk.MESSAGE_INFO,
                                       gtk.BUTTONS_OK, err);
            dialog.run()
            dialog.destroy()

        if not result and have_backup:
            try:
                os.rename(bak_filename, self.filename)
            except OSError, (errnum, errmsg):
                err = "Can't restore backup file '%s' to '%s': %s\nBackup left as '%s'" % (
                    self.filename, bak_filename, errmsg, bak_filename)
                view = TestText.active_window_stack.get()
                dialog = gtk.MessageDialog(view, gtk.DIALOG_MODAL,
                                           gtk.MESSAGE_INFO,
                                           gtk.BUTTONS_OK, err);
                dialog.run()
                dialog.destroy()
  
        return result

    def save_as_ok_func(self, filename):
        old_filename = self.filename

        if (not self.filename or filename != self.filename):
            if os.path.exists(filename):
                err = "Ovewrite existing file '%s'?"  % filename
                view = TestText.active_window_stack.get()
                dialog = gtk.MessageDialog(view, gtk.DIALOG_MODAL,
                                           gtk.MESSAGE_QUESTION,
                                           gtk.BUTTONS_YES_NO, err);
                result = dialog.run()
                dialog.destroy()
                if result != gtk.RESPONSE_YES:
                    return False
  
        self.filename = filename

        if self.save_buffer():
            self.filename_set()
            return True
        else:
            self.filename = old_filename
            return False

    def save_as_buffer(self):
        return FileSel().run(self, "Save File", None, self.save_as_ok_func)

    def check_buffer_saved(self):
        if self.get_modified():
            pretty_name = self.pretty_name()
            msg = "Save changes to '%s'?" % pretty_name
            view = TestText.active_window_stack.get()
            dialog = gtk.MessageDialog(view, gtk.DIALOG_MODAL,
                                       gtk.MESSAGE_QUESTION,
                                       gtk.BUTTONS_YES_NO, msg);
            dialog.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
            result = dialog.run()
            dialog.destroy()
            if result == gtk.RESPONSE_YES:
                if self.filename:
                    return self.save_buffer()
                return self.save_as_buffer()
            elif result == gtk.RESPONSE_NO:
                return True
            else:
                return False
        else:
            return True

class View(gtk.Window):
    def __init__(self, buffer=None):
        menu_items = [
            ( "/_File", None, None, 0, "<Branch>" ),
            ( "/File/_New", "<control>N", self.do_new, 0, None ),
            ( "/File/New _View", None, self.do_new_view, 0, None ),
            ( "/File/_Open", "<control>O", self.do_open, 0, None ),
            ( "/File/_Save", "<control>S", self.do_save, 0, None ),
            ( "/File/Save _As...", None, self.do_save_as, 0, None ),
            ( "/File/sep1", None, None, 0, "<Separator>" ),
            ( "/File/_Close", "<control>W" , self.do_close, 0, None ),
            ( "/File/E_xit", "<control>Q" , self.do_exit, 0, None ),
            ( "/_Edit", None, None, 0, "<Branch>" ),
            ( "/Edit/Find...", None, self.do_search, 0, None ),
            ( "/_Settings", None, None, 0, "<Branch>" ),
            ( "/Settings/Wrap _Off", None, self.do_wrap_changed, gtk.WRAP_NONE, "<RadioItem>" ),
            ( "/Settings/Wrap _Words", None, self.do_wrap_changed, gtk.WRAP_WORD, "/Settings/Wrap Off" ),
            ( "/Settings/Wrap _Chars", None, self.do_wrap_changed, gtk.WRAP_CHAR, "/Settings/Wrap Off" ),
            ( "/Settings/sep1", None, None, 0, "<Separator>" ),
            ( "/Settings/Editable", None, self.do_editable_changed, True, "<RadioItem>" ),
            ( "/Settings/Not editable", None, self.do_editable_changed, False, "/Settings/Editable" ),
            ( "/Settings/sep1", None, None, 0, "<Separator>" ),
            ( "/Settings/Cursor visible", None, self.do_cursor_visible_changed, True, "<RadioItem>" ),
            ( "/Settings/Cursor not visible", None, self.do_cursor_visible_changed, False, "/Settings/Cursor visible" ),
            ( "/Settings/sep1", None, None, 0, "<Separator>" ),
            ( "/Settings/Left-to-Right", None, self.do_direction_changed, gtk.TEXT_DIR_LTR, "<RadioItem>" ),
            ( "/Settings/Right-to-Left", None, self.do_direction_changed, gtk.TEXT_DIR_RTL, "/Settings/Left-to-Right" ),
            ( "/Settings/sep1", None, None, 0, "<Separator>" ),
            ( "/Settings/Sane spacing", None, self.do_spacing_changed, False, "<RadioItem>" ),
            ( "/Settings/Funky spacing", None, self.do_spacing_changed, True, "/Settings/Sane spacing" ),
            ( "/Settings/sep1", None, None, 0, "<Separator>" ),
            ( "/Settings/Don't cycle color tags", None, self.do_color_cycle_changed, False, "<RadioItem>" ),
            ( "/Settings/Cycle colors", None, self.do_color_cycle_changed, True, "/Settings/Don't cycle color tags" ),
            ( "/_Attributes", None, None, 0, "<Branch>" ),
            ( "/Attributes/Editable", None, self.do_apply_editable, True, None ),
            ( "/Attributes/Not editable", None, self.do_apply_editable, False, None ),
            ( "/Attributes/Invisible", None, self.do_apply_invisible, False, None ),
            ( "/Attributes/Visible", None, self.do_apply_invisible, True, None ),
            ( "/Attributes/Custom tabs", None, self.do_apply_tabs, False, None ),
            ( "/Attributes/Default tabs", None, self.do_apply_tabs, True, None ),
            ( "/Attributes/Color cycles", None, self.do_apply_colors, True, None ),
            ( "/Attributes/No colors", None, self.do_apply_colors, False, None ),
            ( "/Attributes/Remove all tags", None, self.do_remove_tags, 0, None ),
            ( "/Attributes/Properties", None, self.do_properties, 0, None ),
            ( "/_Test", None, None, 0, "<Branch>" ),
            ( "/Test/_Example", None, self.do_example, 0, None ),
            ( "/Test/_Insert and scroll", None, self.do_insert_and_scroll, 0, None ),
            ( "/Test/_Add movable children", None, self.do_add_children, 0, None ),
            ( "/Test/A_dd focusable children", None, self.do_add_focus_children, 0, None ),
            ]

        if not buffer:
            buffer = Buffer()
        gtk.Window.__init__(self)

        TestText.views.push(self)

        buffer.ref()
  
        if not TestText.colormap:
            TestText.colormap = self.get_colormap()
  
        self.connect("delete_event", self.delete_event_cb)

        self.accel_group = gtk.AccelGroup()
        self.item_factory = gtk.ItemFactory(gtk.MenuBar, "<main>",
                                        self.accel_group)
        self.item_factory.set_data("view", self)
        self.item_factory.create_items(menu_items)

        self.add_accel_group(self.accel_group)

        vbox = gtk.VBox(False, 0)
        self.add(vbox)

        vbox.pack_start(self.item_factory.get_widget("<main>"),
                        False, False, 0)
  
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        self.text_view = gtk.TextView(buffer)
        self.text_view.set_wrap_mode(gtk.WRAP_WORD)

        # Make sure border width works, no real reason to do this other
        # than testing
        self.text_view.set_border_width(10)
  
        # Draw tab stops in the top and bottom windows.
        self.text_view.set_border_window_size(gtk.TEXT_WINDOW_TOP, 15)
        self.text_view.set_border_window_size(gtk.TEXT_WINDOW_BOTTOM, 15)

        self.text_view.connect("expose_event", self.tab_stops_expose)

        self.bhid = buffer.connect("mark_set", self.cursor_set_callback)
  
        # Draw line numbers in the side windows; we should really be
        # more scientific about what width we set them to.
        self.text_view.set_border_window_size(gtk.TEXT_WINDOW_RIGHT, 30)
        self.text_view.set_border_window_size(gtk.TEXT_WINDOW_LEFT, 30)

        self.text_view.connect("expose_event", self.line_numbers_expose)
  
        vbox.pack_start(sw, True, True, 0)
        sw.add(self.text_view)

        self.set_default_size(500, 500)
        self.text_view.grab_focus()

        self.set_view_title()
        self.init_menus()
        self.add_example_widgets()
  
        self.show_all()

    def delete_event_cb(self, window, event, data=None):
        TestText.active_window_stack.push(self)
        self.check_close_view()
        TestText.active_window_stack.pop()
        return True
    #
    # Menu callbacks
    #
    def get_empty_view(self):
        buffer = self.text_view.get_buffer()
        if (not buffer.filename and not buffer.get_modified()):
            return self
        else:
            return View(Buffer())

    def view_from_widget(widget):
        if isinstance(widget, gtk.MenuItem):
            item_factory = gtk.item_factory_from_widget(widget)
            return item_factory.get_data("view")
        else:
            app = widget.get_toplevel()
            return app.get_data("view")

    def do_new(self, callback_action, widget):
        View()

    def do_new_view(self, callback_action, widget):
        View(self.text_view.get_buffer())

    def open_ok_func(self, filename):
        new_view = self.get_empty_view()
        buffer = new_view.text_view.get_buffer()
        if not buffer.fill_file_buffer(filename):
            if new_view != self:
                new_view.close_view()
            return False
        else:
            buffer.filename = filename
            buffer.filename_set()
            return True;

    def do_open(self, callback_action, widget):
        FileSel().run(self, "Open File", None, self.open_ok_func)

    def do_save_as(self, callback_action, widget):
        TestText.active_window_stack.push(self)
        self.text_view.get_buffer().save_as_buffer()
        TestText.active_window_stack.pop()

    def do_save(self, callback_action, widget):
        TestText.active_window_stack.push(self)
        buffer = self.text_view.get_buffer()
        if not buffer.filename:
            self.do_save_as(callback_data, callback_action)
        else:
            buffer.save_buffer()
            TestText.active_window_stack.pop()

    def do_close(self, callback_action, widget):
        TestText.active_window_stack.push(self)
        self.check_close_view()
        TestText.active_window_stack.pop()

    def do_exit(self, callback_action, widget):
        TestText.active_window_stack.push(self)
        for tmp in TestText.buffers:
            if not tmp.check_buffer_saved():
                return

        gtk.main_quit()
        TestText.active_window_stack.pop()

    def do_example(self, callback_action, widget):
        new_view = self.get_empty_view()
        buffer = new_view.text_view.get_buffer()
        buffer.fill_example_buffer()

        new_view.add_example_widgets()

    def do_insert_and_scroll(self, callback_action, widget):
        buffer = self.text_view.get_buffer()

        start, end = buffer.get_bounds()
        mark = buffer.create_mark(None, end, False)

        buffer.insert(end,
                      "Hello this is multiple lines of text\n"
                      "Line 1\n"  "Line 2\n"
                      "Line 3\n"  "Line 4\n"
                      "Line 5\n")

        self.text_view.scroll_to_mark(mark, 0, True, 0.0, 1.0)
        buffer.delete_mark(mark)

    def do_wrap_changed(self, callback_action, widget):
        self.text_view.set_wrap_mode(callback_action)

    def do_direction_changed(self, callback_action, widget):
        self.text_view.set_direction(callback_action)
        self.text_view.queue_resize()

    def do_spacing_changed(self, callback_action, widget):
        if callback_action:
            self.text_view.set_pixels_above_lines(23)
            self.text_view.set_pixels_below_lines(21)
            self.text_view.set_pixels_inside_wrap(9)
        else:
            self.text_view.set_pixels_above_lines(0)
            self.text_view.set_pixels_below_lines(0)
            self.text_view.set_pixels_inside_wrap(0)

    def do_editable_changed(self, callback_action, widget):
        self.text_view.set_editable(callback_action)

    def do_cursor_visible_changed(self, callback_action, widget):
        self.text_view.set_cursor_visible(callback_action)

    def do_color_cycle_changed(self, callback_action, widget):
        self.text_view.get_buffer().set_colors(callback_action)

    def do_apply_editable(self, callback_action, widget):
        buffer = self.text_view.get_buffer()
        bounds = buffer.get_selection_bounds()
        if bounds:
            start, end = bounds
            if callback_action:
                buffer.remove_tag(buffer.not_editable_tag, start, end)
            else:
                buffer.apply_tag(buffer.not_editable_tag, start, end)

    def do_apply_invisible(self, callback_action, widget):
        buffer = self.text_view.get_buffer()
        bounds = buffer.get_selection_bounds()
        if bounds:
            start, end = bounds
            if callback_action:
                buffer.remove_tag(buffer.invisible_tag, start, end)
            else:
                buffer.apply_tag(buffer.invisible_tag, start, end)

    def do_apply_tabs(self, callback_action, widget):
        buffer = self.text_view.get_buffer()
        bounds = buffer.get_selection_bounds()
        if bounds:
            start, end = bounds
            if callback_action:
                buffer.remove_tag(buffer.custom_tabs_tag, start, end)
            else:
                buffer.apply_tag(buffer.custom_tabs_tag, start, end)

    def do_apply_colors(self, callback_action, widget):
        buffer = self.text_view.get_buffer()
        bounds = buffer.get_selection_bounds()
        if bounds:
            start, end = bounds
            if not callback_action:
                for tag in buffer.color_tags:
                    buffer.remove_tag(tag, start, end)
            else:
                tmp = buffer.color_tags
                i = 0
                next = start.copy()
                while next.compare(end) < 0:
                    next.forward_chars(2)
                    if next.compare(end) >= 0:
                        next = end

                    buffer.apply_tag(tmp[i], start, next)
                    i += 1
                    if i >= len(tmp):
                        i = 0
                    start = next.copy()

    def do_remove_tags(self, callback_action, widget):
        buffer = self.text_view.get_buffer()
        bounds = buffer.get_selection_bounds()
        if bounds:
            start, end = bounds
            buffer.remove_all_tags(start, end)

    def do_properties(self, callback_action, widget):
        #create_prop_editor(view.text_view, 0)
        pass

    def dialog_response_callback(self, dialog, response_id):
        if (response_id != RESPONSE_FORWARD and
            response_id != RESPONSE_BACKWARD):
            dialog.destroy()
            return
  
        start, end = dialog.buffer.get_bounds()
        search_string = start.get_text(end)

        print "Searching for `%s'\n" % search_string

        buffer = self.text_view.get_buffer()
        if response_id == RESPONSE_FORWARD:
            buffer.search_forward(search_string, self)
        elif response_id == RESPONSE_BACKWARD:
            buffer.search_backward(search_string, self)
    
        dialog.destroy()

    def do_search(self, callback_action, widget):
        search_text = gtk.TextView()
        dialog = gtk.Dialog("Search", self,
                            gtk.DIALOG_DESTROY_WITH_PARENT,
                            ("Forward", RESPONSE_FORWARD,
                             "Backward", RESPONSE_BACKWARD,
                             gtk.STOCK_CANCEL, gtk.RESPONSE_NONE))
        dialog.vbox.pack_end(search_text, True, True, 0)
        dialog.buffer = search_text.get_buffer()
        dialog.connect("response", self.dialog_response_callback)

        search_text.show()
        search_text.grab_focus()
        dialog.show_all()

    def movable_child_callback(self, child, event):
        text_view = self.text_view
        info = child.get_data("testtext-move-info")

        if not info:
            info = {}
            info['start_x'] = -1
            info['start_y'] = -1
            info['button'] = -1
            child.set_data("testtext-move-info", info)
  
        if event.type == gtk.gdk.BUTTON_PRESS:
            if info['button'] < 0:
                info['button'] = event.button
                info['start_x'] = child.allocation.x
                info['start_y'] = child.allocation.y
                info['click_x'] = child.allocation.x + event.x
                info['click_y'] = child.allocation.y + event.y
        elif event.type == gtk.gdk.BUTTON_RELEASE:
            if info['button'] < 0:
                return False

            if info['button'] == event.button:
                info['button'] = -1;
                # convert to window coords from event box coords
                x = info['start_x'] + (event.x + child.allocation.x \
                                       - info['click_x'])
                y = info['start_y'] + (event.y + child.allocation.y \
                                       - info['click_y'])
                text_view.move_child(child, x, y)
        elif gtk.gdk.MOTION_NOTIFY:
            if info['button'] < 0:
                return False
            x, y = child.get_pointer() # ensure more events
            # to window coords from event box coords
            x += child.allocation.x
            y += child.allocation.y
            x = info['start_x'] + (x - info['click_x'])
            y = info['start_y'] + (y - info['click_y'])
            text_view.move_child(child, x, y)

        return False

    def add_movable_child(self, text_view, window):
        label = gtk.Label("Drag me around")  
  
        event_box = gtk.EventBox()
        event_box.add_events(gtk.gdk.BUTTON_PRESS_MASK |
                             gtk.gdk.BUTTON_RELEASE_MASK |
                             gtk.gdk.POINTER_MOTION_MASK |
                             gtk.gdk.POINTER_MOTION_HINT_MASK)

        color = TestText.colormap.alloc_color(0xffff, 0, 0)
        event_box.modify_bg(gtk.STATE_NORMAL, color)
        event_box.add(label)
        event_box.show_all()

        event_box.connect("event", self.movable_child_callback)

        text_view.add_child_in_window(event_box, window, 0, 0)

    def do_add_children(self, callback_action, widget):
        text_view = self.text_view
        self.add_movable_child(text_view, gtk.TEXT_WINDOW_WIDGET)
        self.add_movable_child(text_view, gtk.TEXT_WINDOW_LEFT)
        self.add_movable_child(text_view, gtk.TEXT_WINDOW_RIGHT)
        self.add_movable_child(text_view, gtk.TEXT_WINDOW_TEXT)
        self.add_movable_child(text_view, gtk.TEXT_WINDOW_TOP)
        self.add_movable_child(text_view, gtk.TEXT_WINDOW_BOTTOM)

    def do_add_focus_children(self, callback_action, widget):
        text_view = self.text_view
  
        child = gtk.EventBox()
        b = gtk.Button("Button _A in widget.window")
        child.add(b)
        text_view.add_child_in_window(child, gtk.TEXT_WINDOW_WIDGET, 0, 200)

        child = gtk.EventBox()
        b = gtk.Button("Button _B in text.window")
        child.add(b)
        text_view.add_child_in_window(child, gtk.TEXT_WINDOW_TEXT, 50, 50)

        child = gtk.EventBox()
        b = gtk.Button("Button _T in top window")
        child.add(b)
        text_view.add_child_in_window(child, gtk.TEXT_WINDOW_TOP, 100, 0)

        child = gtk.EventBox()
        b = gtk.Button("Button _W in bottom window")
        child.add(b)
        text_view.add_child_in_window(child, gtk.TEXT_WINDOW_BOTTOM, 100, 0)

        child = gtk.EventBox()
        b = gtk.Button("Button _C in left window")
        child.add(b)
        text_view.add_child_in_window(child, gtk.TEXT_WINDOW_LEFT, 0, 50)

        child = gtk.EventBox()
        b = gtk.Button("Button _D in right window")
        child.add(b)
        text_view.add_child_in_window(child, gtk.TEXT_WINDOW_RIGHT, 0, 25)

        buffer = text_view.get_buffer()
        iter = buffer.get_start_iter()
        anchor = buffer.create_child_anchor(iter)
        child = gtk.Button("Button _E in buffer")
        text_view.add_child_at_anchor(child, anchor)

        anchor = buffer.create_child_anchor(iter)
        child = gtk.Button("Button _F in buffer")
        text_view.add_child_at_anchor(child, anchor)

        anchor = buffer.create_child_anchor(iter)
        child = gtk.Button("Button _G in buffer")
        text_view.add_child_at_anchor(child, anchor)

        # show all the buttons
        text_view.show_all()

    def init_menus(self):
        text_view = self.text_view
        direction = text_view.get_direction()
        wrap_mode = text_view.get_wrap_mode()
        menu_item = None

        if direction == gtk.TEXT_DIR_LTR:
            menu_item = self.item_factory.get_widget("/Settings/Left-to-Right")
        elif direction == gtk.TEXT_DIR_RTL:
            menu_item = self.item_factory.get_widget("/Settings/Right-to-Left")

        if menu_item:
            menu_item.activate()

        if wrap_mode == gtk.WRAP_NONE:
            menu_item = self.item_factory.get_widget("/Settings/Wrap Off")
        elif wrap_mode == gtk.WRAP_WORD:
            menu_item = self.item_factory.get_widget("/Settings/Wrap Words")
        elif wrap_mode == gtk.WRAP_CHAR:
            menu_item = self.item_factory.get_widget("/Settings/Wrap Chars")

        if menu_item:
            menu_item.activate()

    def close_view(self):
        TestText.views.remove(self)
        buffer = self.text_view.get_buffer()
        buffer.unref()
        buffer.disconnect(self.bhid)
        self.text_view.destroy()
        del self.text_view
        self.text_view = None
        self.destroy()
        del self
        if not TestText.views:
            gtk.main_quit()

    def check_close_view(self):
        buffer = self.text_view.get_buffer()
        if (buffer.refcount > 1 or
            buffer.check_buffer_saved()):
            self.close_view()

    def set_view_title(self):
        pretty_name = self.text_view.get_buffer().pretty_name()
        title = "testtext - " + pretty_name
        self.set_title(title)

    def cursor_set_callback(self, buffer, location, mark):
        # Redraw tab windows if the cursor moves
        # on the mapped widget (windows may not exist before realization...
  
        text_view = self.text_view
        if mark == buffer.get_insert():
            tab_window = text_view.get_window(gtk.TEXT_WINDOW_TOP)
            tab_window.invalidate_rect(None, False)
            #tab_window.invalidate_rect(tab_window.get_geometry()[:4], False)
      
            tab_window = text_view.get_window(gtk.TEXT_WINDOW_BOTTOM)
            tab_window.invalidate_rect(None, False)
            #tab_window.invalidate_rect(tab_window.get_geometry()[:4], False)

    def tab_stops_expose(self, widget, event):
        #print self, widget, event
        text_view = widget
  
        # See if this expose is on the tab stop window
        top_win = text_view.get_window(gtk.TEXT_WINDOW_TOP)
        bottom_win = text_view.get_window(gtk.TEXT_WINDOW_BOTTOM)

        if event.window == top_win:
            type = gtk.TEXT_WINDOW_TOP
            target = top_win
        elif event.window == bottom_win:
            type = gtk.TEXT_WINDOW_BOTTOM
            target = bottom_win
        else:
            return False

        first_x = event.area.x
        last_x = first_x + event.area.width

        first_x, y = text_view.window_to_buffer_coords(type, first_x, 0)
        last_x, y = text_view.window_to_buffer_coords(type, last_x, 0)

        buffer = text_view.get_buffer()
        insert = buffer.get_iter_at_mark(buffer.get_insert())
        attrs = gtk.TextAttributes()
        insert.get_attributes(attrs)

        tabslist = []
        in_pixels = False
        if attrs.tabs:
            tabslist = attrs.tabs.get_tabs()
            in_pixels = attrs.tabs.get_positions_in_pixels()
      
        for align, position in tabslist:
            if not in_pixels:
                position = pango.PIXELS(position)
      
            pos, y = text_view.buffer_to_window_coords(type, position, 0)
            target.draw_line(text_view.style.fg_gc[text_view.state],
                             pos, 0, pos, 15)

        return True

    def get_lines(self, first_y, last_y, buffer_coords, numbers):
        text_view = self.text_view
        # Get iter at first y
        iter, top = text_view.get_line_at_y(first_y)

        # For each iter, get its location and add it to the arrays.
        # Stop when we pass last_y
        count = 0
        size = 0

        while not iter.is_end():
            y, height = text_view.get_line_yrange(iter)
            buffer_coords.append(y)
            line_num = iter.get_line()
            numbers.append(line_num)
            count += 1
            if (y + height) >= last_y:
                break
            iter.forward_line()

        return count

    def line_numbers_expose(self, widget, event, user_data=None):
        text_view = widget
  
        # See if this expose is on the line numbers window
        left_win = text_view.get_window(gtk.TEXT_WINDOW_LEFT)
        right_win = text_view.get_window(gtk.TEXT_WINDOW_RIGHT)

        if event.window == left_win:
            type = gtk.TEXT_WINDOW_LEFT
            target = left_win
        elif event.window == right_win:
            type = gtk.TEXT_WINDOW_RIGHT
            target = right_win
        else:
            return False
  
        first_y = event.area.y
        last_y = first_y + event.area.height

        x, first_y = text_view.window_to_buffer_coords(type, 0, first_y)
        x, last_y = text_view.window_to_buffer_coords(type, 0, last_y)

        numbers = []
        pixels = []
        count = self.get_lines(first_y, last_y, pixels, numbers)
  
        # Draw fully internationalized numbers!
        layout = widget.create_pango_layout("")
  
        for i in range(count):
            x, pos = text_view.buffer_to_window_coords(type, 0, pixels[i])
            str = "%d" % numbers[i]
            layout.set_text(str)
            widget.style.paint_layout(target, widget.state, False,
                                      None, widget, None, 2, pos + 2, layout)

        # don't stop emission, need to draw children
        return False

    def add_example_widgets(self):
        buffer = self.text_view.get_buffer()
  
        anchor = buffer.get_data("anchor")

        if (anchor and not anchor.get_deleted()):
            widget = gtk.Button("Foo")
            self.text_view.add_child_at_anchor(widget, anchor)
            widget.show()

class Stack(list):
    def __init__(self):
        list.__init__(self)

    def push(self, item):
        self.insert(-1, item)

    def pop(self):
        del self[0]

    def get(self):
        return self[0]
    
class TestText:
    untitled_serial = 1
    colormap = None
    active_window_stack = Stack()
    buffers = Stack()
    views = Stack()

    def __init__(self, filelist):
        view = View()
        self.active_window_stack.push(view)
        for fname in filelist:
            filename = os.path.abspath(fname)
            view.open_ok_func(filename)
        self.active_window_stack.pop()

    def main(self):
        gtk.main()
        return 0

if __name__ == "__main__":
    testtext = TestText(sys.argv[1:])
    testtext.main()

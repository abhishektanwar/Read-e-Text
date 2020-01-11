#! /usr/bin/env python

import sys
import os
import zipfile
import gi
gi.require_version('Gtk','3.0')
from gi.repository import Gtk
from gi.repository import Gdk
import getopt
# gi.require_version('Pango','1.0')
from gi.repository import Pango

page = 0
PAGE_SIZE = 45

class ReadEtexts():

    def keypress_cb(self,widget,event):
        #handle up,down.left,right,+,-
        keyname = Gdk.keyval_name(event.keyval)
        if keyname == 'plus':
            self.font_increase()
            return True
        if keyname == 'minus':
            self.font_decrease()
            return True
        if keyname == 'Page_Up':
            self.page_previous()
            return True
        if keyname == 'Page_Down':
            self.page_next()
            return True
        if keyname == 'Up' or keyname == 'KP_Up':
            self.scroll_up()
            return True
        if keyname == 'Down' or keyname == 'KP_Down':
            self.scroll_down()
            return True
        return False

    def page_previous(self):
        global page
        #local value of page is use here
        #gobal value will be used outside page_previous()
        page = page - 1     
        if page<0:
            page=0
        self.show_page(page)
        v_adjustment = self.scrolled_window.get_vadjustment()
        v_adjustment_value = v_adjustment.get_upper() - v_adjustment.get_page_size()

    def page_next(self):
        global page
        page = page + 1
        if page >=(self.page_index):
            page = 0
        self.show_page(page)
        v_adjustment = self.scrolled_window.get_vadjustment()
        v_adjustment_value = v_adjustment.get_lower()

    def font_decrease(self):
        font_size = self.font_desc.get_size() / 1024
        font_size = font_size - 1
        if font_size < 1 :
            font_size = 1
        self.font_desc.set_size(font_size * 1024)
        self.textview.modify_font(self.font_desc)

    def font_increase(self):
        font_size = self.font_desc.get_size() / 1024
        font_size+=1
        self.font_desc.set_size(font_size * 1024)
        self.textview.modify_font(self.font_desc)
    
    def scroll_down(self):
        v_adjustment = self.scrolled_window.get_vadjustment()
        if v_adjustment.value == v_adjustment.get_upper() - v_adjustment.get_page_size():
            self.page_next()
            return
        if v_adjustment.value < v_adjustment.upper - v_adjustment.page_size:
            new_value = v_adjustment.get_value() + v_adjustment.get_step_increment()
            if new_value > v_adjustment.get_upper() - v_adjustment.page_size:
                new_value = v_adjustment.upper - v_adjustment.get_page_size()
            v_adjustment.set_value(new_value)

    def scroll_up(self):
        v_adjustment = self.scrolled_window.get_vadjustment()
        if v_adjustment.get_value() == v_adjustment.get_lower():
            self.page_previous()
        if v_adjustment.get_value() > v_adjustment.get_lower():
            new_value = v_adjustment.get_value()-v_adjustment.get_step_increment()
            if new_value > v_adjustment.get_lower():
                new_value = v_adjustment.get_lower()
            v_adjustment.set_value(new_value)

    def show_page(self,page_number):
        global PAGE_SIZE,current_word
        position = self.page_index[page_number]
        self.etext_file.seek(position)
        linecount = 0
        label_text = '\n\n\n'
        textbuffer = self.textview.get_buffer()
        # print textbuffer
        while linecount < PAGE_SIZE :
            line = self.etext_file.readline()
            label_text = label_text + unicode(line,'iso-8859-1')
            # print label_text
            linecount+=1
        label_text = label_text + '\n\n\n'
        textbuffer.set_text(label_text)
        self.textview.set_buffer(textbuffer)

    def save_extracted_file(self, zipfile, filename):
        "Extract the file to a temp directory for viewing"
        filebytes = zipfile.read(filename)
        f = open("/tmp/" + filename, 'w')
        try:
            f.write(filebytes)
        finally:
            f.close()

    def read_file(self, filename):
        "Read the Etext file"
        global PAGE_SIZE

        if zipfile.is_zipfile(filename):
            self.zf = zipfile.ZipFile(filename, 'r')
            self.book_files = self.zf.namelist()
            self.save_extracted_file(self.zf, self.book_files[0])
            currentFileName = "/tmp/" + self.book_files[0]
        else:
            currentFileName = filename

        self.etext_file = open(currentFileName,"r")
        self.page_index = [ 0 ]
        linecount = 0
        while self.etext_file:
            line = self.etext_file.readline()
            if not line:
                break
            linecount = linecount + 1
            if linecount >= PAGE_SIZE:
                position = self.etext_file.tell()
                self.page_index.append(position)
                linecount = 0
        if filename.endswith(".zip"):
            os.remove(currentFileName)

    def destroy_cb(self, widget, data=None):
        Gtk.main_quit()

    def main(self, file_path):
        # print file_path
        self.window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        self.window.connect("destroy", self.destroy_cb)
        self.window.set_title("Read Etexts")
        self.window.set_size_request(640, 480)
        self.window.set_border_width(0)
        self.read_file(file_path)
        self.scrolled_window = Gtk.ScrolledWindow(hadjustment=None,vadjustment=None)
        self.textview = Gtk.TextView()
        self.textview.set_editable(False)
        self.textview.set_left_margin(50)
        self.textview.set_cursor_visible(False)
        self.textview.connect("key_press_event", self.keypress_cb)
        self.font_desc = Pango.FontDescription("sans 12")
        self.textview.modify_font(self.font_desc)
        self.show_page(0)
        self.scrolled_window.add(self.textview)
        self.window.add(self.scrolled_window)
        self.textview.show()
        self.scrolled_window.show()
        self.window.show()
        Gtk.main()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage: %s <file>" % (sys.argv[0])
        sys.exit(1)
    try:
        opts, args = getopt.getopt(sys.argv[1:], "")
        # print sys.argv[1:]
        ReadEtexts().main(args[0])
    except getopt.error, msg:
        print msg
        print "This program has no options"
        sys.exit(2)
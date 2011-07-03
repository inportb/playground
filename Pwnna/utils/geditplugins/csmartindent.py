# -*- coding: utf-8 -*-
# Copyright (C) 2008 - Olivier Lauzanne
# Copyright (C) 2009 - Anton Mellit
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

# Modified by Shuhao Wu 2011
# Added support for PHP, and JavaScript

"""Gedit Plugin : smart indentation for Java/C/C++

Smart indentation for Java/C/C++. Based on the smart indentation plugin for python. 
Indents on '{', unindents on '}'.
"""

from gtk import gdk
import gedit

class Plugin(gedit.Plugin):
    """Smart indentation plugin
    """

    def activate(self, window):
        self.views = {}

    def deactivate(self, window):
        """Disconnect all signals.
        """
        for view, signal in self.views.items():
            view.disconnect(signal)

    def update_ui(self, window):
        """Connect the key-press-event signal of the current view to the
        on_key_press method if we are editing a python file.
        """
        buffer = window.get_active_document()
        view = window.get_active_view()

        if buffer == None or view == None:
            return

        language = buffer.get_language()
        if language == None:
            return

        if language.get_name() in ('Java', 'C++', 'C', 'JavaScript', 'PHP', 'C/C++/ObjC Header') and view not in self.views:
            self.views[view] = (view.connect('key-press-event',
                                self.on_key_press, buffer))

    def on_key_press(self, view, event, buffer):
        """Check if the key press is 'Return' or 'Backspace' and indent or
        un-indent accordingly.
        """
        key_name = gdk.keyval_name(event.keyval)
        if key_name not in ('Return', 'braceright', 'BackSpace') or \
           len(buffer.get_selection_bounds()) != 0:
            # If some text is selected we want the default behavior of Return
            # and Backspace so we do nothing
            return

        if view.get_insert_spaces_instead_of_tabs():
            self.indent = ' ' * view.props.tab_width
        else:
            self.indent = '\t'

        if key_name == 'Return':
            line = self._get_current_line(buffer)

            if line.endswith('{'):
                old_indent = line[:len(line) - len(line.lstrip())]
                indent = '\n' + old_indent + self.indent
                
                # Use insert_interactive instead of insert, so that the 
                # undo manager knows what we are doing (or something like that).
                # The True parameter is here because we are inserting into an
                # editable view
                buffer.insert_interactive_at_cursor(indent, True)
                self._scroll_to_cursor(buffer, view)
                return True
        elif key_name == 'braceright':
            line = self._get_current_line(buffer)

            if line.strip() == '' and line != '':
                length = len(self.indent)
                nb_to_delete = len(line) % length or length
                self._delete_before_cursor(buffer, nb_to_delete)
                self._scroll_to_cursor(buffer, view)
                return False
        elif key_name == 'BackSpace':
            line = self._get_current_line(buffer)

            if line.strip() == '' and line != '':
                length = len(self.indent)
                nb_to_delete = len(line) % length or length
                self._delete_before_cursor(buffer, nb_to_delete)
                self._scroll_to_cursor(buffer, view)
                return True

    def _delete_before_cursor(self, buffer, nb_to_delete):
        cursor_position = buffer.get_property('cursor-position')
        iter_cursor = buffer.get_iter_at_offset(cursor_position)
        iter_before = buffer.get_iter_at_offset(cursor_position - nb_to_delete)
        buffer.delete_interactive(iter_before, iter_cursor, True)

    def _get_current_line(self, buffer):
        iter_cursor = self._get_iter_cursor(buffer)
        iter_line = buffer.get_iter_at_line(iter_cursor.get_line())
        return buffer.get_text(iter_line, iter_cursor)

    def _get_current_line_nb(self, buffer):
        iter_cursor = self._get_iter_cursor(buffer)
        return iter_cursor.get_line()

    def _get_iter_cursor(self, buffer):
        cursor_position = buffer.get_property('cursor-position')
        return buffer.get_iter_at_offset(cursor_position)

    def _scroll_to_cursor(self, buffer, view):
        lineno = self._get_current_line_nb(buffer) + 1
        insert = buffer.get_insert()
        view.scroll_mark_onscreen(insert)


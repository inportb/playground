import gedit, gtk, gtk.glade
import os
from xml.dom import minidom

ui_str="""<ui>
<menubar name="MenuBar">
	<menu name="ProjectMenu" action="ProjectMenuAction">
		<placeholder name="ProjectOps_1">
			<menuitem name="NewProject" action="NewProjectAction"/>
		</placeholder>
		<placeholder name="ProjectOps_2">
			<menuitem name="OpenProject" action="OpenProjectAction"/>
			<menuitem name="OpenLastProjectMenu" action="OpenLastProjectMenuAction"/>
			<menuitem name="CloseProject" action="CloseProjectAction"/>
			<separator />
			<menuitem name="OpenFileAsProject" action="OpenFileAsProjectAction"/>
			<separator />
			<menuitem name="ViewProjectFiles" action="ViewProjectFilesAction"/>
			<menuitem name="ReopenAllFiles" action="ReopenAllFilesAction"/>
			<separator />
		</placeholder>
		<placeholder name="ProjectOps_3">
			<menuitem name="AddProjectFile" action="AddProjectFileAction"/>
			<menuitem name="AddCurrentFile" action="AddCurrentFileAction"/>
			<menuitem name="DelProjectFile" action="DelProjectFileAction"/>
			<separator />
		</placeholder>
		<placeholder name="ProjectOps_4">
			<menuitem name="OpenCurrentFileFolder" action="OpenCurrentFileFolderAction"/>
			<menuitem name="OpenProjectFolder" action="OpenProjectFolderAction"/>
			<separator />
		</placeholder>
		<placeholder name="ProjectOps_5">
		</placeholder>
	</menu>
</menubar>
<toolbar name="ToolBar">
    <separator />
    <toolitem name="OpenLastProjectButton" action="OpenLastProjectButtonAction"/>
</toolbar> 
</ui>
"""
class ProjectData:

	def __init__( self ):
		self.filename = ""
		self._files = list()
		self.active = False

	def add_file( self, filename ):
		if filename in self._files:
				return False
		self._files.append( filename )
		print "Adding file to project ... " + filename
		return True

	def del_file( self, filename ):
		if filename in self._files:
			self._files.remove( filename )
			return True
		return False

	def get_files( self ):
		return self._files

	def clear( self ):
		self.name = ""
		self.filename = ""
		self._files = list()
		self.active = False

class ProjectPluginInstance:
	CHOOSER_OPEN = 10
	CHOOSER_SAVE = 11
	CHOOSER_CANCEL = 12
	CHOOSER_NEW = 13
	CHOOSER_OK = 14
	OPEN_PROJECT = 20
	SAVE_PROJECT = 21
	NEW_PROJECT = 22
	OPEN_FILES = 23
	SAVE_FILE = 24
	SAVE_AND_CLOSE_FILE = 25
	WITH_LOG = True
	MAX_HISTORY_FILE_NO = 15
	STATE_PROJECT_NO_FILES_NO	= 0
	STATE_PROJECT_YES_FILES_NO	= 1
	STATE_PROJECT_NO_FILES_YES	= 2
	STATE_PROJECT_YES_FILES_YES = 3
	
	CAN_ADD_FILE = 1
	CAN_REM_FILE = 2
	
	OS_WINDOW_MANAGER = "nautilus"

	def __init__( self, plugin, window ):
		self._window = window
		self._plugin = plugin
		self._encoding = gedit.gedit_encoding_get_current()
		self._project = ProjectData()
		self._history_file = os.path.expanduser( '~' ) + "/.gnome2/gedit/plugins/gedit-project-manager-history"
		self._history = list()
		self._action_group = gtk.ActionGroup( "ProjectPluginActions" )
		self._history_action_group = gtk.ActionGroup( "ProjectPluginHistoryActions" )
		self._state = self.STATE_PROJECT_NO_FILES_NO
		self._add_remove_state = None
		self._message = list()
		
		self._init_history()
		self._insert_menu()
		self._create_choosers()

	def deactivate( self ):
		self._remove_menu()
		self._save_history()
		self._action_group = None
		self._window = None
		self._plugin = None
		self._project = None

		self._open_file_chooser = None
		self._save_file_chooser = None

	def update_ui( self ):
		manager = self._window.get_ui_manager()
		# REMOVE OLD HISTORY
		manager.remove_ui( self._ui_id )
		manager.add_ui_from_string( ui_str )
		manager.remove_action_group(self._history_action_group)
		self._history_action_group = gtk.ActionGroup( "ProjectPluginHistoryActions" )
		manager.ensure_update()
		# INSERT NEW HISTORY
		if len(self._history) != 0:
			for item in self._history:
				if item.strip() != "":
					self._insert_history_menu_item( manager, item, self._history.index( item ) )
		manager.insert_action_group( self._history_action_group, 1 )
		manager.ensure_update()
		# SET BUTTONS SENSITIVITY
		self._add_remove_state = None
		if (self._window.get_active_document() and self._window.get_active_document().get_uri() != None):
			if (self._project.active):
				self._state = self.STATE_PROJECT_YES_FILES_YES
				if (self._window.get_active_document().get_data( "BelongsToProject" ) == self._project.filename):   #GYLL...
					self._add_remove_state = self.CAN_REM_FILE
				else:
					self._add_remove_state = self.CAN_ADD_FILE
			else:
				self._state = self.STATE_PROJECT_NO_FILES_YES
		else:
			if (self._project.active):
				self._state = self.STATE_PROJECT_YES_FILES_NO
			else:
				self._state = self.STATE_PROJECT_NO_FILES_NO
		self._set_menu_state( manager )
		#print self._window.gedit_notebook
		#print self._state
		return

	def _set_menu_state( self, manager ):
		print "In _set_menu_state"
		manager.get_action("/MenuBar/ProjectMenu/ProjectOps_1/NewProject").set_sensitive( not self._project.active )
		manager.get_action("/MenuBar/ProjectMenu/ProjectOps_2/OpenProject").set_sensitive( not self._project.active )

		#GYLL
		manager.get_action("/MenuBar/ProjectMenu/ProjectOps_2/OpenFileAsProject").set_sensitive( False )
		if (not self._project.active):
			if self._window.get_active_document() and self._window.get_active_document().get_uri():
				if  self._has_gedit_project_extension(self._window.get_active_document().get_uri().strip()):
					manager.get_action("/MenuBar/ProjectMenu/ProjectOps_2/OpenFileAsProject").set_sensitive( True )

		#GYLL
		manager.get_action("/ToolBar/OpenLastProjectButton").set_sensitive( len(self._history) != 0 and not self._project.active)
		#GYLL
		manager.get_action("/MenuBar/ProjectMenu/ProjectOps_2/OpenLastProjectMenu").set_sensitive( len(self._history) != 0 and not self._project.active)

		if (self._state == self.STATE_PROJECT_NO_FILES_NO):
				manager.get_action("/MenuBar/ProjectMenu/ProjectOps_2/CloseProject").set_sensitive(False)
				manager.get_action("/MenuBar/ProjectMenu/ProjectOps_2/ViewProjectFiles").set_sensitive(False)
				manager.get_action("/MenuBar/ProjectMenu/ProjectOps_3/AddProjectFile").set_sensitive(False)
				manager.get_action("/MenuBar/ProjectMenu/ProjectOps_3/AddCurrentFile").set_sensitive(False)
				manager.get_action("/MenuBar/ProjectMenu/ProjectOps_2/ReopenAllFiles").set_sensitive(False)
				manager.get_action("/MenuBar/ProjectMenu/ProjectOps_3/DelProjectFile").set_sensitive(False)
				manager.get_action("/MenuBar/ProjectMenu/ProjectOps_4/OpenProjectFolder").set_sensitive(False)
				manager.get_action("/MenuBar/ProjectMenu/ProjectOps_4/OpenCurrentFileFolder").set_sensitive(False)
		elif (self._state == self.STATE_PROJECT_YES_FILES_NO):
				manager.get_action("/MenuBar/ProjectMenu/ProjectOps_2/CloseProject").set_sensitive(True)
				manager.get_action("/MenuBar/ProjectMenu/ProjectOps_2/ViewProjectFiles").set_sensitive(True)
				manager.get_action("/MenuBar/ProjectMenu/ProjectOps_3/AddProjectFile").set_sensitive(True)
				manager.get_action("/MenuBar/ProjectMenu/ProjectOps_3/AddCurrentFile").set_sensitive(False)
				manager.get_action("/MenuBar/ProjectMenu/ProjectOps_2/ReopenAllFiles").set_sensitive(True)
				manager.get_action("/MenuBar/ProjectMenu/ProjectOps_3/DelProjectFile").set_sensitive(False)
				manager.get_action("/MenuBar/ProjectMenu/ProjectOps_4/OpenProjectFolder").set_sensitive(True)
				manager.get_action("/MenuBar/ProjectMenu/ProjectOps_4/OpenCurrentFileFolder").set_sensitive(False)
		elif (self._state == self.STATE_PROJECT_NO_FILES_YES):
				manager.get_action("/MenuBar/ProjectMenu/ProjectOps_2/CloseProject").set_sensitive(False)
				manager.get_action("/MenuBar/ProjectMenu/ProjectOps_2/ViewProjectFiles").set_sensitive(False)
				manager.get_action("/MenuBar/ProjectMenu/ProjectOps_3/AddProjectFile").set_sensitive(False)
				manager.get_action("/MenuBar/ProjectMenu/ProjectOps_3/AddCurrentFile").set_sensitive(False)
				manager.get_action("/MenuBar/ProjectMenu/ProjectOps_2/ReopenAllFiles").set_sensitive(False)
				manager.get_action("/MenuBar/ProjectMenu/ProjectOps_3/DelProjectFile").set_sensitive(False)
				manager.get_action("/MenuBar/ProjectMenu/ProjectOps_4/OpenProjectFolder").set_sensitive(False)
				manager.get_action("/MenuBar/ProjectMenu/ProjectOps_4/OpenCurrentFileFolder").set_sensitive(True)
		elif (self._state == self.STATE_PROJECT_YES_FILES_YES):
				manager.get_action("/MenuBar/ProjectMenu/ProjectOps_2/CloseProject").set_sensitive(True)
				manager.get_action("/MenuBar/ProjectMenu/ProjectOps_2/ViewProjectFiles").set_sensitive(True)
				manager.get_action("/MenuBar/ProjectMenu/ProjectOps_3/AddProjectFile").set_sensitive(True)
				if (self._add_remove_state == self.CAN_ADD_FILE):
        				manager.get_action("/MenuBar/ProjectMenu/ProjectOps_3/AddCurrentFile").set_sensitive(True)
        			else:
        				manager.get_action("/MenuBar/ProjectMenu/ProjectOps_3/AddCurrentFile").set_sensitive(False)
				manager.get_action("/MenuBar/ProjectMenu/ProjectOps_2/ReopenAllFiles").set_sensitive(True)
				if (self._add_remove_state == self.CAN_REM_FILE):
        				manager.get_action("/MenuBar/ProjectMenu/ProjectOps_3/DelProjectFile").set_sensitive(True)
        			else:
        				manager.get_action("/MenuBar/ProjectMenu/ProjectOps_3/DelProjectFile").set_sensitive(False)
				manager.get_action("/MenuBar/ProjectMenu/ProjectOps_4/OpenProjectFolder").set_sensitive(True)
				manager.get_action("/MenuBar/ProjectMenu/ProjectOps_4/OpenCurrentFileFolder").set_sensitive(True)

	def _init_history( self ):
		if os.path.exists( self._history_file ) == True:
			hist_fp = open( self._history_file, "r" )
			try:
				for line in hist_fp:
					self._history.insert( len( self._history ) , line.strip() )
			finally:
				hist_fp.close()
		else:
			hist_fp = open( self._history_file, "w" )
			hist_fp.close()

	def _add_to_history( self, filename ):
		if filename.strip() != "":
			for item in self._history:
				if item == filename:
					self._history.remove( item )
			if os.path.exists(filename):
				if len( self._history ) == self.MAX_HISTORY_FILE_NO:
					self._history.pop( len( self._history )-1 )
				self._history.insert( 0, filename )
			self._save_history()
			self.update_ui()      # GYLL


	def _save_history( self ):
		print "Saving the history ... "
		hist_fp = open( self._history_file, "w" )
		for line in self._history:
			hist_fp.write( line + "\n" )
		hist_fp.close()

	def _insert_history_menu_item ( self, manager, filename, position ):
		file_name, file_ext = os.path.splitext( os.path.basename( filename ) )
		action_label = str( position + 1 ) + ". " + file_name
		manager.add_ui(	merge_id = self._ui_id,
						path = "/MenuBar/ProjectMenu/ProjectOps_5",
						name = filename,
						action = filename,
						type = gtk.UI_MANAGER_AUTO,
						top = False)
		history_action = gtk.Action(name = filename,
									label = action_label,
									tooltip=filename,
									stock_id=None )
		history_action.connect("activate", lambda a: self.on_history_action(filename) )
		history_action.set_sensitive( not self._project.active )
		history_action.set_visible(True)
		self._history_action_group.add_action( history_action )

	def _insert_menu( self ):
		"create and add the Project menu to the menubar"
		manager = self._window.get_ui_manager()

		project_menu_action = gtk.Action( name="ProjectMenuAction",
                                          label="Project",
                                          tooltip="Project menu",
                                          stock_id=None )
		project_menu_action.connect( "activate", lambda a: self.update_ui() )
		self._action_group.add_action( project_menu_action )

		#GYLL : reopen last project button
		open_last_project_button_action = gtk.Action( name="OpenLastProjectButtonAction",
                                          label="Last Project",
                                          tooltip="Reopen the last project",
                                          stock_id=gtk.STOCK_GO_BACK )
		open_last_project_button_action.connect( "activate", lambda a: self.on_open_last_project_action() )
		self._action_group.add_action( open_last_project_button_action )

		#GYLL : reopen last project menu
		open_last_project_menu_action = gtk.Action( name="OpenLastProjectMenuAction",
                                          label="Open Last Project",
                                          tooltip="Reopen the last project",
                                          stock_id=gtk.STOCK_GO_BACK )
		open_last_project_menu_action.connect( "activate", lambda a: self.on_open_last_project_action() )
		self._action_group.add_action( open_last_project_menu_action )



		## First Placeholder ##
		new_project_action = gtk.Action(	name="NewProjectAction",
											label="New Project...\t",
											tooltip="Create a new project",
											stock_id=gtk.STOCK_NEW )
		new_project_action.connect( "activate", lambda a: self.on_new_project_action() )
		self._action_group.add_action( new_project_action )

		## Second Placeholder ##
		open_project_action = gtk.Action( name="OpenProjectAction",
                                          label="Open Project...\t",
                                          tooltip="Open a project file",
                                          stock_id=gtk.STOCK_OPEN )
		open_file_as_project_action = gtk.Action( name="OpenFileAsProjectAction",   #GYLL
                                          label="Open Current File as Project\t",
                                          tooltip="Open the project associated with the current '.gedit-project' file",
                                          stock_id=None )
		close_project_action = gtk.Action( name="CloseProjectAction",
                                           label="Close Project\t",
                                           tooltip="Closes the current project",
                                           stock_id=gtk.STOCK_QUIT )
		view_project_files_action = gtk.Action( name="ViewProjectFilesAction",
                                           label="View Project File List\t",
                                           tooltip="Displays a list with the files in the project.",
                                           stock_id=gtk.STOCK_INFO)
		open_all_files_action = gtk.Action( name="ReopenAllFilesAction",
                                      label="Open All Files In Project\t",
                                      tooltip="Opens all the files contained in the current project",
                                      stock_id=gtk.STOCK_REFRESH )
		open_project_action.connect( "activate", lambda a: self.on_open_project_action() )
		open_file_as_project_action.connect( "activate", lambda a: self.on_open_file_as_project_action() )
		close_project_action.connect( "activate", lambda a: self.on_close_project_action() )
		view_project_files_action.connect( "activate", lambda a: self.on_view_project_files_action() )
		open_all_files_action.connect( "activate", lambda a: self.on_open_all_files_action() )

		self._action_group.add_action( open_project_action )
		self._action_group.add_action( open_file_as_project_action )
		self._action_group.add_action( close_project_action )
		self._action_group.add_action_with_accel( view_project_files_action, "<Ctrl>3" )
		self._action_group.add_action_with_accel( open_all_files_action, "<Ctrl>2" )
		
		# Third Placeholder ##
		add_file_action = gtk.Action( name="AddProjectFileAction",
                                      label="Add Files ...\t",
                                      tooltip="Adds an existing file to the opened project",
                                      stock_id=gtk.STOCK_DND_MULTIPLE )
		add_current_file_action = gtk.Action( name="AddCurrentFileAction",
                                      label="Add Current File\t",
                                      tooltip="Adds the current file to the opened project",
                                      stock_id=gtk.STOCK_DND )
		del_file_action = gtk.Action( name="DelProjectFileAction",
                                      label="Remove Current File\t",
                                      tooltip="Removes the active file from the project",
                                      stock_id=gtk.STOCK_DELETE )
		add_file_action.connect( "activate", lambda a: self.on_add_file_action() )
		add_current_file_action.connect( "activate", lambda a: self.on_add_current_file_action() )
		del_file_action.connect( "activate", lambda a: self.on_del_file_action() )
		self._action_group.add_action( add_file_action )
		self._action_group.add_action_with_accel( add_current_file_action, "<Ctrl>1" )
		self._action_group.add_action_with_accel( del_file_action, "<Ctrl>0" )
		
		## Fourth Placeholder ##
		open_project_folder_action = gtk.Action( name="OpenProjectFolderAction",
                                             label="Open Project File Folder...\t",
                                             tooltip="Open the folder containing the project file.",
                                             stock_id=None )
		open_file_folder_action = gtk.Action( name="OpenCurrentFileFolderAction",
                                             label="Open Current File Folder...\t",
                                             tooltip="Open the current project's folder.",
                                             stock_id=None )

		open_project_folder_action.connect( "activate", lambda a: self.on_open_project_folder_action() )
		open_file_folder_action.connect( "activate", lambda a: self.on_open_files_folder_action() )
		self._action_group.add_action( open_project_folder_action )
		self._action_group.add_action( open_file_folder_action )

		manager.insert_action_group( self._action_group, 0 )
		manager.insert_action_group( self._history_action_group, 1 )
		
		self._ui_id = manager.new_merge_id()
		manager.add_ui_from_string( ui_str )
		manager.ensure_update()

	def _remove_menu( self ):
		"removes the project menu items from the menu"
		manager = self._window.get_ui_manager()
		manager.remove_ui( self._ui_id )
		manager.remove_action_group( self._action_group )
		manager.ensure_update()

	def _create_choosers( self ):
		"Creates open/save file choosers for opening and saving projects"
		self.project_file_filter = gtk.FileFilter()
		self.project_file_filter.add_pattern("*.gedit-project")
		self.all_files_filter = gtk.FileFilter()
		self.all_files_filter.add_pattern("*")

		self._open_file_chooser = gtk.FileChooserDialog( "Open Project File",
                                                         self._window,
                                                         gtk.FILE_CHOOSER_ACTION_OPEN )
		self._open_file_chooser.set_select_multiple( False )
		self._open_file_chooser.add_buttons( gtk.STOCK_OPEN, self.CHOOSER_OPEN,
                                             gtk.STOCK_CANCEL, self.CHOOSER_CANCEL )

		self._save_file_chooser = gtk.FileChooserDialog( "Save Project File",
                                                         self._window,
                                                         gtk.FILE_CHOOSER_ACTION_SAVE )
		self._save_file_chooser.set_select_multiple( False )
		self._save_file_chooser.add_buttons( gtk.STOCK_SAVE, self.CHOOSER_SAVE,
                                             gtk.STOCK_CANCEL, self.CHOOSER_CANCEL )

		self._open_fa_id = -1
		self._open_resp_id = -1
		self._save_fa_id = -1
		self._save_resp_id = -1

	#### MENU ITEM ACTIONS ####

	## First Placeholder ##
	def on_new_project_action( self ):
		"Displays the new project dialog box"
		self._show_chooser( self.NEW_PROJECT )

	## Second Placeholder ##
	def on_open_project_action( self ):
		"Activated when the 'open project' menu item is selected"
		self._show_chooser( self.OPEN_PROJECT )

	def on_close_project_action( self ):
		"Close the active project"
		project_filename = os.path.basename(self._project.filename)  #GYLL
		self._save_project( self._project.filename )
#GYLL		self._show_alert( "Project closed: '" + self._project.filename + "'", self.WITH_LOG )
		self._close_project()
		if self._message: self._show_alert( "Project closed: '" + project_filename + "'", self.WITH_LOG )  #GYLL

	def on_view_project_files_action( self ):
		file_list = list()
		xml = minidom.parse( self._project.filename )
		for subfile in xml.getElementsByTagName( 'file' ):
			file_list.append( subfile.childNodes[0].data.strip() )
#GYLL		message = "Current project: '/" + os.path.basename(self._project.filename) + "'\nFiles in the project:"
		message = "Current project:\n" + self._project.filename + "\n\nFiles in the project:"   #GYLL
		while file_list:
			message = message + "\n - /" + file_list.pop().strip("file:/").replace("%20", " ")
		self._show_alert( message , False, gtk.DIALOG_DESTROY_WITH_PARENT )

	def on_open_project_folder_action( self ):
		"Open the current project folder."
		if os.path.dirname(self._project.filename):
#GYLL			os.system(self.OS_WINDOW_MANAGER + " " + os.path.dirname(self._project.filename))
			os.system(self.OS_WINDOW_MANAGER + " file://" + os.path.dirname(self._project.filename).replace(" ","%20"))   #GYLL
		else:
			self._show_alert( "Can not open the project folder.\nReason: Path not found." )

	def on_open_files_folder_action( self ):
		"Open the current file folder."
		if (self._window.get_active_document()):
			if(self._window.get_active_document().get_uri()):
				current_file = self._window.get_active_document().get_uri().strip()
				if os.path.dirname(current_file):
					os.system( self.OS_WINDOW_MANAGER + " " + os.path.dirname(current_file))
				else:
					self._show_alert( "Can not open the project folder.\nReason: Path not found." )
		else:
			self._show_alert( "There is no open file or the current file is untitled." )

	## Third Placeholder ##
	def on_add_file_action( self ):
		"Adds an existing file to the active project."
		self._show_chooser( self.OPEN_FILES )

	def on_add_current_file_action( self ):
		"Adds the active file to the active project."
		if self._window.get_active_document():
			doc = self._window.get_active_document()
			print "Adding file to project ... " + doc.get_uri()
#GYLL			if doc.get_uri() in self._project._files:
			if doc.get_data( "BelongsToProject" ) == self._project.filename:
				self._show_alert( "The current file is ALREADY IN the project: '/" +
									doc.get_uri().lstrip("file:/").replace("%20"," ") + "'")
			else:
				doc.set_data( "BelongsToProject", self._project.filename )   #GYLL
				self._show_alert( "The current file has been ADDED to the project: '/" +
									doc.get_uri().lstrip("file:/").replace("%20"," ") + "'")
#GYLL			if not doc.get_data( "BelongsToProject" ): doc.set_data( "BelongsToProject", self._project.filename )
			self._project.add_file( doc.get_uri() )
			self._save_project( self._project.filename )
	
	def on_open_all_files_action( self ):
		self._open_project( self._project.filename )
		self._save_project( self._project.filename )
		if self._message: self._show_alert( "Project reopened: '" + os.path.basename( self._project.filename ) + "'", self.WITH_LOG )
	
	def on_del_file_action( self ):
		"Removes the active file from the active project."
		if self._window.get_active_document():
			doc = self._window.get_active_document()
			if doc.get_data( "BelongsToProject" ) == self._project.filename:
				print "Removing file from project ... " + doc.get_uri()
				self._project.del_file( doc.get_uri().strip() )
				#self._window.close_tab( gedit.gedit_tab_get_from_document( doc ) )
				self._save_project( self._project.filename )
				doc.set_data( "BelongsToProject", None )     #GYLL
				self._show_alert( "The current file has been REMOVED from the project: '/" +
									doc.get_uri().lstrip("file:/").replace("%20"," ") + "'")
			else:
				self._show_alert( "The current file doesn't belong to project: '/" +
									doc.get_uri().lstrip("file:/").replace("%20"," ") + "'")

	## CHOOSER ACTIONS ##
	def _show_chooser( self, chooser_type ):
		"A unified interface to show both open/save file choosers"
		if self._open_fa_id > -1: self._open_file_chooser.disconnect( self._open_fa_id )
		if self._open_resp_id > -1: self._open_file_chooser.disconnect( self._open_resp_id )
		if self._save_fa_id > -1: self._save_file_chooser.disconnect( self._save_fa_id )
		if self._save_resp_id > -1: self._save_file_chooser.disconnect( self._save_resp_id )

		if chooser_type == self.OPEN_PROJECT:
			self._open_file_chooser.set_title( "Open Project File" )
			self._open_file_chooser.set_filter(self.project_file_filter)
			self._open_file_chooser.set_select_multiple( False )
			self._open_fa_id = self._open_file_chooser.connect( "file-activated", 
                                                                 self.on_open_project,
                                                                 self.CHOOSER_OPEN )
			self._open_resp_id = self._open_file_chooser.connect( "response", self.on_open_project )
			self._open_file_chooser.show()

		elif chooser_type == self.OPEN_FILES:
			self._open_file_chooser.set_title( "Add File to Project" )
			self._open_file_chooser.set_filter(self.all_files_filter)
			self._open_file_chooser.set_select_multiple( True )
			self._open_fa_id = self._open_file_chooser.connect( "file-activated",
                                                                self.on_open_files,
                                                                self.CHOOSER_OPEN )
			self._open_resp_id = self._open_file_chooser.connect( "response", self.on_open_files )
			self._open_file_chooser.show()

		elif chooser_type == self.NEW_PROJECT:
			self._save_file_chooser.set_title( "Save New Project File As ..." )
			self._save_file_chooser.set_filter(self.project_file_filter)
			self._save_file_chooser.set_current_name("Project-filename-WITHOUT-extension")
			self._save_fa_id = self._save_file_chooser.connect( "file-activated",
                                                                self.on_save_project,
                                                                self.CHOOSER_SAVE )
			self._save_resp_id = self._save_file_chooser.connect( "response",
                                                                  self.on_save_project )
			self._save_file_chooser.show()

		else:
			return False

		return True


	def _has_gedit_project_extension( self, filename ):     #GYLL
		RANDOM_MARKER = "/45n687q2qVcsAHsfDord8326bfaW8e7c"
		filename = filename + RANDOM_MARKER
		if  filename.find( ".gedit-project" + RANDOM_MARKER ) != -1: 
			return True
		else:
			return False


	def _show_alert( self, text=None, with_log=False, my_flags=gtk.DIALOG_MODAL ):
		alert_box_text = text + "\n"
		if with_log and self._message:
			self._message.sort()
			while self._message:
				alert_box_text = alert_box_text + self._message.pop() + "\n"
		alert_box = gtk.MessageDialog(	parent = self._window,
										flags = my_flags,
										type = gtk.MESSAGE_INFO,
										buttons = gtk.BUTTONS_OK,
										message_format = alert_box_text )
		alert_box.connect( "response", self.on_alert_response )
		alert_box.show()

	def on_alert_response( self, widget, data=None ): widget.hide()

	def on_open_files( self, widget, data=None ):
		"Activated when the user selects a file to open"
		if data == self.CHOOSER_OPEN:
			file_list = list()
			for filename in self._open_file_chooser.get_uris():
				file_list.append( filename )
			self._open_files( file_list )
			self._save_project( self._project.filename )
			if self._message: self._show_alert( "Files opened.\n", self.WITH_LOG )
		self._open_file_chooser.hide()

	def on_history_action( self, filename=None  ):
		"Opens a recently used project file"
		if os.path.exists( filename ):
			self._open_project( filename )
			self._save_project( self._project.filename )
			if self._message: self._show_alert( "Project opened: '" + os.path.basename( filename ) + "'", self.WITH_LOG )
		else:
			self._show_alert(	"Project not opened: '"+ os.path.basename( filename ) + "'\n\nProject file not found: \n" + filename )
		self._add_to_history( filename )

	#GYLL
	def on_open_last_project_action( self ):
		if self._project.active == True:
			self.update_ui()
			return
		for filename in self._history:
			if os.path.exists( filename ):
				self._open_project( filename )
				self._save_project( self._project.filename )
				if self._message: self._show_alert( "Project opened: '" + os.path.basename( self._project.filename ) + "'", self.WITH_LOG )
			else:
				self._show_alert(	"Project not opened: '"+ os.path.basename( filename ) + "'\n\nProject file not found: \n" + filename )
			self._add_to_history( filename )
			return
		self._show_alert("Project history list is empty")

	#GYLL
	def on_open_file_as_project_action( self):
		doc = self._window.get_active_document()
		if (doc and doc.get_uri() != None):
			filename = "/" + doc.get_uri().strip().lstrip("file:/").replace("%20", " ")
			print "Opening file as project: " + filename
			if self._project.active: 
				self._show_alert("Could not open project: " + filename + "\nReason: A project is already open")
				return
			if not self._has_gedit_project_extension( filename ):
				self._show_alert("Cannot open project.\nReason: Current file is not a '.gedit-project' file")
				return
			if os.path.exists( filename ):
				if doc in self._window.get_unsaved_documents():
					self._show_alert( "Cannot open current file as project.\nReason: Project file is modified but NOT SAVED." )
					return
				self._window.close_tab( gedit.gedit_tab_get_from_document( doc ))
				self._open_project( filename )
				self._save_project( filename )
				self._add_to_history( filename )
				if self._message: self._show_alert( "Project opened: '" + os.path.basename( self._project.filename ) + "'", self.WITH_LOG )
			else: 
				self._show_alert(	"Project not opened: '"+ os.path.basename( filename ) + "'\n\nProject file not found: \n" + filename )

	def on_open_project( self, widget, data=None ):
		"Activated when the user opens a project from the chooser"
		if data == self.CHOOSER_OPEN:
			if self._open_file_chooser.get_filename():
				self._open_project( self._open_file_chooser.get_filename().strip() )
				self._save_project( self._project.filename )
				self._add_to_history( self._project.filename )
				if self._message: self._show_alert( "Project opened: '" + os.path.basename( self._project.filename ) + "'", self.WITH_LOG )
		self._open_file_chooser.hide()


	def on_save_project( self, widget, data=None ):
		"Activated when the user saves a project with the chooser"
		if data == self.CHOOSER_SAVE:
			if self._save_file_chooser.get_filename():
				project_filename = self._save_file_chooser.get_filename().strip()   #GYLL
				if not self._has_gedit_project_extension( project_filename ):
					project_filename = project_filename + ".gedit-project"   #GYLL
				if os.path.exists( project_filename.replace("%20", " ") ):                           #GYLL
					self._show_alert("Project file already EXISTS; it has not been replaced: " + project_filename.replace("%20", " ") ) #GYLL
				else:
					self._save_project( project_filename )   #GYLL
					self._add_to_history( project_filename ) #GYLL
					self._project.active = True
					self.update_ui()                         #GYLL
					self._show_alert( "New project opened: '" + os.path.basename( self._project.filename ) )
		self._save_file_chooser.hide()

	def _open_files( self, file_list ):
		for file_uri in file_list:
			if os.path.exists( file_uri.lstrip( "file:" ).replace("%20", " ") ):
				file_is_not_open = True
				for item in self._window.get_documents():
					if item.get_uri() == file_uri:
						item.set_data( "BelongsToProject", self._project.filename )   #GYLL
						file_is_not_open = False
						break
				if file_is_not_open:
					tab = self._window.create_tab_from_uri( file_uri, self._encoding, 0, False, False )
					tab.get_document().set_data( "BelongsToProject", self._project.filename )
					self._window.set_active_tab( tab )
				else:
					self._message.append( " - The following file is ALREADY OPEN in gedit; it has not been loaded from disk: '/" +
											file_uri.lstrip("file:/").replace("%20"," ") + "'" )
				self._project.add_file( file_uri )
			else:
				self._message.append( " - The following file has NOT BEEN FOUND; it has been REMOVED from the project: '/" +
										file_uri.lstrip( "file:/" ).replace("%20"," ") + "'")

	def _close_project( self ):
		print "Closing project ... " + self._project.filename
		for item in self._window.get_documents():                                                     #GYLL
			if item.get_uri() == None and not (item in self._window.get_unsaved_documents()):     #GYLL
				self._window.close_tab( gedit.gedit_tab_get_from_document( item ) )           #GYLL

		there_are_unsaved_files = False
		for item in self._window.get_documents():
			if item.get_data("BelongsToProject") == self._project.filename:
				item.set_data( "BelongsToProject", None )   #GYLL
				if not (item in self._window.get_unsaved_documents()):
					self._window.close_tab( gedit.gedit_tab_get_from_document( item ) )
				else:
					self._message.append( " - The following file is NOT SAVED; it has not been closed: '/" +
											item.get_uri().lstrip("file:/").replace("%20", " ") + "'" )
		self._project.clear()
		self.update_ui()

	def _open_project( self, filename ):
		"Process the project file and open all the child files"
		for item in self._window.get_documents():                                                     #GYLL
			if item.get_uri() == None and not (item in self._window.get_unsaved_documents()):     #GYLL
				self._window.close_tab( gedit.gedit_tab_get_from_document( item ) )           #GYLL

		self._project.filename = filename
		file_list = list()
		
		xml = minidom.parse( filename )
		for subfile in xml.getElementsByTagName( 'file' ):
			file_list.append( subfile.childNodes[0].data.strip() )
		self._open_files( file_list )
		self._project.active = True     #GYLL  -- this line has been inserted into this function; it used to be placed  throught the program after each call to _open_project
		print "Opening project ... " + filename

	def _save_project( self, filename ):
		"Output the project XML to a file"
		self._project.filename = filename
		self._saving_project = True
		
		# TODO: Compile an XML document out of self._project and save it
		out_xml = minidom.Document()
		out_xml.version = 1.0

		gedit_project_element = minidom.Element( 'gedit-project' )

		for subfilename in self._project.get_files():
			file_element = minidom.Element( 'file' )
			text_node = minidom.Text()
			text_node.data = subfilename
			file_element.childNodes.append( text_node )
			gedit_project_element.childNodes.append( file_element )

		out_xml.childNodes.append( gedit_project_element )

		outfile = file( self._project.filename, "w" )
		outfile.writelines( out_xml.toprettyxml() )
		outfile.close()

		self._saving_project = False
		print "Saving project ... " + self._project.filename


class ProjectPlugin( gedit.Plugin ):
	DATA_TAG = "ProjectPluginInstance"

	def __init__( self ):
		gedit.Plugin.__init__( self )

	def _get_instance( self, window ):
		return window.get_data( self.DATA_TAG )

	def _set_instance( self, window, instance ):
		window.set_data( self.DATA_TAG, instance )

	def activate( self, window ):
		self._set_instance( window, ProjectPluginInstance( self, window ) )

	def deactivate( self, window ):
		self._get_instance( window ).deactivate()
		self._set_instance( window, None )

	def update_ui( self, window ):
		self._get_instance( window ).update_ui()

#python

#
# IMPORTANT: Make sure the Octane Viewport is rendering prior to running this script.
#

import modo
import lx

# Only runs on Modo15/16
# import PySide2
# from PySide2.QtGui import *
from PySide2.QtCore import Qt
# from PySide2.QtWidgets import *
from PySide2.QtWidgets import QFileDialog, QApplication, QProgressDialog

# Get the file save name and location.  Enter the correct extension to match the Octane Save parameters (ie. .png or .exr)
path_to_file, _ = QFileDialog.getSaveFileName(None, "Save Files As...", None, "ORBX (*.orbx)")

if path_to_file != "":
   # Split the path into a filename/folder and an extension
   extension = path_to_file[path_to_file.rfind("."):]
   path_to_file = path_to_file[0:path_to_file.rfind(".")]

   # Get the currently select Pass Group
   current_pass_group_name = lx.eval('group.current ? pass')
   render_pass_group = modo.item.RenderPassGroup(current_pass_group_name)

   # Popup a progress window.  Remove the cancel button, as cancelling the render via the Render progress window should cancel all rendering
   progress = QProgressDialog("Rendering passes for " + render_pass_group.name, "Abort Rendering", 0, render_pass_group.itemCount, None)
   progress.setWindowModality(Qt.NonModal)
   progress.setWindowFlags(progress.windowFlags() ^ Qt.WindowStaysOnTopHint)
   progress.setCancelButton(None)
   progress.show()
   progress.move (progress.pos().x(), progress.pos().y() - 100)
   QApplication.processEvents()

   # Render and save each Pass in the current Pass Group
   action_clip_number = 0

   for action_clip in render_pass_group.passes:
      progress.setValue(action_clip_number)
      QApplication.processEvents()
      action_clip_number = action_clip_number + 1
      action_clip.active = True
      if action_clip.enabled:
          filename = path_to_file + "_" + action_clip.name +  extension
          try:
             result = lx.eval('octane.saveFrame "' + filename + '"')
          except:
             break

   progress.setValue(action_clip_number)
   progress.hide()
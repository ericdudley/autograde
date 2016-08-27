# autograde
A python script meant to help speed up grading python scripts for CS1 at RIT.

#How to Use
1. Download scripts to be graded from MyCourses (######-#######-Last, First-scriptname.py)
2. Extract scripts into a directory.
3. Download autograde.py and grading_rubric.txt into same directory as scripts.
4. Edit grading_rubric.txt to match the rubric of assignment.
5. Run autograde.py from terminal.

#Important
Currently only "Turtlegrade" and "Print turtle grades" are enabled, the other features are being developed.

If you are running the script in a Windows environment, you may have to modify "os_python" and/or "os_editor" at the bottom of autograde.py. The variables represent cmd commands that will run a python 3 program and open a text file respectively.

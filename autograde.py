"""
	autograde is a script intended to help speed up the grading process of python scripts.
	Features:
		-Run students' scripts in a subprocess.
		-Run automated tests.
		-Output results of automated and manual tests to grades file.
		-Input file to define automated tests.
		+Run turtle scripts
		+Input file to define grading rubric
	Requirements:
		-Meant to be run on RIT unix CS machines or any other linux system.
		-Python 3
		-gedit
	@author Eric Dudley
"""

import subprocess #Used to run python scripts in isolated environment
import os
import tempfile #Safely modify scripts without affecting original
from collections import OrderedDict #Used to keep rubric and scripts in order or grading

"""
	Runs a terminal command and returns output.
"""
def run_script(input):
	return subprocess.check_output(input, universal_newlines=True)

"""
	Runs a terminal command.
"""
def run_script_blind(input, stdinstrs):
	p = subprocess.Popen(input, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
	if(len(stdinstrs) > 0):
		comstr = ""
		for string in stdinstrs:
			comstr += string+"\n"
		p.communicate(comstr)
	print(p.communicate())
	#return subprocess.call(input)
	
"""
	Reads in custom test cases from input file.
	Returns them in a dictionary.
"""
def getCases(filename):
	rdict = {}
	line_separator = "$$$<<<>>>"
	name = ""
	args = []
	output = ""
	next = "name"
	for line in open(filename,"r"):
		line = line.strip()
		if(line == line_separator):
			rdict[name] = {"args":args,"output":output}
			name = ""
			args = []
			output = ""
			next = "name"
			continue
		if(next == "name"):
			name = line
			next = "args"
			continue
		elif(next == "args"):
			args = line.split()
			next = "output"
			continue
		elif(next == "output"):
			output += line+"\n"
	return rdict

"""
	Builds a dictionary of test cases for turtle.
"""
def getTurtleCases(filename):
	rdict  = OrderedDict()
	count = 0
	for line in open(filename, "r"):
		line = line.strip()
		if(line == ""): continue
		elems = line.split(",")
		elems = [elem.strip() for elem in elems]
		rdict["Test "+str(count)] = elems
		count+=1
	return rdict
"""
	Grades automatically/manually scripts in submissions directory with custom test cases.
"""
def grade(auto):
	subdir = "submissions"
	case_file = "test_cases.txt"
	tests = getCases(case_file)
	runfile = "test.py"
	for test in tests:
		print("^^^")
		name = test
		result = run_script(["python", runfile]+tests[test]["args"])
		passed = False
		if(auto):
			passed = (result == tests[test]["output"])
			if(passed):
				print("Passed "+test+"!")
			else:
				print("Failed "+test+"!")
				print("Expected:\n"+tests[test]["output"])
				print("---\nGot:\n"+result)
		else:
			print("Expected:\n"+tests[test]["output"])
			print("---\nGot:\n"+result)
			choice = input("Passed? [y/n] ")
			if(choice == "y"):
				passed = True
			elif(choice == "n"):
				passed = False

"""
	Runs all turtle scripts in current directory and displays scripts in gedit, then allows user to grade each part of the rubric.
"""
def turtle_grade():
	grades = OrderedDict()
	count = 0
	print("Running all turtle files...")
	for(dir, sub_dir, files) in os.walk("."):
		for filename in files:
			if( filename.endswith(".py") and #python script
			("import turtle" in open(filename).read() or "from turtle" in open(filename).read()) and #implements turtle 
			filename != "autograde.py"): #not itself
				count+=1
				print(filename)
				
				filei = open(filename, "r")
				rewrite = "" #Rewrite the file line by line. Try to insert helpful lines.
				turtle_name = "turtle"
				for line in filei:
					if "import turtle" in line or "from turtle import" in line:
						if "import turtle as" in line: #Account for shortnames for turtle
							turtle_name = line.split(" ")[3].strip()
						line += turtle_name+".speed(0)\n" #Set turtle to max speed
					if turtle_name+".done()" in line:
						line = line.replace(".done()", ".exitonclick()") #Enable click to exit
					rewrite += line	
				if ".exitonclick()" not in rewrite:
					rewrite += turtle_name+".exitonclick()" #Add to end of script if not anywhere else
				filei.close()
				
				fileo = tempfile.NamedTemporaryFile(mode="w", delete=False);
				fileo.write(rewrite) #Create temporary file for modified script
				fileo.close()
				
				cases = getTurtleCases("turtle_cases.txt")
				print(cases)
				if(len(cases) > 0):
					for case in cases:
						run_script_blind([os_python, fileo.name], cases[case]+["y"]) #Temporary fix
				else:
					run_script_blind([os_python, fileo.name], ["y"]) #Temporary fix
				os.remove(fileo.name) #Delete temporary file
				print("Opening code")
				os.system(os_editor+' "'+filename+'"') #Open original script in gedit
				
				#Get user input to grade everything on rubric
				grades[filename] = OrderedDict()
				gguidef = open("grading_rubric.txt", "r")
				for line in gguidef:
					line = line.strip()
					elems = line.split(",")
					if len(elems) == 2:
						elems = [ elem.strip() for elem in elems]
						grades[filename][elems[0]] = {}
						grades[filename][elems[0]]["max"] = int(elems[1])
						invalidNum = True
						while(invalidNum):
							try:
								innum = int(input(elems[0]+"[0-"+elems[1]+"]: "))
								if(innum < 0 or innum > int(elems[1])):
									continue
								invalidNum = False
								grades[filename][elems[0]]["earned"] = innum
							except ValueError:
								continue
				gguidef.close()
				grades[filename]["comments"] = input("Comments: ")

	out_str = ""
	if count == 0:
		print("No turtle files in current directory!")
		return
	for key in grades.keys(): #For each student
		if len(key.split("-")) > 2:
			out_str += key.split("-")[2].strip()
		else:
			out_str += key.strip()
		out_str += "\n"
		overall = 0 #Total points
		max_overall = 0 #Maximum possible total points
		for cat in grades[key].keys(): #For each part of rubric
			if cat == "comments":
				out_str += "Comments: "+grades[key][cat]+"\n"
				continue
			out_str += "   "+cat+": "+str(grades[key][cat]["earned"])+"/"+str(grades[key][cat]["max"])+"\n"
			overall += grades[key][cat]["earned"]
			max_overall += grades[key][cat]["max"]
		out_str += "Overall: "+str(overall)+"/"+str(max_overall)+"\n"
		out_str += "===================\n"
	print("Saving grades to turtle_grades.txt...")
	outfile = open("turtle_grades.txt", "w")
	outfile.write(out_str)
	outfile.close()
	print("Grading completed.")
	
"""
	Outputs turtle grades, the turtle grading process must be done first.
"""
def print_turtle_grades():
	ifile = open("turtle_grades.txt", "r")
	for line in ifile:
		print(line)

"""
	Output grades to a grades file.
"""
def gen_output():
	print("Outputting to outputs.txt...")
	out_str = ""
	#for each submission
	author = "Eric R Dudley"
	filename = "test.py"
	result = run_script(["python",filename])
	out_str += author+"\n---\n"+result+"---\n"
	outfile = open("outputs.txt", "w")
	outfile.write(out_str)
	outfile.close()
	
"""
	Handles menu navigation.
"""
def main():
	print("Welcome to autograder!")
	while(True):
		print("Please choose an action...")
		print("[1] Autograde(dummy)\n[2] Manugrade(dummy)\n[3] Generate output(dummy)\n[4] Turtlegrade\n[5] Print turtle grades\n[q] Quit")
		choice = input(">>>")
		if(choice == "1"): #Autograde
			#grade(True)
			print("In development.")
		elif(choice == "2"): #Manugrade
			#grade(False)
			print("In development.")
		elif(choice == "3"): #Generate output
			#gen_output()
			print("In development.")
		elif(choice == "4"): #Turtlegrade
			turtle_grade()
		elif(choice == "5"): #Print turtle grades
			print_turtle_grades()
		elif(choice == "q"): #Quit
			break

#Linux/Unix environment
os_python = "python3"
os_editor = "gedit"

#Windows environment
if os.name == "nt": 
	os_python = "python"
	os_editor = "C:\\Python34\\Lib\\idlelib\\idle.py"
main()

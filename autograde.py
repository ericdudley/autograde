import subprocess
import os
import tempfile
import collections
def run_script(input):
	return subprocess.check_output(input, universal_newlines=True)

def run_script_blind(input):
	return subprocess.call(input)
	
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
	#for each submission
	#test each testcase, storing results along the way
def turtle_grade():
	grades = collections.OrderedDict()
	print("Running all turtle files...")
	count = 0
	for(dir, sub_dir, files) in os.walk("."):
		for filename in files:
			if(filename.endswith(".py") and ("import turtle" in open(filename).read() or "from turtle" in open(filename).read()) and filename != "autograde.py"):
				count+=1
				print(filename)
				filei = open(filename, "r")
				rewrite = ""
				turtle_name = "turtle"
				for line in filei:
					if "import turtle" in line or "from turtle import" in line:
						if "import turtle as" in line:
							turtle_name = line.split(" ")[3].strip()
						line += turtle_name+".speed(0)\n"
					if turtle_name+".done()" in line:
						line = line.replace(".done()", ".exitonclick()")
					rewrite += line	
				if ".exitonclick()" not in rewrite:
					rewrite += turtle_name+".exitonclick()"
				filei.close()
				fileo = tempfile.NamedTemporaryFile(mode="w", delete=False);
				fileo.write(rewrite)
				fileo.close()
				run_script_blind(["python3", fileo.name])
				os.remove(fileo.name)
				print("Opening code")
				os.system('gedit "'+filename+'"')
				grades[filename] = collections.OrderedDict()
				gguidef = open("grading_guide.txt", "r")
				for line in gguidef:
					line = line.strip()
					elems = line.split(",")
					if len(elems) == 2 and elems[0].lower() != "overall":
						elems[0] = elems[0].strip()
						elems[1] = elems[1].strip()
						grades[filename][elems[0]] = {}
						grades[filename][elems[0]]["max"] = int(elems[1])
						grades[filename][elems[0]]["earned"] = int(input(elems[0]+"[0-"+elems[1]+"]: "))
				gguidef.close()
	out_str = ""
	if count == 0:
		print("No turtle files in current directory!")
		return
	for key in grades.keys():
		if len(key.split("-")) > 2:
			out_str += key.split("-")[2].strip()
		else:
			out_str += key.strip()
		out_str += "\n"
		overall = 0
		max_overall = 0
		for cat in grades[key].keys():
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
def print_turtle_grades():
	ifile = open("turtle_grades.txt", "r")
	for line in ifile:
		print(line)
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
def main():
	print("Welcome to autograder!")
	#run_script(["python", "test.py","Kevin"])
	while(True):
		print("Please choose an action...")
		print("[1] Autograde\n[2] Manugrade\n[3] Generate output\n[4] Turtlegrade\n[5] Print turtle grades\n[q] Quit")
		choice = input(">>>")
		if(choice == "1"):
			grade(True)
		elif(choice == "2"):
			grade(False)
		elif(choice == "3"):
			gen_output()
		elif(choice == "4"):
			turtle_grade()
		elif(choice == "5"):
			print_turtle_grades()
		elif(choice == "q"):
			break

main()

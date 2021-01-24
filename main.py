import mysql.connector
import datetime
import random
import hashlib
import userInput
import names
import os

def getRandomDate():
    start_date = datetime.date(2000, 1, 1)
    end_date = datetime.date(2010, 1, 1)

    return start_date + datetime.timedelta(days=random.randrange((end_date - start_date).days))

db = mysql.connector.connect(
    user="root", 
    password="root",
    host="127.0.0.1",
    database="vote"
)

cursor = db.cursor(dictionary=True)

def editCandidates(tutor):
    while True:
        menu = """\n{0} candidates menu :
    1) View candidates
    2) Nominate candidates
    3) Remove candidates
    4) Return to tutor menu
""".format(tutor)
        menuChoice = userInput.chooseFromList(int, menu, [1, 2, 3, 4])

        if menuChoice == 1:
            cursor.execute("SELECT * FROM candidates WHERE studentID IN (SELECT studentID FROM student_in_tutor WHERE tutorID='{0}')".format(tutor))
            students = cursor.fetchall()
            if students:
                cursor.execute("SELECT * FROM students WHERE studentID IN {0}".format(str(tuple([student["studentID"] for student in students])).replace(",)", ")")))
                students = cursor.fetchall()
                print("\n###{0} CANDIDATES###".format(tutor))
                printStudents(students)
                print()
            else:
                print("There are no candidates for " + tutor)
        elif menuChoice == 2:
            nominateCandidates(tutor)
        elif menuChoice == 3:
            removeCandidates(tutor)
        elif menuChoice == 4:
            return

def editStudents(tutor):
    while True:
        menu = """\n{0} students menu :
    1) View students
    2) Add students
    3) Remove students
    4) Return to tutor menu
""".format(tutor)

        menuChoice = userInput.chooseFromList(int, menu, [1, 2, 3, 4, 5])

        if menuChoice == 1:
            cursor.execute("SELECT * FROM students WHERE studentID IN (SELECT studentID FROM student_in_tutor WHERE tutorID='{0}')".format(tutor))
            students = cursor.fetchall()
            if students:
                print("\n###{0} CANDIDATES###")
                printStudents(students)
                print()
            else:
                print("There are no students in " + tutor)
        elif menuChoice == 2:
            addStudents(tutor)
        elif menuChoice == 3:
            removeStudents(tutor)
        elif menuChoice == 4:
            return

def removeCandidate(id):
    cursor.execute("DELETE FROM candidates WHERE studentID='{0}'".format(id))
    db.commit()

def printStudents(students):
    idColumnWidth = max(3, max([len(str(student["studentID"])) for student in students]))
    columnWidth = max(16, max([len(student["studentName"]) for student in students] + [len(student["dob"].strftime("%d %B %y")) for student in students]))
    
    row = "{0:<" + str(idColumnWidth) + "} | {1:<" + str(columnWidth) + "} | {2:<" + str(columnWidth) + "} | {3:<" + str(10) + "} | {4:<" + str(10) + "}"
    print(row.format("ID", "Name", "Date of birth", "Voted", "Abstained"))
    print("_" * idColumnWidth + "_|_" + "_" * columnWidth + "_|_" + "_" * columnWidth + ("_|_" + "_" * 10)*2)
    for student in students:
        voted = "yes" if student["voted"] else "no"
        abstained = "yes" if student["abstained"] else "no"
        print(row.format(student["studentID"], student["studentName"], student["dob"].strftime("%d %B %y"), voted, abstained))
    return len(students)

def printCandidates(candidates):
    idColumnWidth = max(3, max([len(str(student["studentID"])) for student in candidates]))
    columnWidth = max(16, max([len(student["studentName"]) for student in candidates] + [len(student["dob"].strftime("%d %B %y")) for student in candidates]))
    
    row = "{0:<" + str(idColumnWidth) + "} | {1:<" + str(columnWidth) + "} | {2:<" + str(columnWidth) + "}"
    print(row.format("ID", "Name", "Date of birth"))
    print("_" * idColumnWidth + "_|_" + "_" * columnWidth + "_|_" + "_" * columnWidth)
    for student in candidates:
        print(row.format(student["studentID"], student["studentName"], student["dob"].strftime("%d %B %y")))
    return len(candidates)

def removeCandidates(tutor):
    cursor.execute("SELECT * FROM candidates WHERE studentID IN (SELECT studentID FROM student_in_tutor WHERE tutorID='{0}')".format(tutor))
    students = cursor.fetchall()

    while len(students):
        cursor.execute("SELECT * FROM students WHERE studentID IN {0}".format(str(tuple([student["studentID"] for student in students])).replace(",)", ")")))
        students = cursor.fetchall()
        print("Current candidates: ")
        printStudents(students)
        print()
        ids = [student["studentID"] for student in students]
        id = userInput.chooseFromList(int, "Enter the student ID of the candidate you wish to remove: ", ids)
        
        removeCandidate(id)

        cursor.execute("SELECT studentName FROM students WHERE studentID={0}".format(id))
        print("{0} removed".format(cursor.fetchone()["studentName"]))


        cursor.execute("SELECT * FROM candidates WHERE studentID IN (SELECT studentID FROM student_in_tutor WHERE tutorID='{0}')".format(tutor))
        students = cursor.fetchall()

        if not userInput.yesno("Remove another student?: "):
            break

        print()

    print("There are no canidates in {0}".format(tutor))

def nominateCandidates(tutor):
    cursor.execute("SELECT * FROM candidates WHERE studentID IN (SELECT studentID FROM student_in_tutor WHERE tutorID='{0}')".format(tutor))
    students = cursor.fetchall()
    no = 4 - len(students)

    if len(students):
        cursor.execute("SELECT * FROM students WHERE studentID IN {0}".format(str(tuple([student["studentID"] for student in students])).replace(",)", ")")))
        students = cursor.fetchall()
        print("Current candidates: ")
        printStudents(students)
        print()

    if no <= 0:
        print("No more candidates can be nominated")
        return

    cursor.execute("SELECT * FROM students WHERE studentID IN (SELECT studentID FROM student_in_tutor WHERE tutorID='{0}')".format(tutor))
    students = cursor.fetchall()

    nameRegex = "^[a-zA-Z,.'-]+$"
    counter = no
    while counter > 0:
        firstName = userInput.getStringInput("Please enter the first name of the person you wish to nominate, or type view to see all students: ", nameRegex, ["view"])
        if firstName == "view":
            cursor.execute("SELECT * FROM students WHERE studentID IN (SELECT studentID FROM student_in_tutor WHERE tutorID='{0}')".format(tutor))
            students = cursor.fetchall()
            printStudents(students)
            print()
            continue
        stmt = (
            "SELECT * FROM students WHERE "
            "studentID IN (SELECT studentID FROM student_in_tutor WHERE tutorID='{0}') AND "
            "studentID NOT IN (SELECT studentID FROM candidates) AND "
            "studentName LIKE '{1}%'"
        ).format(tutor, firstName)
        cursor.execute(stmt)
        students = cursor.fetchall()
        if len(students) == 0:
            print("There are no students in {0} with that name".format(tutor))
            continue
        elif len(students) == 1:
            student = students[0]
            if userInput.yesno("Do you mean {0}, born on {1}?: ".format(student["studentName"], student["dob"].strftime("%d %B %y"))):
                nominateCandidate(student["studentID"])
                print("{0} nominated".format(student["studentName"]))
                counter -= 1
        else:
            printStudents(students)
            ids = [student["studentID"] for student in students]
            prompt = "Enter the student ID of the student you want to nominate: "
            id = userInput.chooseFromList(int, prompt, ids)
            nominateCandidate(id)
            cursor.execute("SELECT studentName FROM students WHERE studentID = {0}".format(id))
            print("{0} nominated".format(cursor.fetchone()["studentName"]))
            counter -= 1

        if not userInput.yesno("Nominate another candiate? "):
            return
    print("You have reached the maximum number of candidates")

def nominateCandidate(studentID):
    stmt = (
        "INSERT INTO candidates(studentID, votes) "
        "VALUES ({0}, 0)"
    ).format(studentID)
    cursor.execute(stmt)
    db.commit()

def addStudent(name, dob, tutor):
    stmt = (
        "INSERT INTO students(studentName, dob) "
        "VALUES ('{0}', '{1}')"
    ).format(name.lower(), dob)
    cursor.execute(stmt)
    db.commit()

    cursor.execute("SELECT studentID FROM students WHERE studentName='{0}' AND dob='{1}'".format(name, dob))
    studentID = cursor.fetchone()["studentID"]

    #student_in_tutor
    stmt = (
       "INSERT INTO student_in_tutor (studentID, tutorID) "
        "VALUES ({0}, '{1}')"
    ).format(studentID, tutor.lower())
    cursor.execute(stmt)
    db.commit()
    
def addStudents(tutor):
    no = userInput.getNumInRange(int, "How many students do you want to add? ", (1, 1000), "Please enter an integer 1 or above")

    nameRegex = "^[a-zA-Z ,.'-]+$"

    print("Enter 'exit' at any time to stop")
    for i in range(no):
        while True:
            print("STUDENT NO {0}".format(i+1))
            name = userInput.getStringInput("Please enter their full name: ", nameRegex, ["exit"], "Name must only comtain letters, spaces, dashes, '-'. '.', ',' or '''")
            if name == "exit":
                return
            dobInput = userInput.getDate("Please enter their date of birth: ", ["exit"])
            dob = datetime.datetime.strptime(dobInput, "%d/%m/%Y")
            if dob == "exit":
                return
            if userInput.yesno("Is this correct? : '{0}' born on '{1}'".format(name, dobInput)):
                addStudent(name, dob, tutor)
                print()
                break
    
def removeStudents(tutor):
    while True:
        cursor.execute("SELECT * FROM students WHERE studentID IN (SELECT studentID FROM student_in_tutor WHERE tutorID='{0}')".format(tutor))
        students = cursor.fetchall()

        if not len(students):
            print("There are no canidates in {0}".format(tutor))

        print("Current {} students: ".format(tutor))
        printStudents(students)
        print()

        nameRegex = "^[a-zA-Z,.'-]+$"
        while students:
            cursor.execute("SELECT * FROM students WHERE studentID IN (SELECT studentID FROM student_in_tutor WHERE tutorID='{0}')".format(tutor))
            students = cursor.fetchall()
            if not students:
                print("There are no students in {0}".format(0))
                return
            firstName = userInput.getStringInput("Please enter the first name of the person you wish to delete, or type view to see all students: ", nameRegex, ["view"])
            if firstName == "view":
                cursor.execute("SELECT * FROM students WHERE studentID IN (SELECT studentID FROM student_in_tutor WHERE tutorID='{0}')".format(tutor))
                students = cursor.fetchall()
                printStudents(students)
                print()
                continue
            stmt = (
                "SELECT * FROM students WHERE "
                "studentID IN (SELECT studentID FROM student_in_tutor WHERE tutorID='{0}') AND "
                "studentName LIKE '{1}%'"
            ).format(tutor, firstName)
            cursor.execute(stmt)
            students = cursor.fetchall()
            if len(students) == 0:
                print("There are no students in {0} with that name".format(tutor))
                continue
            elif len(students) == 1:
                student = students[0]
                if userInput.yesno("Do you mean {0}, born on {1}?: ".format(student["studentName"], student["dob"].strftime("%d %B %y"))):
                    removeStudent(student["studentID"])
                    print("{0} removed".format(student["studentName"]))
                else:
                    continue
            else:
                printStudents(students)
                ids = [student["studentID"] for student in students]
                prompt = "Enter the student ID of the student you want to nominate: "
                id = userInput.chooseFromList(int, prompt, ids)

                name = cursor.execute(("SELECT studentName FROM students "
                "WHERE studentID={0}").format(id)).fetchone()["studentName"]

                removeStudent(id)

                print("{0} removed".format(name))

            if not userInput.yesno("Delete another student? "):
                return

def removeStudent(id):
    cursor.execute(("DELETE FROM student_in_tutor "
    "WHERE studentID={0}".format(id)))

    cursor.execute(("DELETE FROM candidates "
    "WHERE studentID={0}".format(id)))

    cursor.execute(("DELETE FROM students "
    "WHERE studentID={0}".format(id)))

    db.commit()

def newTutor():
    while True:
        tutorID = input("Enter new tutor group name: ")
        confirm = input("Confirm new tutor group name: ")
        if tutorID == confirm:
            break

        print("Confirmation must match original\n")

    print()

    while True:
        username = userInput.getStringInput("Enter tutor admin username: ", "^[A-Za-z0-9_-]*$", "Only letters, numbers, underscore and dash are allowed in username")
        confirm = input("Confirm tutor admin username: ")
        if username == confirm:
            break

        print("Confirmation must match original\n")

    username = username.lower()
    print()

    password = userInput.passwordEntry(True)

    password = hashlib.sha1(bytes(password, "utf-8")).hexdigest()

    stmt = (
        "INSERT INTO tutor (tutorID, username, password) "
        "VALUES ('{0}', '{1}', '{2}')"
    ).format(tutorID.lower(), username, password)

    cursor.execute(stmt)

    db.commit()

def adminLogin():
    cursor.execute("SELECT tutorID FROM tutor")
    tutors = [x["tutorID"] for x in cursor.fetchall()]
    tutorID = userInput.chooseFromList(str, "What tutor group are you the tutor for? ", tutors)

    run = True
    while run:
        username = input("what is your username?: ")
        password = userInput.getPassword("What is your password?: ")
        password = hashlib.sha1(bytes(password, "utf-8")).hexdigest()
        cursor.execute("SELECT tutorID FROM tutor WHERE username='{0}' AND password='{1}' AND tutorID='{2}'".format(username, password, tutorID))

        tutor = cursor.fetchone()

        if tutor:
            return tutor["tutorID"]
        else:
            print("Incorrect username or password")
            run = userInput.yesno("Try again? ")

def voterLogin():
    nameRegex = "^[a-zA-Z ,.'-]+$"

    run = True
    while run:
        cursor.execute("SELECT tutorID FROM tutor") 
        tutors = [x["tutorID"] for x in cursor.fetchall()]
        tutor = userInput.chooseFromList(str, "What tutor are you in? ", tutors)
        name = userInput.getStringInput("Please enter your full name: ", nameRegex).lower()
        date = userInput.getDate("Please enter your date of birth (dd/mm/yyyy): ", "Invalid date")

        date = datetime.datetime.strptime(date, '%d/%m/%Y').date().strftime("%Y-%m-%d")
        cursor.execute("SELECT * FROM students WHERE studentName='{0}' AND dob='{1}' and studentID IN (SELECT studentID FROM student_in_tutor WHERE tutorID='{2}')".format(name, date, tutor))

        student = cursor.fetchone()

        if not student:
            print("There is no registered voter with this name and date of birth")
            run = userInput.yesno("Try again? ")
        else:
            cursor.execute("SELECT tutorID FROM student_in_tutor WHERE studentID={0}".format(student["studentID"]))
            return student, cursor.fetchone()["tutorID"]

    return False

def addRandom(n, tutor):
    for i in range(n):
        addStudent(names.get_full_name(), getRandomDate(), tutor)

def voteFor(studentID):
    cursor.execute(("SELECT votes FROM candidates WHERE studentID='{0}'").format(studentID))
    voteCount = cursor.fetchone()["votes"]

    cursor.execute(("UPDATE candidates "
            "SET votes={0} "
            "WHERE studentID={1}".format(voteCount+1 if voteCount else 1, studentID)))

def vote():
    student, tutor = voterLogin()

    if not student["studentID"]:
        return

    if student["voted"]:
        print("You have already voted")
        return

    if student["abstained"]:
        print("You have abstained")
        return

    if not userInput.yesno("Do you want to vote? : "):
        stmt = ("UPDATE students "
                "SET abstained=1 "
                "WHERE studentID={}".format(student["studentID"]))
        cursor.execute(stmt)
        db.commit()
        return

    cursor.execute("SELECT * FROM candidates WHERE studentID IN (SELECT studentID FROM student_in_tutor WHERE tutorID='{0}')".format(tutor))
    students = cursor.fetchall()
    if students:
        cursor.execute("SELECT * FROM students WHERE studentID IN {0}".format(str(tuple([student["studentID"] for student in students])).replace(",)", ")")))
        students = cursor.fetchall()
        print("\n###{0} CANDIDATES###".format(tutor))
        printCandidates(students)
        print()
    else:
        print("There are no candidates for " + tutor)
        return
    
    studentIDs = [student["studentID"] for student in students]
    vote = userInput.chooseFromList(int, "Please enter the ID of the candidate you want to vote for: ", studentIDs)

    voteFor(vote)

    stmt = ("UPDATE students "
            "SET voted=1 "
            "WHERE studentID={}".format(student["studentID"]))
    cursor.execute(stmt)

    stmt = ("SELECT * FROM students "
    "WHERE studentID={0}").format(vote)
    cursor.execute(stmt)
    student = cursor.fetchone()


    print("You voted for", student["studentName"])

    db.commit()

def adminMenu(tutor):
    while True:
        menu = """\n{0} ADMIN MENU:
    1) Edit Students
    2) Edit Candidates
    3) Return to main menu
""".format(tutor)

        menuChoice = userInput.chooseFromList(int, menu, [1, 2, 3])

        if menuChoice == 1:
            editStudents(tutor)
        elif menuChoice == 2:
            editCandidates(tutor)
        else:
            return

def menu():
    while True:
        menu = """\nMAIN MENU : 
    1) Cast vote
    2) Tutor admin menu
    3) Exit
"""

        menuChoice = userInput.chooseFromList(int, menu, [1, 2])

        if menuChoice == 1:
            vote()
        elif menuChoice == 2:
            tutor = adminLogin()
            if tutor:
                adminMenu(tutor)
        elif menuChoice == 3:
            exit()

menu()
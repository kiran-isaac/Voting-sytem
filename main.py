import mysql.connector
import datetime
import random
import hashlib
import userInput
import os

def getRandomDate():
    start_date = datetime.date(2000, 1, 1)
    end_date = datetime.date(2010, 1, 1)

    return start_date + datetime.timedelta(days=random.randrange((end_date - start_date).days))

db = mysql.connector.connect(
    user="root", 
    password="StinkPig37",
    host="127.0.0.1",
    database="vote"
)

cursor = db.cursor(dictionary=True)

def editStudents(tutor):
    menu = """{0} students menu :
    1) View students
    2) 

def addStudent(name, dob, tutor):
    global cursor

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
        name = userInput.getStringInput("Please enter your full name: ", nameRegex).lower()
        date = userInput.getDate("Please enter your date of birth (dd/mm/yyyy): ", "Invalid date")

        date = datetime.datetime.strptime(date, '%d/%m/%Y').date().strftime("%Y-%m-%d")
        print(date)
        cursor.execute("SELECT studentID FROM students WHERE studentName='{0}' AND dob='{1}'".format(name, date))

        student = cursor.fetchone()

        if not student:
            print("There is no registered voter with this name and date of birth")
            run = userInput.yesno("Try again? ")
        else:
            cursor.execute("SELECT tutorID FROM student_in_tutor WHERE studentID={0}".format(student["studentID"]))
            return student["studentID"], cursor.fetchone()["tutorID"]

    return False

def vote():
    studentID = voterLogin()
    print(studentID)
    if not studentID:
        return

def adminMenu(tutor):
    menu = """\n{0} ADMIN MENU:
    1) Edit Students
    2) Placeholder
    3) Placeholder
""".format(tutor)

    print(menu)

    menuChoice = userInput.chooseFromList(int, menu, [1, 2, 3])

    if menuChoice == 1:
        editStudents(tutor)

def menu():
    menu = """\nMAIN MENU : 
    1) Cast vote
    2) Tutor menu
"""

    menuChoice = userInput.chooseFromList(int, menu, [1, 2])

    if menuChoice == 1:
        vote()
    elif menuChoice == 2:
        tutor = adminLogin()
        if tutor:
            adminMenu(tutor)

menu()
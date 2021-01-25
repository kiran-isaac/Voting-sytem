import userInput

def voteFor(studentID):
    cursor.execute(("SELECT votes FROM candidates WHERE studentID='{0}'").format(studentID))
    voteCount = cursor.fetchone()["votes"]

    cursor.execute(("UPDATE candidates "
            "SET votes={0} "
            "WHERE studentID={1}".format(voteCount+1 if voteCount else 1, studentID)))

def vote():
    student, tutor = voterLogin()

    if not student:
        return

    if student["voted"]:
        print("You have already voted")
        return

    if student["abstained"]:
        print("You have abstained")
        return

    if not userInput.yesno("Do you want to vote? : "):
        stmt = ("UPDATE students "
                "SET abstained=1, "
                "voted=1 "
                "WHERE studentID={}".format(student["studentID"]))
        cursor.execute(stmt)
        db.commit()
        return

    cursor.execute("SELECT * FROM candidates WHERE studentID IN (SELECT studentID FROM student_in_tutor WHERE tutorID='{0}')".format(tutor))
    students = cursor.fetchall()
    if students:
        cursor.execute("SELECT * FROM students WHERE studentID<>{0} AND studentID IN {1}".format(student["studentID"], str(tuple([student["studentID"] for student in students])).replace(",)", ")")))
        students = cursor.fetchall()
        print("\n###{0} CANDIDATES###".format(tutor))
        printCandidates(students)
        print()
    else:
        print("There are no candidates for " + tutor)
        return

    while True:
        studentIDs = [student["studentID"] for student in students]
        vote = userInput.chooseFromList(int, "Please enter the ID of the candidate you want to vote for: ", studentIDs)
        
        stmt = ("SELECT * FROM students "
        "WHERE studentID={0}").format(vote)
        cursor.execute(stmt)
        student = cursor.fetchone()

        print("You voted for", student["studentName"])

        if userInput.yesno("Are you sure you want to vote for {0}"):
            voteFor(vote)

            stmt = ("UPDATE students "
                    "SET voted=1 "
                    "WHERE studentID={}".format(student["studentID"]))
            cursor.execute(stmt)

            db.commit()

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
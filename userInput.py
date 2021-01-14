def chooseFromList(inputType, prompt, validate = None, error=None, caseSensetive = True, inputFunc = input, outputFunc = print):
    while True:
        if inputType == str:
            response = inputFunc(prompt)

            if type(validate) != list:
                raise ValueError("Validate must be a list")
            
            if not caseSensetive:
                validate = [x.lower() for x in validate]
                response = response.lower()

            #validate
            if response in validate:
                return response

        elif inputType == int:
            response = ""
            run = True
            while run:
                response = inputFunc(prompt)
                try:
                    response = int(response)
                    run = False
                except:
                    outputFunc("Please enter an integer")

            if response in validate:
                return response
        
        if error:
            outputFunc(error)
        else:
            errorString = "Please choose one from "
            last = str(validate.pop())
            penultimate = str(validate.pop())
            for item in validate:
                errorString += str(item) + ", "
            errorString += penultimate + " or " + last
            outputFunc(errorString)

def getNumInRange(inputType, prompt, validate = None, error=None, inputFunc = input, outputFunc = print):
    if inputType not in [float, int]:
        raise ValueError("Input type must be int or float")
    response = ""
    run = True
    while run:
        response = inputFunc(prompt)
        try:
            response = inputType(response)
            run = False
        except:
            outputFunc("Please enter a number")

    try:
        if response >= validate[0] and response <= validate[1]:
            return response
        else:
            if error:
                outputFunc(error)
            else:
                outputFunc("Input must be between {0} and {1}".format(validate[0], validate[1]))
        if validate[0] >= validate[1]:
            raise ValueError
    except ValueError:
        raise ValueError("The minimum value of the tuple must be less than the maximum value")
    except:
        raise IndexError("Validate must be a tuple of 2 numbers if mode = 'range' (min, max)")
        
def yesno(prompt, error=None, inputFunc = input, outputFunc = print):
    while True:
        response = inputFunc(prompt)

        if response.lower() == "yes":
            return True
        elif response.lower() == "no":
            return False
        else:
            if error:
                outputFunc(error)
            else:
                outputFunc("Please choose yes or no")

def getStringInput(prompt, regex, choice=None, error=None, inputFunc = input, outputFunc = print):
    while True:
        response = inputFunc(prompt)
                
        import re
        if re.search(regex, response) or choice and response in choice:
            return response
        else:
            if error:
                outputFunc(error)
            else:
                outputFunc("Invalid entry")

def getDate(prompt, choice = None, error = None, inputFunc = input, outputFunc = print):
    return getStringInput(prompt, "(^(((0[1-9]|1[0-9]|2[0-8])[\/](0[1-9]|1[012]))|((29|30|31)[\/](0[13578]|1[02]))|((29|30)[\/](0[4,6,9]|11)))[\/](19|[2-9][0-9])\d\d$)|(^29[\/]02[\/](19|[2-9][0-9])(00|04|08|12|16|20|24|28|32|36|40|44|48|52|56|60|64|68|72|76|80|84|88|92|96)$)", choice, error, inputFunc, outputFunc)

def setPassword(confirm = False, prompt = None, outputFunc = print): 
    import stdiomask

    while True:
        if not prompt:
            prompt = "Enter your password: "
        if confirm:
            password = getStringInput(prompt, "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$", "Your password must be at least 8 digits long, and you need at least 1 capital letter and 1 digit in your password", stdiomask.getpass, outputFunc)
            confirm = stdiomask.getpass("Confirm password: ")
            if password == confirm:
                return password
            else:
                outputFunc("Passwords do not match\n")
        else:
            return getStringInput(prompt, "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$", "You need at least 1 capital letter and 1 digit in your password", stdiomask.getpass, outputFunc)

def getPassword(prompt = "Enter Password: "):
    import stdiomask

    return stdiomask.getpass(prompt)
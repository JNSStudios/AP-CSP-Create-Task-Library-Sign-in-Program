# === IMPORT SECTION === 
import tkinter as tk
import pandas as pd
from datetime import datetime
from hashlib import sha256
from tkinter import scrolledtext
import tkinter.filedialog as filedialog
import os
import pathlib
"""
PROGRAM SYNOPSIS: 
This program reads from a CSV file that acts as a database for students at a school. 
The CSV should at least include the student's first and last name, and their Student ID. 
Other identifying information is not required for this program to function, but it is helpful for confirming identity.

It then waits for a user to input their Student ID into the sign-in screen. If the ID matches someone in the database,
it brings up a screen that displays the first/last name of the student (and other additional info) to confirm that it's them. 
If the student presses "Yes," their name and ID is recorded into a sign-in log that also records the time at which they signed in.

This sign-in record can then be exported by the librarian by using a Librarian Password.
(The report is also exported automatically when the window is closed to ensure the log is kept.)
The password is saved to a separate file and is encoded as a security measure. 

If the file does not contain the encoded password or the file doesn't exist, the librarian will be prompted to make one upon starting the program.
The Librarian can also change the password at any time. (Requires entering the old password for security purposes.)
The librarian can then choose the directory in which to export the sign-in report to, as well as the file name.
(It defaults to the Desktop when it is first started, but the directory is also saved to the preferences file if the librarian changes it.)
When the sign-in log is exported, it will be saved to a .txt file and record the time at which the report was started and ended. 
""" 
 
# === DEFINITION SECTION ===
# This section contains chunks of code that can be reused multiple times. 
# Reused code is called a "Function" or "Definition."

def openDatabase(filename, headerLine, sortBy):
    # Open the input CSV file
    database = pd.read_csv(filename, header=headerLine)
    databaseFrame = pd.DataFrame(database)
 
    # Sort CSV data by desired variable
    sortedDatabase = databaseFrame.sort_values(sortBy)
 
    # check if the sorted version of the CSV is different from the original CSV
    if(not database.equals(sortedDatabase)):
        # if the CSV file is not sorted, return the sorted version if it for use in this program.
        sortedDatabase.to_csv(filename, index=False, header=True)
        return sortedDatabase
    # return original database frame if it's already sorted
    return databaseFrame
 
def openPreferences(filename):
    # Use Open in append+ mode to create the preferences file just in case it doesn't exist.
    #  Close immediately afterwards to prevent confusion.
    createFailsafe =  open(filename, "a+")
    createFailsafe.close()
    # Open the file to read its contents and turn them into a List
    prefFile = open(filename, "r+").readlines()
    # set these values to defaults
    encPass = ""
    prevDir = ""
    database = ""
    # print(len(prefFile))
    if(len(prefFile) == 0):
        # do nothing to the variables if the file is empty
        None
    elif(len(prefFile) == 1):
        # overwrite the encoded password variable if it exists in the file
        encPass = prefFile[0]
    elif(len(prefFile) == 2):
        encPass = prefFile[0]
        prevDir = prefFile[1]
    else:
        # overwrite both the encoded password and directory variables if they both exist in the file
        encPass = prefFile[0]
        prevDir = prefFile[1]
        database = prefFile[2]
    # return as tuple to be unpacked later
    return (encPass, prevDir, database)
 
 
def printMessageToUser(printText):
    # replace the Error Report text in the Sign-In screen with the input text
    lbl_err.config(text=printText)
 
def printMessageToPasswordCreate(printText):
    # replace the Error Report text in the Create Password screen with the input text
    lbl_newPassErr.config(text=printText)
 
def printMessageToPassword(printText):
    # replace the Error Report text in the Enter Password screen with the input text
    lbl_passErr.config(text=printText)

def printMessageToInitalSetup(printText):
    # replace the Error Report text in the Create Password screen with the input text
    lbl_initPrintText.config(text=printText)
 
def printMessageToError(printText):
    # replace the Error Report text in the Create Password screen with the input text
    lbl_errorSetupText.config(text=printText)

 
def displaySignInScreen():
    # bring up the sign in screen
    frame_signin.tkraise()
 
def displayConfirmationScreen():
    global currentFName, currentLName, currentSID, currentGrade
    # write the name, ID, and grade into the labels on the Confirmation screen
    lbl_name.config(text=f"Name: {currentFName} {currentLName}")
    lbl_sID.config(text=f"ID #{currentSID}")
    lbl_grade.config(text=f"Grade {currentGrade}")
    # display the Confirmation screen
    frame_confirm.tkraise()
 
def displayLibrarianPasswordScreen():
    # bring up the Librarian Password screen
    frame_passwd.tkraise()
 
def displayPasswordResetScreen():
    # bring up the Create Password screen
    frame_passwdCreate.tkraise()
 
def displayExportReportScreen():
    # reset the file name to have the current date/time included in it
    ent_fileName.delete(0, "end")
    instant = datetime.now()
    instantF = instant.strftime("%m-%d ")
    ent_fileName.insert(0, f"{defaultFileNameStart}{instantF}Period _")
    # bring up the Export Report screen
    frame_saveReport.tkraise()
 
 
def getDetailsAboutStudent(id):
    # This method will search the Student Database CSV file for a student with the input ID number. 
    # It will return False if no student can be found, and will return the following data if found:
    # The student's first and last name, and their grade.
    global database, invalidInputText
 
    # Search the database for any entries that match the input ID
    student = database.loc[database["ID"] == id]
    if(student.empty):
        # If the .loc() function doesn't find anything, it will have the .empty parameter. 
        # If the student variable has .empty, the student with that ID wasn't found.
        # In this case, return False.
        return False
    else:
        # convert the student data with the matching ID to a List to be easier to export to the rest of the program.
        studList = student.values.tolist()
        # return the last name, first name, and grade using the second, third, and fourth entries
        # in the converted Student list
        return (studList[0][1], studList[0][2], studList[0][3])

def confirmID():
    global minDigits, maxDigits, currentFName, currentLName, currentSID, currentGrade, noStudentFoundText1, noStudentFoundText2, invalidInputText
    # get the current text inside the ID entry box. Check if it is only a number
    studentIDraw = str(ent_sID.get()).strip()
    # if the text inside cannot be converted to decimal, print error to user
    if(not studentIDraw.isdecimal()):
        printMessageToUser(invalidInputText)
        return
    # convert the entry text into a number and get the number of digits
    studentID = int(studentIDraw)
    idDigits = len(str(studentID))
    # print error messages to user if the ID is not within the allowed digit space
    if(idDigits > 1):
        plural = "s"
    else:
        plural = ""
    youEnteredXDigitsText = f"(You entered {idDigits} digit{plural}.)"
    if(minDigits > idDigits):
        printMessageToUser(f"{tooFewDigitsStartText} {invalidDigitCountSharedText}\n{youEnteredXDigitsText}")
        return
    elif(idDigits > maxDigits):
        printMessageToUser(f"{tooManyDigitsStartText} {invalidDigitCountSharedText}\n{youEnteredXDigitsText}")
        return
    # The ID is valid and the database CSV will now be checked for a student with this ID
    else:
        # Check if this is a real student ID
        studentData = getDetailsAboutStudent(studentID)
        # the getDetailsAboutStudent method returns False if no student can be found. 
        # If this is the case, print out appropriate error message.
        if(studentData is False):
            printMessageToUser(f"{noStudentFoundText1}{studentID}{noStudentFoundText2}")
            return
        else:
            # the getDetailsAboutStudent method returns a tuple if the student is found. 
            # Save the tuple contents to appropriate variables 
            # and convert them to strings and ints accordingly
            (lName, fName, grade) = studentData
            currentFName = str(fName)
            currentLName = str(lName)
            currentSID = int(studentID)
            currentGrade = int(grade)
            # display the confirmation screen with appropriate information
            displayConfirmationScreen()
 
def updatePassword(useOldPass = True, pass1RAW = None , pass2RAW = None):
    global preferencesFileName, encPass, librarianPassUpdateText, oldPasswordIncorrectText, newPasswordIncorrectText
    # if no password in the preferences file can be found, 
    # old password is made blank. 
    if(pass1RAW is None):
        pass1RAW = ent_pass1.get()
    if(pass2RAW is None):
        pass2RAW = ent_pass2.get()
    if(not useOldPass):
        oldPass = ""
        pass0 = ""
    else:
        # read the data from the preferences file and get the saved encoded password
        data = open(preferencesFileName, "r+").readlines()
        # print(data[0])
        oldPass = data[0].strip()
        # get the contents of the "enter old password" box and encode them for security
        pass0 = sha256(ent_pass0.get().encode('utf-8')).hexdigest()
    # get the contents of the "enter new password twice" boxes and encode them
    pass1 = sha256(pass1RAW.encode('utf-8')).hexdigest()
    pass2 = sha256(pass2RAW.encode('utf-8')).hexdigest()
    length = len(pass1RAW.strip())

    print(pass1RAW)
    # if the new encoded passwords match and the old entered password matches the one from the file
    if(pass1 == pass2 and pass0 == oldPass and length >= 4):
        # print("Passwords match! Updating password in file...")
        # open the file for writing
        data = open(preferencesFileName, "r+").readlines()
        # set the first line to be the newly entered encoded password
        data[0] = f"{pass1}\n"
        # save the local variable that stores the encoded password to the newly entered password
        encPass = pass1
        # write the updated contents of the file back to it
        with open(preferencesFileName, 'w') as file:
            file.writelines( data )
        signinTime = datetime.now()
        signinTimeFormatted = signinTime.strftime("%I:%M %p")
        currentRecords.append(f"{reportChangePassword}{signinTimeFormatted}")
        # print out confirmation message
        printMessageToUser(librarianPassUpdateText)
        # erase all the data inside the entry boxes
        ent_pass0.delete(0, 'end')
        ent_pass1.delete(0, 'end')
        ent_pass2.delete(0, 'end')
        ent_passInit1.delete(0, 'end')
        ent_passInit2.delete(0, 'end')
        ent_passError1.delete(0, 'end')
        ent_passError2.delete(0, 'end')
        # return to base sign-in screen
        displaySignInScreen()
    # if the entered password doesn't match the one in the file, report error
    elif(pass0 != oldPass):
        printMessageToPasswordCreate(oldPasswordIncorrectText)
    # if the two new passwords don't match, report error
    elif(pass1 != pass2):
        printMessageToInitalSetup(createPasswordIncorrectText)
        printMessageToPasswordCreate(newPasswordIncorrectText)
        printMessageToError(newPasswordIncorrectText)
    elif(len(ent_pass1.get()) < 4):
        printMessageToInitalSetup(passwordTooShortText)
        printMessageToPasswordCreate(passwordTooShortText)
        printMessageToError(passwordTooShortText)

def changeDatabasePath():
    global databasePath, databaseBeginningText, databasePopupText, lbl_currDir, database, currentRecords, reportChangeDatabase
    # open a directory window to choose where to save the file
    newData = filedialog.askopenfilename(title=databasePopupText,filetypes=[("CSV files", "*.csv")]) # shows dialog box and return the path
    # update the variable and space in the file that represent the directory, ONLY if the new directory was picked.
    # Also handles an issue where closing the directory window causes it to have an empty directory.
    if(newData != ""):
        databasePath = newData
    filename = databasePath[ databasePath.rfind("/")+1 :]
    txt = f"{databaseBeginningText}\n{filename}"  
    database = openDatabase(databasePath, databaseHeaderLine, databaseSortBy)
    signinTime = datetime.now()
    signinTimeFormatted = signinTime.strftime("%I:%M %p")
    currentRecords.append(f"{reportChangeDatabase}{signinTimeFormatted}")
    
    print(txt)
    # UPDATE TO HAVE THE LIBRARIAN SCREEN UPDATE AS WELL
    # lbl_data.config(text=txt)
    lbl_currData.config(text=txt)
    lbl_errData.config(text=txt)
    lbl_database.config(text=txt)
    updateDatabaseInFile()

def updateDatabaseInFile():
    global databasePath, preferencesFileName
    with open(preferencesFileName, 'r') as file:
        # save the contents of the file into a List data structure
        data = file.readlines()
 
    # update the file to include new directory. 
    # If it is blank, save it with a space above it.
    # Otherwise, just save it as normal.
    if(len(data) < 3):
        while(len(data) <= 3):
            data.append("")
        data.append(f'\n{databasePath}')
    else:
        data[2] = f'{databasePath}\n'
    print(data)
    # write everything back to the file
    with open(preferencesFileName, 'w') as file:
        file.writelines( data )


def updateDirectoryInFile():
    global saveDirectory, preferencesFileName
    with open(preferencesFileName, 'r') as file:
        # save the contents of the file into a List data structure
        data = file.readlines()
 
    # update the file to include new directory. 
    # If it is blank, save it with a space above it.
    # Otherwise, just save it as normal.
    if(len(data) <= 1):
        data.append(f'\n{saveDirectory}')
    else:
        data[1] = f'{saveDirectory}\n'
    print(data)
    # write everything back to the file
    with open(preferencesFileName, 'w') as file:
        file.writelines( data )
 
def changeSaveDirectory():
    global saveDirectory, saveDirectoryBeginningText, directoryPopupText, lbl_currDir, reportChangeSave
    # open a directory window to choose where to save the file
    newDir = filedialog.askdirectory(title=directoryPopupText) # shows dialog box and return the path
    # update the variable and space in the file that represent the directory, ONLY if the new directory was picked.
    # Also handles an issue where closing the directory window causes it to have an empty directory.
    if(newDir != ""):
        saveDirectory = newDir
    txt = f"{saveDirectoryBeginningText}\n{saveDirectory}"  
    signinTime = datetime.now()
    signinTimeFormatted = signinTime.strftime("%I:%M %p")
    currentRecords.append(f"{reportChangeSave}{signinTimeFormatted}")
    print(txt)
    lbl_dir.config(text=txt)
    lbl_currDir.config(text=txt)
    lbl_errDir.config(text=txt)
    updateDirectoryInFile()
 
 # A simplified command for the initial setup screen to setup the password and directory in one button

def updatePassAndDir():
    updatePassword(False, ent_passInit1.get(), ent_passInit2.get())
    updateDirectoryInFile()
    printMessageToUser("Inital setup completed")

def fixPassword():
    updatePassword(False, ent_passError1.get(), ent_passError2.get())

def fixSave():
    updateDirectoryInFile()
    displaySignInScreen()

def fixDatabase():
    updateDatabaseInFile()
    displaySignInScreen()

def confirmYes():
    global currentRecords, currentFName, currentLName, currentSID, currentGrade, signInSuccessfulText
    # get the datetime that the user confirmed their identity and format it to be the time only
    signinTime = datetime.now()
    signinTimeFormatted = signinTime.strftime("%I:%M %p")
    # print out the sign-in log text and append it to the records list
    text = f"{currentFName} {currentLName} (ID #{currentSID}, Grade {currentGrade}) signed in at {signinTimeFormatted}."
    print(text)
    currentRecords.append(text)
    # reset all the data on the screen and replace the error reporting text with a confirmation message
    confirmNo()
    printMessageToUser(signInSuccessfulText)
 
def confirmNo():
    global currentFName, currentLName, currentSID, currentGrade
    # reset the variables tied to the signed-in user, reset the error message space on the sign-in screen, and return to the sign-in screen 
    currentFName = ""
    currentLName = ""
    currentSID = 0
    currentGrade = 0
    printMessageToUser("")
    lbl_name.config(text="")
    lbl_sID.config(text="")
    lbl_grade.config(text="")
    ent_sID.delete(0, 'end')
    displaySignInScreen()
 
 
def confirmLibPass():
    global preferencesFileName, encPass, incorrectPasswordText, reportPreviewHeadingText
    # grab and encode the text entry in the password box
    entPass = sha256(ent_libPass.get().encode('utf-8')).hexdigest()
    # if the password in the box matches the saved password
    if(entPass == encPass):
        # print("Password is correct. Bringing up screen.")
        displayExportReportScreen()
        # update the report display label with the current report
        lbl_report.config(text=f"{reportPreviewHeadingText}\n{compileSigninList()}")
        # clear out the important entry spaces and labels to ensure security
        clearEntriesAndPrints()
    else:
        # print("Not correct.")
        printMessageToPassword(incorrectPasswordText)
 
 
def clearEntriesAndPrints():
    # erase the contents of the important entry spaces to ensure security
    ent_pass0.delete(0, 'end')
    ent_pass1.delete(0, 'end')
    ent_pass2.delete(0, 'end')
    ent_libPass.delete(0, 'end')
    ent_sID.delete(0, 'end')
    # erase all the error prints
    printMessageToUser("")
    printMessageToPassword("")
    printMessageToPasswordCreate("")
 
def clearAndDisplayLogin():
    # just combines these two methods for easy access in one button
    clearEntriesAndPrints()
    displaySignInScreen()
 
 
def compileSigninList():
    global currentRecords
    # initialize compiled report variable
    compiledReport = ""
    for i in range(len(currentRecords)):
        # loop through the current records list and add each element to the string
        compiledReport += f"{currentRecords[i]}\n"
    # get rid of any additional whitespace and return it
    return compiledReport.strip()
 
def saveFile(windowClosed=False):
    global saveDirectory, currentRecords, reportStartExportText, signInExportSuccessfulText, reportExportLibrarianText, reportExportShutdownText, defaultFileNameStart
    
    # get the time of the export and format it
    exportTime = datetime.now()
    exportTimeFormatted = exportTime.strftime("%m/%d/%y at %I:%M %p")
    # add the time that the file was exported to the end of the file.
    # also include the reason the file was exported
    if(windowClosed):
        reason = f"{reportExportStart}{reportExportAutomaticText}on "
        filenameTime = exportTime.strftime("%m-%d %I-%M %p")
        saveName = f"{defaultFileNameStart}{filenameTime}"
    else:
        reason = f"{reportExportStart}{reportExportManualText}on "
        saveName = ent_fileName.get()
    fullReport = f"{compileSigninList()}\n{reason}{exportTimeFormatted}."
    # get the file name typed in the box and trim off the .txt if they typed it
    
    if(saveName.endswith(".txt")):
        saveName = saveName[:-4]
    # get the full file path and name using the save directory and name
    completePathName = os.path.join(saveDirectory, f"{saveName}.txt")
    # check if the starting file name is valid and not already taken
    nameValid = False
    offsetNumber = 0
    # loop until a valid file name is found
    while not nameValid:
        # check if a file with the current file name exists
        if(os.path.isfile(completePathName)):
            # add one to the offset number and set the file save name to have the offset number tailing the file name
            offsetNumber += 1
            completePathName = os.path.join(saveDirectory, f"{saveName} ({offsetNumber}).txt")
        else:
            # the file with this name doesn't exist, so set the variable to true to end the loop
            nameValid = True
    print(completePathName)
    # print(f"Full Report: {fullReport}")
    # create the file via open(), write to it, and close.
    with open(completePathName, "w") as file:
        file.write(fullReport)
    # print("Report successfully exported. Clearing report from program and resetting...")
    if(not windowClosed): 
        # if the program hasn't shut down, reset the records list and set it to new values accordingly
        currentRecords.clear()
        currentRecords = [f"{reportStartExportText}{exportTimeFormatted}."]
        # bring up the login screen and display a message to the user
        clearAndDisplayLogin()
        printMessageToUser(signInExportSuccessfulText)
 
#Define function to hide the widget
def hide_widget(widget):
   widget.grid_remove()


# === GUI SETUP AND MAIN CODE SECTION === 
if __name__ == "__main__":
    # The variable declarations below is just setting up the fundamentals of the sign-in window. The variables above are simply for ease of locating.
    # The window dimensions and padding (space  between screen elements) are measured in pixels.
    windowWidth = 1440
    windowHeight = 810
    universalFont = "Arial"
    
    # these numbers represent the minimum and maximum amount of numbers to allow for an ID
    minDigits = 4
    maxDigits = 7
 
    # Easy place to access most the text used in the program
    # Title strings
    windowTitle = "Study Hall Sign-in"
    confirmTitle = "Is this you?"
    libPassText = "Enter Librarian Password to continue"
    libPassCreateText = "Create a Librarian Password"
    initSetupText = "Initial Setup Screen"
    errorText = "An error occured"
    exportTitleText = "Export Report"
 
    
    signInInstructionText = "Type in your Student ID below to sign into Study Hall"
    libPassCreateDescText = "This will be entered by the librarian\nto authorize the exporting of the sign-in report."
    initSetupDescText = "Please have the librarian/operator set up the program."
    errorDescDefaultText = "DEFAULT ERROR MESSAGE."
    errorDescPasswordText = "The password could not be found.\nPlease recreate the password below."
    errorDescSaveText = "The saving directory for reports has been moved or deleted.\nPlease relocate the directory or specify a new one below."
    errorDescDatabaseText = "The Student Database file has been moved or deleted.\nPlease relocate the database or specify a new one below."

    exportNoticeText = "Saving this file will restart the sign-in log"
 
    enterPassOldText = "Enter old password"
    enterPassNewText = "Enter new password twice"
    enterPassCreateText = "Create password (type it twice)"
    saveDirectoryBeginningText = "Current saving directory:"
    databaseBeginningText = "Current database file:"
    currentFileNameLabelText = "Current file name: (type to change)"
    directoryPopupText = "Select Folder to Save Report to"
    databasePopupText = "Select Database File"
    reportPreviewHeadingText = "Preview of Report:"
 
    signInExportSuccessfulText = "Sign in report successfully exported"
    librarianPassUpdateText = "Librarian password updated successfully"
    signInSuccessfulText = "Successfully signed in. Enjoy your time in study hall!"
    oldPasswordBlankText = "Leave \"old password\" space blank"
 
    incorrectPasswordText = "Incorrect password"
    oldPasswordIncorrectText = "Incorrect old password"
    newPasswordIncorrectText = "New passwords do not match"
    createPasswordIncorrectText = "Passwords do not match"
    passwordTooShortText = "Password too short. It must be more than 4 characters."
    invalidInputText = "Couldn't get an ID from that.\nRemove any letters and/or spaces and try again."
    noStudentFoundText1 = "No student with ID #"
    noStudentFoundText2 = " was found.\nCheck for typos or ask for assistance."
    tooManyDigitsStartText = "Too many digits."
    tooFewDigitsStartText = "Too few digits."
    invalidDigitCountSharedText = f"Student ID's must be {minDigits}-{maxDigits} digits long."
 
    signInButtonText = "Sign in"
    confirmYesButtonText = "Yes"
    confirmNoButtonText = "No"
    backButtonText = "Back"
    finishSetupButtonText = "Complete Setup"
    fixErrorButtonText = "Continue"
    changePasswordButtonText = "Change Password"
    librarianPasswordEnterButtonText = "Continue"
    changeDirectoryText = "Change Directory"
    changeDatabaseText = "Change Database File"
    saveFileButtonText = "Save File"
    updatePasswordButtonText = "Change"
    exportReportButtonText = "Librarian Mode"
 
    reportStartExportText = "Report START from PREVIOUS REPORT EXPORT on "
    reportStartProgramText = "Report START from PROGRAM START on "
    reportExportStart = "Report exported "
    reportExportManualText = "MANUALLY by librarian "
    reportExportAutomaticText = "AUTOMATICALLY due to program shutdown "
    reportChangePassword = "Password was UPDATED at "
    reportChangeSave = "Report save location was UPDATED at "
    reportChangeDatabase = "Student Database was UPDATED at "

    
    defaultFileNameStart = "SH Signin Report "
    initalSetup = False
 
    # set up various font configurations
    titleFont = (universalFont, 50, "bold")
    largeFont = (universalFont, 35)
    dataFont = (universalFont, 25, "bold")
    entryFont = (universalFont, 25)
    smallFont = (universalFont, 20)
    smallBoldFont = (universalFont, 20, "bold")

 
    # variables used for files
    preferencesFileName = "preferences.ini"
    if(os.path.isfile(preferencesFileName)):
        (encPass, saveDirectory, databasePath) = openPreferences(preferencesFileName)
        encPass = encPass.strip()
        saveDirectory = saveDirectory.strip()
        databasePath = databasePath.strip()
        databaseName = databasePath[ databasePath.rfind("/")+1 :]
        initialSetup = False
        
        noPass = False
        noSave = False
        noData = False
        if(encPass is ""):
            noPass = True
        if(not os.path.isdir(saveDirectory)):
            noSave = True
        if(not os.path.isfile(databasePath)):
            noData = True

    else:
        (encPass, saveDirectory, databasePath) = openPreferences(preferencesFileName)
        encPass = None
        saveDirectory = None
        databasePath = None
        databaseName = None
        initialSetup = True
        noPass = False
        noSave = False
        noData = False

    # print(noPass, noSave, noData)

    # print(encPass, saveDirectory, databasePath)
    databaseHeaderLine = 0
    databaseSortBy = "ID"
 
    # visual padding standard
    pad = 15
    
    # get data from all the files needed (student database and preferences file)
    if(databasePath is not "" and not noData and not initialSetup ):
        database = openDatabase(databasePath, databaseHeaderLine, databaseSortBy)
    else:
        database = None
  
    print(database)
 
    # if there's nothing recorded for the save directory, set it to the user's Desktop by default
    if(saveDirectory == ""):
        #set default to desktop
        # saveDirectory = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        saveDirectory = pathlib.Path.home()
        updateDirectoryInFile()
 
    # initialize the sign-in record list with a report timestamp
    bootupDateTime = datetime.now()
    bootupDateTimeFormatted = bootupDateTime.strftime("%m/%d/%y at %I:%M %p")
    initRecordText = f"{reportStartProgramText}{bootupDateTimeFormatted}."
    # print(initRecordText)
    currentRecords = [initRecordText]
 
    # reformat the program startup time to be shorter and used for the default report file name 
    bootupTimeFormat2 = bootupDateTime.strftime("%m-%d ")
    saveFileName = f"{defaultFileNameStart}{bootupTimeFormat2}Period _"
 
    # variables used for displaying the name of the user signing in
    currentFName = ""
    currentLName = ""
    currentSID = 0
    currentGrade = 0
    


    # INITIALIZE THE WINDOW
    root = tk.Tk()
    root.wm_geometry(f"{windowWidth}x{windowHeight}")
    root.title(windowTitle)
    root.columnconfigure(2, weight=10)
    
    #### THE SIGN IN SCREEN                                 ####
    #### PROGRAM NORMALLY BEGINS ON THIS SCREEN             ####
    #### ENTER STUDENT ID OR HIT THE EXPORT REPORT BUTTON   ####
    frame_signin = tk.Frame(root)
    frame_signin.grid(row=0, column=2, sticky='news')
    frame_signin.columnconfigure(2, weight=5)
 
    # Large Bold title at the top
    lbl_title = tk.Label(frame_signin, text=windowTitle, font=titleFont, pady=pad*5).grid(row=5,column=2,sticky="news")
 
    # Instructional box
    lbl_signinInstructions = tk.Label(frame_signin, text=signInInstructionText, font=largeFont, pady=pad*2).grid(row=7,column=2)
    
    # Entry box for ID
    ent_sID = tk.Entry(frame_signin, bd=5, font=entryFont)
    ent_sID.grid(row=9, column=2)
 
    # Enter button for ID entry box
    btn_signin = tk.Button(frame_signin, text=signInButtonText, font=smallBoldFont, command=confirmID).grid(row=10,column=2)
 
    # Error message space (used to print errors to the user or other messages.)
    lbl_err = tk.Label(frame_signin, font=entryFont, fg="red", pady=pad*5)
    lbl_err.grid(row=12,column=2)
 
    # Enter button for ID entry box
    btn_exportReport = tk.Button(frame_signin, text=exportReportButtonText, font=smallFont, command=displayLibrarianPasswordScreen).grid(row=30,column=2)
 
 
    #### THE USER CONFIRMATION SCREEN                   ####
    #### DISPLAYED WHEN VALID STUDENT ID IS ENTERED     ####
    #### MUST HIT YES OR NO TO CONFIRM/DENY IDENTITY    ####
    frame_confirm = tk.Frame(root)
    frame_confirm.grid(row=0, column=2, sticky='NEWS')
    frame_confirm.columnconfigure(2, weight=5)
 
    # "Is this you?" text at the top
    lbl_confirmTitle = tk.Label(frame_confirm, text=confirmTitle, font=titleFont, pady=pad*7)
    lbl_confirmTitle.grid(row=6,column=2)
 
    # Name print
    lbl_name = tk.Label(frame_confirm, text="", font=dataFont, pady=pad)
    lbl_name.grid(row=7,column=2)
 
    # ID print
    lbl_sID = tk.Label(frame_confirm, text="", font=dataFont, pady=pad)
    lbl_sID.grid(row=8,column=2)
 
    # Grade print
    lbl_grade = tk.Label(frame_confirm, text="", font=dataFont, pady=pad)
    lbl_grade.grid(row=9,column=2)
 
    # Yes button
    btn_yes = tk.Button(frame_confirm, text=confirmYesButtonText, font=smallBoldFont, command=confirmYes).grid(row=10,column=2)
 
    # No button
    btn_no = tk.Button(frame_confirm, text=confirmNoButtonText, font=smallFont, command=confirmNo).grid(row=11,column=2)
 
 
    #### THE LIBRARIAN PASSWORD SCREEN                  ####
    #### DISPLAYED WHEN "EXPORT REPORT" BUTTON IS HIT   ####
    #### LIBRARIAN MUST ENTER OR RESET PASSWORD         ####
    frame_passwd = tk.Frame(root)
    frame_passwd.grid(row=0, column=2, sticky='NEWS')
    frame_passwd.columnconfigure(2, weight=5)
 
    # Title text
    lbl_passwdTitle = tk.Label(frame_passwd, text=libPassText, font=titleFont, pady=pad*5)
    lbl_passwdTitle.grid(row=6,column=2)
 
    # Error message space (For errors with the password entry.)
    lbl_passErr = tk.Label(frame_passwd, font=entryFont, fg="red", pady=pad*2)
    lbl_passErr.grid(row=7,column=2)
 
    # Entry box for password
    ent_libPass = tk.Entry(frame_passwd, bd=5, font=entryFont, show="*")
    ent_libPass.grid(row=8, column=2)
 
    # Enter button for password entry box
    btn_libPassEnter = tk.Button(frame_passwd, text=librarianPasswordEnterButtonText, font=smallBoldFont, command=confirmLibPass).grid(row=9,column=2)
 
    # Button for going back to the sign-in screen
    btn_back = tk.Button(frame_passwd, text=backButtonText, font=smallFont, command=clearAndDisplayLogin).grid(row=10,column=2)
 
    # Button for forgot password
    btn_passForgot = tk.Button(frame_passwd, text=changePasswordButtonText, font=smallFont, command=displayPasswordResetScreen).grid(row=11,column=2)
 
 
    #### THE REPORT PRINTOUT SCREEN                             ####
    #### DISPLAYED WHEN LIBRARIAN ENTERS THEIR PASSWORD         ####
    #### CONFIRM THE FILE NAME/DIRECTORY AND SAVE THE FILE      ####
    frame_saveReport = tk.Frame(root)
    frame_saveReport.grid(row=0, column=2, sticky='NEWS')
    frame_saveReport.columnconfigure(0, weight=5)
    frame_saveReport.columnconfigure(1, weight=5)
    frame_saveReport.columnconfigure(2, weight=5)
 
    # Title text
    lbl_exportTitle = tk.Label(frame_saveReport, text=exportTitleText, font=largeFont, pady=pad*2)
    lbl_exportTitle.grid(row=0,column=0)
 
    # Report preview
    lbl_report = tk.Label(frame_saveReport, text=reportPreviewHeadingText, font=smallFont, anchor="e", pady=pad)
    lbl_report.grid(row=0,column=2)
 
    # save path directory
    lbl_dir = tk.Label(frame_saveReport, text=f"{saveDirectoryBeginningText}\n{saveDirectory}", font=smallFont, pady=pad)
    lbl_dir.grid(row=1,column=0)
    
    # Change directory button
    btn_changeDir = tk.Button(frame_saveReport, text=changeDirectoryText, font=smallFont, command=changeSaveDirectory).grid(row=3,column=0)
 
    # save name 
    lbl_fileNameLabel = tk.Label(frame_saveReport, text=currentFileNameLabelText, font=smallFont, pady=pad)
    lbl_fileNameLabel.grid(row=5,column=0)
    
    # Entry box for password
    ent_fileName = tk.Entry(frame_saveReport, bd=5, font=entryFont, width=30)
    ent_fileName.grid(row=6, column=0)
    ent_fileName.delete(0, "end")
    ent_fileName.insert(0, f"{saveFileName}")
 
    # export notice text
    lbl_notice = tk.Label(frame_saveReport, text=exportNoticeText, font=smallFont, pady=pad*2)
    lbl_notice.grid(row=7,column=0)
 
    # save the file button
    btn_saveFile = tk.Button(frame_saveReport, text=saveFileButtonText, font=smallBoldFont, command=saveFile).grid(row=8,column=0)
 
    # Back to sign-in
    btn_exportBack = tk.Button(frame_saveReport, text=backButtonText, font=smallFont, command=clearAndDisplayLogin).grid(row=9,column=0)
 
    # Update Database label
    lbl_database = tk.Label(frame_saveReport, text=f"{databaseBeginningText}\n{databaseName}", font=smallFont, pady=pad*2)
    lbl_database.grid(row=11,column=0)

    # Update database button
    btn_databaseChange = tk.Button(frame_saveReport, text=changeDatabaseText, font=smallFont, command=changeDatabasePath).grid(row=12,column=0)


 
    #### THE CREATE LIBRARIAN PASSWORD SCREEN                                   ####
    #### DISPLAYED WHEN "RESET PASSWORD" IS SELECTED OR IF NO PASSWORD IS SET   ####
    #### LIBRARIAN MUST ENTER OLD PASSWORD AND SET NEW PASSWORD TO CHANGE       ####
    frame_passwdCreate = tk.Frame(root)
    frame_passwdCreate.grid(row=0, column=2, sticky='NEWS')
    frame_passwdCreate.columnconfigure(2, weight=5)
 
    # Title text
    lbl_passwdTitle = tk.Label(frame_passwdCreate, text=libPassCreateText, font=titleFont, pady=pad*2)
    lbl_passwdTitle.grid(row=0,column=2)
 
    # Instructional box
    lbl_passCreateInstructions = tk.Label(frame_passwdCreate, text=libPassCreateDescText, font=largeFont, pady=pad).grid(row=1,column=2)

    # Error message space (for printing errors with resetting the password.) 
    lbl_newPassErr = tk.Label(frame_passwdCreate, font=entryFont, fg="red", pady=pad)
    lbl_newPassErr.grid(row=2,column=2)
 
    # "Enter old password" label
    lbl_passOld = tk.Label(frame_passwdCreate, text=enterPassOldText, font=entryFont, pady=pad*2).grid(row=4,column=2)
 
    # Entry box for old password confirmation
    ent_pass0 = tk.Entry(frame_passwdCreate, bd=5, font=entryFont, show="*")
    ent_pass0.grid(row=5, column=2)
 
    # "Enter new password twice" label
    lbl_passNew = tk.Label(frame_passwdCreate, text=enterPassNewText, font=entryFont, pady=pad*2).grid(row=7,column=2)
 
    # First Entry box for new password
    ent_pass1 = tk.Entry(frame_passwdCreate, bd=5, font=entryFont, show="*")
    ent_pass1.grid(row=8, column=2)
 
    # Second Entry box for new password
    ent_pass2 = tk.Entry(frame_passwdCreate, bd=5, font=entryFont, show="*")
    ent_pass2.grid(row=9, column=2)
 
    # Enter button
    btn_libPassUpdate = tk.Button(frame_passwdCreate, text=updatePasswordButtonText, font=smallFont, command=updatePassword).grid(row=11,column=2)
 
    # back button to return to sign-in screen
    btn_libPassBack = tk.Button(frame_passwdCreate, text=backButtonText, font=smallFont, command=clearAndDisplayLogin).grid(row=12,column=2)
 

 
    #### THE INITIAL SETUP SCREEN                                               ####
    #### REQUIRES LIBRARIAN TO CREATE A PASSWORD AND DECIDE SAVE LOCATION       ####
    frame_initSetup = tk.Frame(root)
    frame_initSetup.grid(row=0, column=2, sticky='NEWS')
    frame_initSetup.columnconfigure(2, weight=5)
 
    # Title text
    lbl_initTitle = tk.Label(frame_initSetup, text=initSetupText, font=titleFont, pady=pad*2)
    lbl_initTitle.grid(row=0,column=2)
 
    # Instructional box
    lbl_initInstructions = tk.Label(frame_initSetup, text=initSetupDescText, font=largeFont).grid(row=1,column=2)
 
    # Error message space (for printing errors with resetting the password.) 
    lbl_initPrintText = tk.Label(frame_initSetup, font=entryFont, fg="red", pady=pad)
    lbl_initPrintText.grid(row=2,column=2)
  
    # "Create password (type it in twice)" label
    lbl_passNew = tk.Label(frame_initSetup, text=enterPassCreateText, font=entryFont, pady=pad).grid(row=7,column=2)
 
    # First Entry box for password
    ent_passInit1 = tk.Entry(frame_initSetup, bd=5, font=entryFont, show="*")
    ent_passInit1.grid(row=8, column=2)
 
    # Second Entry box for password
    ent_passInit2 = tk.Entry(frame_initSetup, bd=5, font=entryFont, show="*")
    ent_passInit2.grid(row=9, column=2)
  
    # Current Directory label
    lbl_currDir = tk.Label(frame_initSetup, text=f"{saveDirectoryBeginningText}\n{saveDirectory}", font=entryFont, pady=pad*2)
    lbl_currDir.grid(row=10,column=2)

    # Change directory button
    btn_currDirChange = tk.Button(frame_initSetup, text=changeDirectoryText, font=smallFont, command=changeSaveDirectory).grid(row=11,column=2)

    # Current Directory label
    lbl_currData = tk.Label(frame_initSetup, text=f"{databaseBeginningText}\n{databaseName}", font=entryFont, pady=pad*2)
    lbl_currData.grid(row=12,column=2)

    # Change directory button
    btn_currDataChange = tk.Button(frame_initSetup, text=changeDatabaseText, font=smallFont, command=changeDatabasePath).grid(row=13,column=2)


    # back button to return to sign-in screen
    btn_initSetupConfirm = tk.Button(frame_initSetup, text=finishSetupButtonText, font=smallFont, command=updatePassAndDir).grid(row=14,column=2)



    #### THE ERROR FIXTURE SCREEN                       ####
    #### ASKS LIBRARIAN TO FIX PROBLEM WITH DATA        ####
    #### (Password, Save directory, or database file)   ####
    frame_error = tk.Frame(root)
    frame_error.grid(row=0, column=2, sticky='NEWS')
    frame_error.columnconfigure(2, weight=5)
 
    # Title text
    lbl_errorTitle = tk.Label(frame_error, text=errorText, font=titleFont, pady=pad*2)
    lbl_errorTitle.grid(row=0,column=2)
 
    # Instructional box
    lbl_errorInstructions = tk.Label(frame_error, text=errorDescDefaultText, font=largeFont)
    lbl_errorInstructions.grid(row=1,column=2)
 
    # Error message space (for printing errors with resetting the password.) 
    lbl_errorSetupText = tk.Label(frame_error, font=entryFont, fg="red", pady=pad)
    lbl_errorSetupText.grid(row=2,column=2)
   
    # "Create password (type it in twice)" label
    lbl_passError = tk.Label(frame_error, text=enterPassCreateText, font=entryFont, pady=pad)
    lbl_passError.grid(row=7,column=2)

    # First Entry box for password
    ent_passError1 = tk.Entry(frame_error, bd=5, font=entryFont, show="*")
    ent_passError1.grid(row=8, column=2)
 
    # Second Entry box for password
    ent_passError2 = tk.Entry(frame_error, bd=5, font=entryFont, show="*")
    ent_passError2.grid(row=9, column=2)
  
    # Current Directory label
    lbl_errDir = tk.Label(frame_error, text=f"{saveDirectoryBeginningText}\n{saveDirectory}", font=entryFont, pady=pad*2)
    lbl_errDir.grid(row=10,column=2)

    # Change directory button
    btn_errDirChange = tk.Button(frame_error, text=changeDirectoryText, font=smallFont, command=changeSaveDirectory)
    btn_errDirChange.grid(row=11,column=2)

    # Current Directory label
    lbl_errData = tk.Label(frame_error, text=f"{databaseBeginningText}\n{databaseName}", font=entryFont, pady=pad*2)
    lbl_errData.grid(row=12,column=2)

    # Change directory button
    btn_errDataChange = tk.Button(frame_error, text=changeDatabaseText, font=smallFont, command=changeDatabasePath)
    btn_errDataChange.grid(row=13,column=2)


    # back button to return to sign-in screen
    btn_errFixPass = tk.Button(frame_error, text=fixErrorButtonText, font=smallFont, command=fixPassword)
    btn_errFixPass.grid(row=14,column=2)

    # back button to return to sign-in screen
    btn_errFixSave = tk.Button(frame_error, text=fixErrorButtonText, font=smallFont, command=fixSave)
    btn_errFixSave.grid(row=14,column=2)

    # back button to return to sign-in screen
    btn_errFixData = tk.Button(frame_error, text=fixErrorButtonText, font=smallFont, command=fixDatabase)
    btn_errFixData.grid(row=14,column=2)




 
    #### STARTUP SCREEN SETUP ####
    if(initialSetup):
        # if this is the first time starting up the program, display the initial setup screen
        frame_initSetup.tkraise()
    elif(noPass):
        frame_error.tkraise()
        lbl_errorInstructions.config(text=errorDescPasswordText)
        hide_widget(lbl_errDir)
        hide_widget(btn_errDirChange)
        hide_widget(lbl_errData)
        hide_widget(btn_errDataChange)
        hide_widget(btn_errFixSave)
        hide_widget(btn_errFixData)
    elif(noSave):
        frame_error.tkraise()
        lbl_errorInstructions.config(text=errorDescSaveText)
        hide_widget(lbl_passError)
        hide_widget(ent_passError1)
        hide_widget(ent_passError2)
        hide_widget(lbl_errData)
        hide_widget(btn_errDataChange)
        hide_widget(btn_errFixPass)
        hide_widget(btn_errFixData)
    elif(noData):
        frame_error.tkraise()
        lbl_errorInstructions.config(text=errorDescDatabaseText)
        hide_widget(lbl_passError)
        hide_widget(ent_passError1)
        hide_widget(ent_passError2)
        hide_widget(lbl_errDir)
        hide_widget(btn_errDirChange)
        hide_widget(btn_errFixSave)
        hide_widget(btn_errFixPass)
    else:
        # open to the sign-in screen
        frame_signin.tkraise()
    
    # begin the window loop to keep the window open
    root.mainloop()
 
    # After this point, the window is closed. The program should save whatever data is still left.
    # only save the data if the length of the records is greater than 1 
    # (aka it has more than just the Log Start time inside it.) 
    if(len(currentRecords) > 1):
        saveFile(True)
 


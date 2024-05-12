from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import pymysql

window = Tk()
window.geometry("1000x600")
window.title("Billing")
window.configure(bg="#f0f0f0")  # Set background color


# ===========field listener ==========================
def quantityFieldListener(a, b, c):
    global quantityVar
    global costVar
    global itemRate
    quantity = quantityVar.get()
    if quantity != "":
        try:
            quantity = float(quantity)
            cost = quantity * itemRate
            quantityVar.set("%.2f" % quantity)
            costVar.set("%.2f" % cost)
        except ValueError:
            quantity = quantity[:-1]
            quantityVar.set(quantity)
    else:
        quantity = 0
        quantityVar.set("%.2f" % quantity)


def costFieldListener(a, b, c):
    global quantityVar
    global costVar
    global itemRate
    cost = costVar.get()
    if cost != "":
        try:
            cost = float(cost)
            quantity = cost / itemRate
            quantityVar.set("%.2f" % quantity)
            costVar.set("%.2f" % cost)
        except ValueError:
            cost = cost[:-1]
            costVar.set(cost)
    else:
        cost = 0
        costVar.set(cost)


# ============= global variable for entries ===========
# ======== login variable ========
usernameVar = StringVar()
passwordVar = StringVar()

# ============ main window variable ========
options = []
rateDict = {}
itemVariable = StringVar()
quantityVar = StringVar()
quantityVar.trace_add("write", quantityFieldListener)
itemRate = 2
rateVar = StringVar()
rateVar.set("%.2f" % itemRate)
costVar = StringVar()
costVar.trace_add("write", costFieldListener)
# ============= mainTreeView ==========
billsTV = ttk.Treeview(height=15, columns=("Rate", "Quantity", "Cost"))

# ==========update tree View
updateTV = ttk.Treeview(height=15, columns=("Name", "Rate", "type", "Store_Type"))


# ============= add item Variables ==========
storeOptions = ["Frozen", "Fresh"]
addItemNameVar = StringVar()
addItemRateVar = StringVar()
addItemTypeVar = StringVar()
addStoredVar = StringVar()
addStoredVar.set(storeOptions[0])
totalCost = 0.0
totalCostVar = StringVar()
totalCostVar.set("Total Cost = {}".format(totalCost))
itemLists = list()
updateItemId = ""


# =============funtion to generate bill=====================
def generate_bill():
    global itemVariable
    global quantityVar
    global itemRate
    global costVar
    global itemLists
    global totalCost
    global totalCostVar
    itemName = itemVariable.get()
    quantity = quantityVar.get()
    cost = costVar.get()
    conn = pymysql.connect(host="localhost", user="root", passwd="", db="billservice")
    cursor = conn.cursor()

    query = "insert into bill (name,quantity, rate, cost) values('{}','{}','{}','{}')".format(
        itemName, quantity, itemRate, cost
    )
    cursor.execute(query)
    conn.commit()
    conn.close()
    listDict = {"name": itemName, "rate": itemRate, "quantity": quantity, "cost": cost}
    itemLists.append(listDict)
    totalCost += float(cost)
    quantityVar.set("0")
    costVar.set("0")
    updateListView()
    totalCostVar.set("Total Cost = {}".format(totalCost))


def OnDoubleClick(event):
    global addItemNameVar
    global addItemRateVar
    global addItemTypeVar
    global addStoredVar
    global updateItemId
    item = updateTV.selection()
    updateItemId = updateTV.item(item, "text")
    item_detail = updateTV.item(item, "values")
    item_index = storeOptions.index(item_detail[3])
    addItemTypeVar.set(item_detail[2])
    addItemRateVar.set(item_detail[1])
    addItemNameVar.set(item_detail[0])
    addStoredVar.set(storeOptions[item_index])


def updateListView():
    records = billsTV.get_children()
    for element in records:
        billsTV.delete(element)
    for row in itemLists:
        billsTV.insert(
            "",
            "end",
            text=row["name"],
            values=(row["rate"], row["quantity"], row["cost"]),
        )


def getItemLists():
    records = updateTV.get_children()

    for element in records:
        updateTV.delete(element)

    conn = pymysql.connect(host="localhost", user="root", passwd="", db="billservice")
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    query = "select * from itemlist"
    cursor.execute(query)
    data = cursor.fetchall()
    for row in data:
        updateTV.insert(
            "",
            "end",
            text=row["nameid"],
            values=(row["name"], row["rate"], row["type"], row["storetype"]),
        )
    updateTV.bind("<Double-1>", OnDoubleClick)

    conn.close()


def print_bill():
    global itemLists
    global totalCost

    billString = ""
    billString += "=====================Receipt==========================\n\n"
    billString += "======================================================\n"
    billString += "{:<20}{:<10}{:<15}{:<10}\n".format(
        "Name", "Rate", "Quantity", "Cost"
    )
    billString += "======================================================\n"

    for item in itemLists:
        billString += "{:<20}{:<10}{:<15}{:<10}\n".format(
            item["name"], item["rate"], item["quantity"], item["cost"]
        )

    billString += "======================================================\n"
    billString += "{:<20}{:<10}{:<15}{:<10}\n".format("Total Cost", " ", " ", totalCost)

    billFile = filedialog.asksaveasfile(mode="w", defaultextension=".txt")
    if billFile is None:
        messagebox.showerror("Invalid file Name", "Please enter valid name")
    else:
        billFile.write(billString)
        billFile.close()

    print(billString)

    itemLists = []
    totalCost = 0.0
    updateListView()
    totalCostVar.set("Total Cost = {}".format(totalCost))


# ===============function to logOut===================
def LogOut():
    remove_all_widgets()
    loginWindow()


def moveToUpdate():
    remove_all_widgets()
    updateItemWindow()


# ===============function to move to veiw bills window========
def movetoBills():
    remove_all_widgets()
    viewAllBills()


# ==========function to remove all widget
def remove_all_widgets():
    global window
    for widget in window.winfo_children():
        widget.grid_remove()


# =================update bill data===========
def updateBillsData():
    records = billsTV.get_children()

    for element in records:

        billsTV.delete(element)

    conn = pymysql.connect(host="localhost", user="root", passwd="", db="billservice")
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    query = "select * from bill"
    cursor.execute(query)
    data = cursor.fetchall()

    for row in data:
        billsTV.insert(
            "",
            "end",
            text=row["name"],
            values=(row["rate"], row["quantity"], row["cost"]),
        )
    conn.close()


# =========funtion to read data from list of item
def readAllData():
    global options
    global rateDict
    global itemVariable
    global itemRate
    global rateVar
    options = []
    rateDict = {}
    conn = pymysql.connect(host="localhost", user="root", passwd="", db="billservice")
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    query = "select * from itemlist"
    cursor.execute(query)
    data = cursor.fetchall()
    count = 0
    for row in data:
        count += 1
        options.append(row["nameid"])
        rateDict[row["nameid"]] = row["rate"]
        itemVariable.set(options[0])
        itemRate = int(rateDict[options[0]])
    conn.close()
    rateVar.set("%.2f" % itemRate)
    if count == 0:
        remove_all_widgets()
        ItemAddWindow()
    else:
        remove_all_widgets()
        mainwindow()


# ============== admin login function=======
def adminLogin():
    global usernameVar
    global passwordVar

    username = usernameVar.get()
    password = passwordVar.get()

    conn = pymysql.connect(host="localhost", user="root", passwd="", db="billservice")
    cursor = conn.cursor()
    query = "select * from users where username='{}' and password='{}'".format(
        username, password
    )
    cursor.execute(query)
    data = cursor.fetchall()
    admin = False
    for row in data:
        admin = True
    conn.close()
    if admin:
        readAllData()
    else:
        messagebox.showerror("Invalid user", "Credentials entered are invalid")


def optionMenuListener(event):
    global itemVariable
    global rateDict
    global itemRate
    item = itemVariable.get()
    itemRate = int(rateDict[item])
    rateVar.set("%.2f" % itemRate)


def addItemListener():
    remove_all_widgets()
    ItemAddWindow()


def addItem():
    global addItemNameVar
    global addItemRateVar
    global addItemTypeVar
    global addStoredVar
    name = addItemNameVar.get()
    rate = addItemRateVar.get()
    Type = addItemTypeVar.get()
    storeType = addStoredVar.get()
    nameId = name.replace(" ", "_")
    conn = pymysql.connect(host="localhost", user="root", passwd="", db="billservice")
    cursor = conn.cursor()
    query = "insert into itemlist (name,nameid,rate,type,storetype) value('{}','{}','{}','{}','{}')".format(
        name, nameId, rate, Type, storeType
    )
    cursor.execute(query)
    conn.commit()
    conn.close()
    addItemNameVar.set("")
    addItemRateVar.set("")
    addItemTypeVar.set("")


def updateItem():
    global addItemNameVar
    global addItemRateVar
    global addItemTypeVar
    global addStoredVar
    global updateItemId
    name = addItemNameVar.get()
    rate = addItemRateVar.get()
    Type = addItemTypeVar.get()
    storeType = addStoredVar.get()
    conn = pymysql.connect(host="localhost", user="root", passwd="", db="billservice")
    cursor = conn.cursor()
    query = "update  itemlist set name='{}',rate='{}',type='{}',storetype='{}' where nameid='{}'".format(
        name, rate, Type, storeType, updateItemId
    )
    cursor.execute(query)
    conn.commit()
    conn.close()
    addItemNameVar.set("")
    addItemRateVar.set("")
    addItemTypeVar.set("")
    getItemLists()


def loginWindow():
    titleLabel = Label(
        window,
        text="Restaurant Billing System",
        font=("Arial", 30),
        fg="green",
        bg="#f0f0f0",
    )
    titleLabel.grid(row=0, column=0, columnspan=2, pady=10)

    # Load and display image
    img = PhotoImage(file="F:/Restaurant Billing System/images.png")
    imgLabel = Label(window, image=img, bg="#f0f0f0")
    imgLabel.image = img  # Store image reference
    imgLabel.grid(row=1, column=0, columnspan=2, pady=10)

    loginFrame = Frame(window, bg="#f0f0f0")  # Set frame background color
    loginFrame.grid(row=2, column=0, columnspan=2, pady=10)

    loginLabel = Label(loginFrame, text="Admin Login", font=("Arial", 20), bg="#f0f0f0")
    loginLabel.grid(row=0, column=0, columnspan=2, pady=10)

    usernameLabel = Label(loginFrame, text="Username", bg="#f0f0f0")
    usernameLabel.grid(row=1, column=0, padx=20, pady=5)

    passwordLabel = Label(loginFrame, text="Password", bg="#f0f0f0")
    passwordLabel.grid(row=2, column=0, padx=20, pady=5)

    usernameEntry = Entry(loginFrame, textvariable=usernameVar)
    usernameEntry.grid(row=1, column=1, padx=20, pady=5)

    passwordEntry = Entry(loginFrame, textvariable=passwordVar, show="*")
    passwordEntry.grid(row=2, column=1, padx=20, pady=5)

    loginButton = Button(
        loginFrame,
        text="Login",
        width=20,
        height=2,
        bg="#007bff",
        fg="white",
        command=lambda: adminLogin(),
    )
    loginButton.grid(row=3, column=0, columnspan=2, pady=10)


def mainwindow():
    titleLabel = Label(
        window,
        text="Restaurant Billing System",
        font=("Arial", 30),
        fg="green",
        bg="#f0f0f0",
    )
    titleLabel.grid(row=0, column=0, columnspan=5, pady=(10, 20))

    addNewItem = Button(
        window,
        text="Add Item",
        width=15,
        height=2,
        command=lambda: addItemListener(),
        bg="#007bff",
        fg="white",
        font=("Arial", 12, "bold"),
    )
    addNewItem.grid(row=1, column=0, padx=10, pady=10)

    updateItem = Button(
        window,
        text="Update Item",
        width=15,
        height=2,
        bg="#ffc107",
        fg="black",
        font=("Arial", 12, "bold"),
        command=lambda: moveToUpdate(),
    )
    updateItem.grid(row=1, column=1, padx=10, pady=10)

    showallEntry = Button(
        window,
        text="Show Bills",
        width=15,
        height=2,
        bg="#ffc107",
        fg="black",
        font=("Arial", 12, "bold"),
        command=lambda: movetoBills(),
    )
    showallEntry.grid(row=1, column=2, padx=10, pady=10)

    logoutBtn = Button(
        window,
        text="Logout",
        width=15,
        height=2,
        bg="#dc3545",
        fg="white",
        font=("Arial", 12, "bold"),
        command=lambda: LogOut(),
    )
    logoutBtn.grid(row=1, column=4, padx=10, pady=10)

    itemLabel = Label(window, text="Select Item", bg="#f0f0f0", font=("Arial", 12))
    itemLabel.grid(row=2, column=0, padx=5, pady=10, sticky="w")
    itemDropDown = OptionMenu(
        window, itemVariable, *options, command=optionMenuListener
    )
    itemDropDown.config(width=12, font=("Arial", 12))
    itemDropDown.grid(row=2, column=1, padx=10, pady=10, sticky="w")

    rateLabel = Label(window, text="Rate", bg="#f0f0f0", font=("Arial", 12))
    rateLabel.grid(row=2, column=2, padx=10, pady=10, sticky="w")
    rateValue = Label(window, textvariable=rateVar, bg="#f0f0f0", font=("Arial", 12))
    rateValue.grid(row=2, column=3, padx=10, pady=10, sticky="w")

    quantityLabel = Label(window, text="Quantity", bg="#f0f0f0", font=("Arial", 12))
    quantityLabel.grid(row=3, column=0, padx=5, pady=10, sticky="w")
    quantityEntry = Entry(
        window, textvariable=quantityVar, font=("Arial", 12), width=15
    )
    quantityEntry.grid(row=3, column=1, padx=5, pady=10, sticky="w")

    costLabel = Label(window, text="Cost", bg="#f0f0f0", font=("Arial", 12))
    costLabel.grid(row=3, column=2, padx=10, pady=10, sticky="w")
    costEntry = Entry(window, textvariable=costVar, font=("Arial", 12), width=15)
    costEntry.grid(row=3, column=3, padx=10, pady=10, sticky="w")

    buttonBill = Button(
        window,
        text="Add to List",
        width=15,
        command=lambda: generate_bill(),
        bg="#007bff",  # Blue background color
        fg="white",  # White text color
        font=("Arial", 12, "bold"),
        bd=0,  # Border width
        relief="raised",
    )
    buttonBill.grid(row=3, column=4, padx=(5, 0), pady=(10, 0))

    billLabel = Label(window, text="Bills", font="Arial 25")
    billLabel.grid(row=4, column=2, pady=20)

    billsTV.grid(row=5, column=0, columnspan=5, padx=10)

    scrollBar = Scrollbar(window, orient="vertical", command=billsTV.yview)
    scrollBar.grid(row=5, column=4, sticky="NSE")

    billsTV.configure(yscrollcommand=scrollBar.set)

    billsTV.heading("#0", text="Item Name")
    billsTV.heading("#1", text="Rate")
    billsTV.heading("#2", text="Quantity")
    billsTV.heading("#3", text="Cost")

    # Total Cost Label
    totalCostLabel = Label(
        window,
        textvariable=totalCostVar,
        font=("Arial", 16, "bold"),
        bg="#f0f0f0",  # Light gray background color
        fg="green",
    )
    totalCostLabel.grid(row=6, column=1, padx=(10, 0))

    # Generate Bills Button
    generateBill = Button(
        window,
        text="Generate Bills",
        width=15,
        command=lambda: print_bill(),
        bg="#007bff",  # Blue background color
        fg="white",  # White text color
        font=("Arial", 12, "bold"),
        bd=0,  # Border width
        relief="raised",
    )
    generateBill.grid(row=6, column=4)

    updateListView()


def ItemAddWindow():
    backButton = Button(window, text="Back", command=lambda: readAllData())
    backButton.grid(row=0, column=1)
    titleLabel = Label(
        window, text="Add Item", font=("Arial", 30), fg="green", bg="#f0f0f0", width=40
    )
    titleLabel.grid(row=0, column=2, columnspan=4, pady=(10, 0))

    itemNameLabel = Label(window, text="Name", font=("Arial", 12), bg="#f0f0f0")
    itemNameLabel.grid(row=1, column=1, pady=(10, 0))
    itemNameEntry = Entry(window, textvariable=addItemNameVar, font=("Arial", 12))
    itemNameEntry.grid(row=1, column=2, pady=(10, 0))

    itemRateLabel = Label(window, text="Rate", font=("Arial", 12), bg="#f0f0f0")
    itemRateLabel.grid(row=1, column=3, pady=(10, 0))
    itemRateEntry = Entry(window, textvariable=addItemRateVar, font=("Arial", 12))
    itemRateEntry.grid(row=1, column=4, pady=(10, 0))

    itemTypeLabel = Label(window, text="Type", font=("Arial", 12), bg="#f0f0f0")
    itemTypeLabel.grid(row=2, column=1, pady=(10, 0))
    itemTypeEntry = Entry(window, textvariable=addItemTypeVar, font=("Arial", 12))
    itemTypeEntry.grid(row=2, column=2, pady=(10, 0))

    storeTypeLabel = Label(window, text="Stored Type", font=("Arial", 12), bg="#f0f0f0")
    storeTypeLabel.grid(row=2, column=3, pady=(10, 0))
    storeEntry = OptionMenu(window, addStoredVar, *storeOptions)
    storeEntry.grid(row=2, column=4, pady=(10, 0))

    AddItemButton = Button(
        window,
        text="Add Item",
        width=20,
        height=2,
        bg="#007bff",
        fg="white",
        font=("Arial", 12, "bold"),
        command=lambda: addItem(),
    )
    AddItemButton.grid(row=3, column=3, pady=(12, 0), columnspan=1)


def updateItemWindow():
    backButton = Button(window, text="Back", command=lambda: readAllData())
    backButton.grid(row=0, column=1)
    titleLabel = Label(
        window,
        text="Update Item",
        font=("Arial", 30),
        fg="green",
        bg="#f0f0f0",
        width=40,
    )
    titleLabel.grid(row=0, column=2, columnspan=4, pady=(10, 0))

    itemNameLabel = Label(window, text="Name", font=("Arial", 12), bg="#f0f0f0")
    itemNameLabel.grid(row=1, column=1, pady=(10, 0))
    itemNameEntry = Entry(window, textvariable=addItemNameVar, font=("Arial", 12))
    itemNameEntry.grid(row=1, column=2, pady=(10, 0))

    itemRateLabel = Label(window, text="Rate", font=("Arial", 12), bg="#f0f0f0")
    itemRateLabel.grid(row=1, column=3, pady=(10, 0))
    itemRateEntry = Entry(window, textvariable=addItemRateVar, font=("Arial", 12))
    itemRateEntry.grid(row=1, column=4, pady=(10, 0))

    itemTypeLabel = Label(window, text="Type", font=("Arial", 12), bg="#f0f0f0")
    itemTypeLabel.grid(row=2, column=1, pady=(10, 0))
    itemTypeEntry = Entry(window, textvariable=addItemTypeVar, font=("Arial", 12))
    itemTypeEntry.grid(row=2, column=2, pady=(10, 0))

    storeTypeLabel = Label(window, text="Stored Type", font=("Arial", 12), bg="#f0f0f0")
    storeTypeLabel.grid(row=2, column=3, pady=(10, 0))
    storeEntry = OptionMenu(window, addStoredVar, *storeOptions)
    storeEntry.grid(row=2, column=4, pady=(10, 0))

    AddItemButton = Button(
        window,
        text="Update Item",
        width=20,
        height=2,
        bg="#007bff",
        fg="white",
        font=("Arial", 12, "bold"),
        command=lambda: updateItem(),
    )
    AddItemButton.grid(row=3, column=3, pady=(12, 0), columnspan=1)

    updateTV.grid(row=4, column=0, columnspan=5)
    scrollBar = Scrollbar(window, orient="vertical", command=billsTV.yview)
    scrollBar.grid(row=4, column=4, sticky="NSE")

    updateTV.configure(yscrollcommand=scrollBar.set)

    updateTV.heading("#0", text="Item ID")
    updateTV.column("#0", minwidth=0, width=150)
    updateTV.heading("#1", text="Item Name")
    updateTV.column("#1", minwidth=0, width=170)
    updateTV.heading("#2", text="Rate")
    updateTV.column("#2", minwidth=0, width=150)
    updateTV.heading("#3", text="Type")
    updateTV.column("#3", minwidth=0, width=150)
    updateTV.heading("#4", text="Store Type")
    updateTV.column("#4", minwidth=0, width=150)

    getItemLists()


def viewAllBills():
    backButton = Button(window, text="Back", command=lambda: readAllData())
    backButton.grid(row=0, column=1)
    titleLabel = Label(
        window,
        text="Billing History",
        font=("Arial", 30),
        fg="green",
        bg="#f0f0f0",
        width=40,
    )
    titleLabel.grid(row=0, column=2, columnspan=4, pady=(10, 0))
    billsTV.grid(row=1, column=0, columnspan=5, padx=10)

    scrollBar = Scrollbar(window, orient="vertical", command=billsTV.yview)
    scrollBar.grid(row=1, column=4, sticky="NSE")

    billsTV.configure(yscrollcommand=scrollBar.set)

    billsTV.heading("#0", text="Item Name")
    billsTV.heading("#1", text="Rate")
    billsTV.heading("#2", text="Quantity")
    billsTV.heading("#3", text="Cost")

    updateBillsData()


loginWindow()
window.mainloop()

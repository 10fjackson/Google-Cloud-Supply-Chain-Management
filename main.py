import mysql.connector
import re
import configparser
def connect_to_database():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            port='3306',
            user='root',
            password='change-me',
            database='FSE_ENGSTORE',
        )
        return conn
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def create_student_record(conn, name, age):
    try:
        cursor = conn.cursor()
        query = "INSERT INTO Students (name, age) VALUES (%s, %s)"
        cursor.execute(query, (name,age))
        conn.commit()
        print("Student record created successfully")
    except mysql.connector.Error as e:
        print(f"Error creating a record: {e}")

def select_and_display_students(conn):
    try:
        cursor = conn.cursor()
        query = "SELECT * FROM Students"
        cursor.execute(query)
        for(student_id, name, age) in cursor:
            print(f"ID: {student_id}, Name: {name}, Age: {age}")
    except mysql.connector.Error as e:
        print(f"Error fetching records: {e}")


def prompt_user(conn):

    print("Choose the number of the option you wish to complete:")
    print("1. List all products that are out of stock")
    print("2. Find the total number of orders placed by each customer")
    print("3. Display the details of the most expensive product ordered in each order")
    print("4. Retrieve a list of products that have never been ordered")
    print("5. Show the total revenue generated by each supplier")
    print("6. Add a new Order")
    print("7. Update the stock quantity of a product after an order is placed")
    num = input()
    if num == '1' or num == '2' or num == '3' or num == '4' or num == '5' or num == '6' or num == '7':
        print("one moment while I handle your request")

        if num == '1':
            list_OOS_products(conn)

        if num == '2':
            total_orders_per_customer(conn)

        if num == '3':
            expensive_product(conn)

        if num == '4':
            never_ordered(conn)

        if num == '5':
            revenue_total(conn)

        if num == '6':
            new_order_procedure(conn)

        if num == '7':
            update_stock_quantity_procedure(conn)

    else:
        print("!!!SORRY, please enter a number 1-5!!!")
        prompt_user()
    print("")
    prompt_user(conn)



def list_OOS_products(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Products WHERE UnitsInStock = 0")
    rows = cursor.fetchall()
    print(len(rows))
    for row in rows:
        print(row)
    conn.commit()

def total_orders_per_customer(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT Customers.CustomerName, COUNT(Orders.OrderID) as TotalOrders "
                   "FROM Customers "
                   "JOIN Orders ON Customers.CustomerID = Orders.CustomerID "
                   "GROUP BY Customers.CustomerID;")
    rows = cursor.fetchall()
    print(len(rows))
    for row in rows:
        print(row)
    conn.commit()

def expensive_product(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT o.OrderID, p.ProductID, p.ProductName, od.UnitPrice, od.Quantity FROM Orders o"
                   " JOIN OrderDetails od ON o.OrderID = od.OrderID"
                   " JOIN Products p ON od.ProductID = p.ProductID"
                   " WHERE (o.OrderID, od.UnitPrice) IN ("
                   "SELECT OrderID, MAX(UnitPrice)"
                   " FROM OrderDetails"
                   " GROUP BY OrderID)"
                   " ORDER BY o.OrderID;")
    rows = cursor.fetchall()
    print(len(rows))
    for row in rows:
        print(row)
    conn.commit()

def never_ordered(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Products "
                   "LEFT JOIN OrderDetails ON Products.ProductID = OrderDetails.ProductID "
                   "WHERE OrderDetails.ProductID IS NULL;")
    rows = cursor.fetchall()
    print(len(rows))
    for row in rows:
        print(row)
    conn.commit()

def revenue_total(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT Suppliers.SupplierName, SUM(OrderDetails.Quantity * OrderDetails.UnitPrice) AS TotalRevenue"
                   " FROM Suppliers "
                   "JOIN Products ON Suppliers.SupplierID = Products.SupplierID "
                   "JOIN OrderDetails ON Products.ProductID = OrderDetails.ProductID "
                   "GROUP BY Suppliers.SupplierName;")
    rows = cursor.fetchall()
    print(len(rows))
    for row in rows:
        print(row)
    conn.commit()

def prompt_user_for_input(prompt_message, pattern):
    while True:
        user_input = input(prompt_message)
        if re.match(pattern, user_input):
            return user_input
        else:
            print("Invalid input, please try again.")

def new_order_procedure(conn):
    try:
        # Establish cursor to the server connection
        cursor = conn.cursor()

        # Prompt for each attribute and convert types as necessary
        p_CustomerID = int(prompt_user_for_input("Enter Customer ID (integer): ", r"^\d+$"))
        p_OrderDate = prompt_user_for_input("Enter Order Date (YYYY-MM-DD): ", r"^\d{4}-\d{2}-\d{2}$")
        p_ShipDate = prompt_user_for_input("Enter Ship Date (YYYY-MM-DD): ", r"^\d{4}-\d{2}-\d{2}$")
        p_ShipAddress = prompt_user_for_input("Enter Ship Address: ", r"^.+$")
        p_ShipCity = prompt_user_for_input("Enter Ship City: ", r"^.+$")
        p_ShipPostalCode = prompt_user_for_input("Enter Ship Postal Code: ", r"^.+$")
        p_ShipCountry = prompt_user_for_input("Enter Ship Country: ", r"^.+$")
        p_ProductID = int(prompt_user_for_input("Enter Product ID (integer): ", r"^\d+$"))
        p_Quantity = int(prompt_user_for_input("Enter Quantity (integer): ", r"^\d+$"))
        p_UnitPrice = float(prompt_user_for_input("Enter Unit Price (decimal): ", r"^\d+(\.\d{1,2})?$"))

        # Call the stored procedure
        query = "CALL new_order(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (p_CustomerID, p_OrderDate, p_ShipDate, p_ShipAddress, p_ShipCity, p_ShipPostalCode, p_ShipCountry, p_ProductID, p_Quantity, p_UnitPrice))

        conn.commit()
        print("Order created successfully. ")

    except mysql.connector.Error as e:
        print(f"Error calling stored procedure: {e}")


# Calls Procedure.
def update_stock_quantity_procedure(conn):
    try:
        # Establish cursor to the server connection
        cursor = conn.cursor()
        p_ProductID = int(prompt_user_for_input("Enter Product ID (integer): ", r"^\d+$"))
        p_UnitsInStock = int(prompt_user_for_input("Enter Units in Stock (integer): ", r"^\d+$"))

        # Call the stored procedure
        query = "CALL update_units_in_stock(%s, %s)"
        cursor.execute(query, (p_ProductID, p_UnitsInStock))
        conn.commit()
        print("Product units in stock updated successfully. ")
    except mysql.connector.Error as e:
        print(f"Error updating product units in stock: {e}")






def main():
    conn = connect_to_database()
    if conn:
        prompt_user(conn)
        #create_student_record(conn, 'John Doe', 20)
        #select_and_display_students(conn)
        conn.close()
    else:
        print("Cant connect to database")

if __name__ == "__main__":
   main()

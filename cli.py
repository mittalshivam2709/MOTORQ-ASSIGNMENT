import pymysql
import pymysql.cursors


db_config = {
    "host": "localhost",
    "user": "root",
    "db": "CBA",
}

connection = pymysql.connect(**db_config)
cursor = connection.cursor()

def create_tables():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS CONFERENCE (
            Name VARCHAR(255) PRIMARY KEY,
            Location VARCHAR(255),
            Topics VARCHAR(255),
            Start TIMESTAMP,
            End TIMESTAMP,
            AvailableSlots INT,
            CHECK (Name REGEXP '^[A-Za-z0-9 ]*$'),
            CHECK (Location REGEXP '^[A-Za-z0-9 ]*$'),
            CHECK (Topics REGEXP '^[A-Za-z0-9, ]*$' AND LENGTH(Topics) - LENGTH(REPLACE(Topics, ',', '')) < 10),
            CHECK (Start < End),
            CHECK (TIMESTAMPDIFF(HOUR, Start, End) <= 12),
            CHECK (AvailableSlots > 0)
    );  

    """)
    # cursor.execute("""INSERT INTO CONFERENCE (Name, Location, Topics, Start, End, AvailableSlots) 
    # VALUES 
    #     ('Tech Summit 2024', 'New York City', 'AI,Blockchain,Quantum Computing,Space Exploration', '2024-08-03 09:00:00', '2024-08-03 17:00:00', 100),
    #     ('Innovation Expo', 'San Francisco', 'Robotics,AI,IoT,Cloud Computing', '2024-08-05 10:00:00', '2024-08-05 15:00:00', 200),
    #     ('Healthcare Conference', 'Los Angeles', 'Medical Devices,Telemedicine,Pharmaceuticals', '2024-08-10 08:00:00', '2024-08-10 20:00:00', 150),
    #     ('Startup Pitch Day', 'Boston', 'Startups,Investment,Entrepreneurship', '2024-08-12 11:00:00', '2024-08-12 13:00:00', 50);

    # """)

    cursor.execute("""CREATE TABLE IF NOT EXISTS USER (
        UserID VARCHAR(255) PRIMARY KEY,
        InterestedTopics VARCHAR(1000),
        CHECK (UserID REGEXP '^[A-Za-z0-9]*$'),
        CHECK (InterestedTopics REGEXP '^[A-Za-z0-9, ]*$' AND LENGTH(InterestedTopics) - LENGTH(REPLACE(InterestedTopics, ',', '')) < 50)
        );
    """)
    cursor.execute("""CREATE TABLE IF NOT EXISTS BOOKING (
                id INT AUTO_INCREMENT PRIMARY KEY,
                Name VARCHAR(255),
                UserID VARCHAR(255),
                Status ENUM('Confirmed', 'Waiting', 'Cancelled') DEFAULT 'Waiting',
                FOREIGN KEY (Name) REFERENCES CONFERENCE(Name),
                FOREIGN KEY (UserID) REFERENCES USER(UserID)
            );
        """)
    connection.commit()

create_tables()

def add_conference():
    name = input("Enter name of conference")
    location = input("Enter location of conference")
    topics = input("Enter topics of conference")
    start = input("Enter start date of conference")
    end = input("Enter end date of conference")
    slots = input("Enter number of available    slots")
    query = "SELECT * FROM CONFERENCE WHERE Name = %s"
    cursor.execute(query, (name,))
    result = cursor.fetchone()
    if not result:
        cursor.execute("INSERT INTO CONFERENCE (Name, Location, Topics, Start, End, AvailableSlots) VALUES (%s, %s, %s, %s, %s, %s)", (name, location, topics, start, end, slots))
        connection.commit()
        print("Conference added")
    else:
        print("Conference already exists")

def add_user():
    user_id = input("Enter user id")
    topics = input("Enter topics of interest")
    query = "SELECT * FROM USER WHERE UserID = %s"
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    if not result:
        cursor.execute("INSERT INTO USER (UserID, InterestedTopics) VALUES (%s, %s)", (user_id, topics))
        connection.commit()
        print("User added")
    else:
        print("User already exists")

def book_conference():
    conference=input("Enter Conference Name")
    user=input("Enter User ID")
    query = "SELECT * FROM CONFERENCE WHERE Name = %s"
    cursor.execute(query, (conference,))
    result = cursor.fetchone()
    if not result:
        print("Conference does not exist")
        return
    query = "SELECT * FROM USER WHERE UserID = %s"
    cursor.execute(query, (user,))
    result = cursor.fetchone()
    if not result:
        print("User does not exist")
        return
    query="SELECT * FROM BOOKING WHERE UserID = %s AND Name = %s AND Status = 'Confirmed'"
    cursor.execute(query, (user,))
    result = cursor.fetchone()
    if result:
        print("User already has a booking with booking id: ", result[0])
        return
    query="SELECT AvailableSlots FROM CONFERENCE WHERE Name = %s"
    cursor.execute(query, (conference,))
    result = cursor.fetchone()
    if result[0] == 0:
        query="INSERT INTO BOOKING (Name, UserID, Status) VALUES (%s, %s, 'Waiting')"
        cursor.execute(query, (conference, user))
        connection.commit()
        query="Select id from BOOKING WHERE Name = %s AND UserID = %s"
        print("Conference is full, added to waiting list with id: ", result[0])
        return
    
    connection.begin()
    try:
        query="UPDATE CONFERENCE SET AvailableSlots = AvailableSlots - 1 WHERE Name = %s"
        cursor.execute(query, (conference,))

        query="INSERT INTO BOOKING (Name, UserID, Status) VALUES (%s, %s, 'Confirmed')"
        cursor.execute(query, (conference, user))
        query="Select id from BOOKING WHERE Name = %s AND UserID = %s"
        cursor.execute(query, (conference, user))
        result = cursor.fetchone()
        connection.commit()
        print("Booking Confirmed, with id: ", result[0])
    except:
        connection.rollback()
        print("Error occurred, booking not confirmed")

def track_booking():
    trackingid=input("Enter Booking ID")
    query="SELECT * FROM BOOKING WHERE id = %s"
    cursor.execute(query, (trackingid,))
    result = cursor.fetchone()
    if not result:
        print("Booking does not exist")
        return
    print("Booking ID: ", result[0])
    print("Conference Name: ", result[1])
    print("User ID: ", result[2])
    print("Status: ", result[3])
    if result[3] == 'Waiting':
        query="SELECT AvailableSlots FROM CONFERENCE WHERE Name = %s"
        cursor.execute(query, (result[1],))
        result = cursor.fetchone()
        print("Do you want to cancel your booking?")
        ch=input("Enter Y/N")
        if ch == 'Y':
            query="UPDATE BOOKING SET Status = 'Cancelled' WHERE id = %s"
            cursor.execute(query, (trackingid,))
            connection.commit()
            print("Booking Cancelled")
            return
        else:
            print("Booking not cancelled")
        if result[0] == 0:
            print("Conference is full, you are on waiting list")
        else:
            print("Do you want to confirm your booking?")
            ch=input("Enter Y/N")
            if ch == 'Y':
                query="UPDATE CONFERENCE SET AvailableSlots = AvailableSlots - 1 WHERE Name = %s"
                cursor.execute(query, (result[1],))
                connection.commit()
                query="UPDATE BOOKING SET Status = 'Confirmed' WHERE id = %s"
                cursor.execute(query, (trackingid,))
                connection.commit()
                print("Booking Confirmed")
                return
            else:
                print("Booking not confirmed")
    if result[3] == 'Confirmed':
        print("Do you want to cancel your booking?")
        ch=input("Enter Y/N")
        if ch == 'Y':
            query="UPDATE CONFERENCE SET AvailableSlots = AvailableSlots + 1 WHERE Name = %s"
            cursor.execute(query, (result[1],))
            connection.commit()
            query="UPDATE BOOKING SET Status = 'Cancelled' WHERE id = %s"
            cursor.execute(query, (trackingid,))
            connection.commit()
            print("Booking Cancelled")
        else:
            print("Booking not cancelled")

while(1):
    print("Select the type of query you want to perform")
    print("1. Add Conference")
    print("2. Add User")
    print("3. Book a Conference")
    print("4. Track Booking")

    ch = int(input("Enter choice> "))
    if(ch==1):
        add_conference()
    if (ch==2):
        add_user()
    if(ch==3):
        book_conference()
    if(ch==4):
        track_booking()

cursor.close()
connection.close()

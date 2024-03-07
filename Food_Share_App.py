# importing sqlite database module
import sqlite3

# Creating Class for user authentication and listings
class User:
    # Database paths and connections
    def __init__(self, db_path="users.db", listings_db_path="listings.db"):
        self.db_path = db_path
        self.listings_db_path = listings_db_path
        self.conn = sqlite3.connect(db_path)
        self.listings_conn = sqlite3.connect(listings_db_path)
        self.new_table()
        self.new_listings_table()
        self.logged_in = False
        self.logged_in_username = None

    # Creating 'users' table if it doesn't exist
    def new_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL
                )
            ''')

    # Registering new user in the 'users' table
    def register_user(self, username, password):
        with self.conn:
            try:
                self.conn.execute('''
                    INSERT INTO users (username, password) VALUES (?, ?)
                ''', (username, password))
                print("New user registration successful!")
                return True
            except sqlite3.IntegrityError:
                print("Username already exists. Please choose another username.")
                return False 


    # Authentication of the user 
    def login_user(self, username, password):
        with self.conn:
            cursor = self.conn.execute('''
                SELECT id FROM users WHERE username = ? AND password = ?
            ''', (username, password))
            result = cursor.fetchone()
            if result:
                print("Login successful.")
                self.logged_in_username = username
                return result[0]
            else:
                print("Wrong username or password.")
                return None


    # Creating new 'listings' table if it doesn't exist
    def new_listings_table(self):
        with self.listings_conn:
            self.listings_conn.execute('''
                CREATE TABLE IF NOT EXISTS listings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    area TEXT NOT NULL,
                    food TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    contact TEXT NOT NULL
                )
            ''')

    # Adding new listing to the 'listings' table
    def add_listing(self, area, food, quantity, contact):
        with self.listings_conn:
            self.listings_conn.execute('''
                INSERT INTO listings (username, area, food, quantity, contact) VALUES (?, ?, ?, ?, ?)
            ''', (self.logged_in_username, area, food, quantity, contact))
            print("New listing added successfully!")

     # Viewing the listings of the user that is logged in
    def view_my_listings(self):
        with self.listings_conn:
            cursor = self.listings_conn.execute('''
                SELECT * FROM listings WHERE username = ?
            ''', (self.logged_in_username,))
            result = cursor.fetchall()
            for row in result:
                print(f"ID: {row[0]}, Area: {row[2]}, Food: {row[3]}, Quantity: {row[4]}, Contact: {row[5]}")
            if result:
                delete_option = input("Enter ID of listing to delete or Enter to return to menu: ")
                if delete_option:
                    self.delete_listing(int(delete_option))


     # Viewing all the listings, can be searched by area
    def view_all_listings(self):
        with self.listings_conn:
            search_area = input("Enter area to search: ")

            if search_area:
                search = f"%{search_area}%" 
                cursor = self.listings_conn.execute('''
                    SELECT * FROM listings WHERE area LIKE ?
                ''', (search,))
            else:
                cursor = self.listings_conn.execute('''
                    SELECT * FROM listings
                ''')

            result = cursor.fetchall()
            
            if not result:
                print("No listings found.")
            else:
                for row in result:
                    print(f"ID: {row[0]}, Area: {row[2]}, Food: {row[3]}, Quantity: {row[4]}, Contact: {row[5]}")



    # Deleting a listing 
    def delete_listing(self, listing_id):
        with self.listings_conn:
            cursor = self.listings_conn.execute('''
                SELECT id FROM listings WHERE id = ? AND username = ?
            ''', (listing_id, self.logged_in_username))
            result = cursor.fetchone()

            if result:
                self.listings_conn.execute('''
                    DELETE FROM listings WHERE id = ?
                ''', (listing_id,))
                print("Listing deleted successfully!")
            else:
                print("Wrong listing.")

    # Closing the database
    def close_connection(self):
        self.conn.close()

def main():
    user_auth = User()

    # Main menu loop
    while True:
        if not user_auth.logged_in:
            print("Welcome to the Food Sharing App!")
            menu = input("Press 1 to register a new user,  2 to login or 3 to exit: ")

            # Option 1 for adding a new user
            if menu == "1":
                while True:
                    username = input("Enter a new username: ")
                    password = input("Enter a new password: ")
                    registration_success = user_auth.register_user(username, password)

                    if registration_success:
                        user_auth.logged_in_username = username
                        user_auth.logged_in = True
                        break

            # Loging in users that are already registered
            elif menu == "2":
                username = input("Enter your username: ")
                password = input("Enter your password: ")

                user_id = user_auth.login_user(username, password)

                # Logged in menu
                if user_id is not None:
                    while True:
                        print("1. Add new listing")
                        print("2. View my listings")
                        print("3. View all listings")
                        print("4. Exit")

                        logged_in = input("Enter your choice: ")

                        # Adding a new listing
                        if logged_in == "1":
                            area = input("Enter your area: ")
                            food = input("Enter your food: ")
                            qnt = input("Enter food quantity / portions: ")
                            contact = input("Enter your contact information: ")
                            user_auth.add_listing(area, food, qnt, contact)

                        # Viewing logged in user's listings
                        elif logged_in == "2":
                            print("My listings")
                            user_auth.view_my_listings()

                        # Viewing all the listings
                        elif logged_in == "3":
                            user_auth.view_all_listings()

                        # Exiting menu
                        elif logged_in == "4":
                            user_auth.close_connection()
                            print("Bye!")
                            return  

                        else:
                            print("Wrong choice.")

            # Exiting loop
            elif menu == "3":
                break

        # Logged in user options
        else:
            print(f"Logged in as {user_auth.logged_in_username}.")
            print("1. Add new listing")
            print("2. View my listings")
            print("3. View all listings")
            print("4. Exit")

            logged_in = input("Enter your choice: ")

            if logged_in == "1":
                area = input("Enter your area: ")
                food = input("Enter your food: ")
                qnt = input("Enter food quantity / portions: ")
                contact = input("Enter your contact information: ")
                user_auth.add_listing(area, food, qnt, contact)

            elif logged_in == "2":
                print("My listings")
                user_auth.view_my_listings()

            elif logged_in == "3":
                user_auth.view_all_listings()

            elif logged_in == "4":
                user_auth.close_connection()
                print("Bye!")
                return  

            else:
                print("Wrong choice.")


if __name__ == "__main__":
    main()
from mysql.connector import connect
import pandas

TABLES = {}
TABEL_NAMES=['books','users','ratings','borrow']
TABLES['books'] = (
    "create table `books` ("
    "   `b_id` int,"
    "   `b_title` varchar(50) not null,"
    "   `b_author` varchar(30) not null,"
    "   primary key(`b_id`)"
    ")"
)
TABLES['users'] = (
    "create table `users` ("
    "   `u_id` int,"
    "   `u_name` varchar(30) not null,"
    "   primary key(`u_id`)"
    ")"
)
TABLES['ratings'] = (
    "create table `ratings` ("
    "   `b_id` int,"
    "   `u_id` int,"
    "   `b_u_rating` int not null,"
    "   primary key(`b_id`,`u_id`),"
    "   foreign key(`b_id`) references `books`(`b_id`),"
    "   foreign key(`u_id`) references `users`(`u_id`),"
    "   check(`b_u_rating` in (1,2,3,4,5))"
    ")"
)
TABLES['borrow'] = (
    "create table `borrow` ("
    "   `b_id` int,"
    "   `u_id` int,"
    "   primary key(`b_id`,`u_id`),"
    "   foreign key(`b_id`) references `books`(`b_id`),"
    "   foreign key(`u_id`) references `users`(`u_id`)"
    ")"
)

def initialize_database():
    # YOUR CODE GOES HERE
    # print msg
    csvFile = pandas.read_csv('data.csv',encoding='latin1')
    for table in TABEL_NAMES:
        try:
            cursor.execute(TABLES[table])
        except:
            cursor.execute(f"delete from {table}")
    connection.commit()

    row_list = csvFile.values.tolist()
    for row in row_list:
        b_id, b_title, b_author, u_id, u_name, b_u_rating = row
        cursor.execute(f"insert ignore into books values ({b_id}, '{b_title}', '{b_author}')")
        cursor.execute(f"insert ignore into users values ({u_id}, '{u_name}')")
        cursor.execute(f"insert ignore into ratings values ({b_id}, {u_id}, {b_u_rating})")
    connection.commit()

    print('Database successfully initialized')
    pass

def reset():
    # YOUR CODE GOES HERE
    pass

def print_books():
    # YOUR CODE GOES HERE
    # print msg
    cursor.execute("select * from books")
    print(cursor.fetchall())

def print_users():
    # YOUR CODE GOES HERE
    # print msg
    cursor.execute("select * from users")
    print(cursor.fetchall())

def insert_book():
    title = input('Book title: ')
    author = input('Book author: ')
    # YOUR CODE GOES HERE
    # print msg
    cursor.execute("select max(b_id) as max from books")
    x = cursor.fetchall()[0]['max']
    cursor.execute(f"insert into books values ({x+1},'{title}','{author}')")

def remove_book():
    book_id = input('Book ID: ')
    # YOUR CODE GOES HERE
    # print msg
    pass

def insert_user():
    name = input('User name: ')
    # YOUR CODE GOES HERE
    # print msg
    pass

def remove_user():
    user_id = input('User ID: ')
    # YOUR CODE GOES HERE
    # print msg
    pass

def checkout_book():
    book_id = input('Book ID: ')
    user_id = input('User ID: ')
    # YOUR CODE GOES HERE
    # print msg
    pass

def return_and_rate_book():
    book_id = input('book ID: ')
    user_id = input('User ID: ')
    rating = input('Ratings (1~5): ')
    # YOUR CODE GOES HERE
    # print msg
    pass

def print_users_for_book():
    user_id = input('User ID: ')
    # YOUR CODE GOES HERE
    # print msg
    pass

def print_borrowing_status_for_user():
    user_id = input('User ID: ')
    # YOUR CODE GOES HERE
    # print msg
    pass

def search_books():
    query = input('Query: ')
    # YOUR CODE GOES HERE
    # print msg

def recommend_popularity():
    # YOUR CODE GOES HERE
    user_id = input('User ID: ')
    # YOUR CODE GOES HERE
    # print msg
    pass

def recommend_item_based():
    user_id = input('User ID: ')
    # YOUR CODE GOES HERE
    # print msg
    pass


def main():
    global connection 
    connection = connect(
        host = 'astronaut.snu.ac.kr',
        port = 7001,
        user = 'DB2023_16728',
        password = 'DB2023_16728',
        db = 'DB2023_16728',
        charset = 'utf8'
    )   
    global cursor
    with connection.cursor(dictionary=True) as cursor:
        cursor.execute("show tables")
        result = cursor.fetchall()
        print(result)

        while True:
            print('============================================================')
            print('1. initialize database')
            print('2. print all books')
            print('3. print all users')
            print('4. insert a new book')
            print('5. remove a book')
            print('6. insert a new user')
            print('7. remove a user')
            print('8. check out a book')
            print('9. return and rate a book')
            print('10. print borrowing status of a user')
            print('11. search books')
            print('12. recommend a book for a user using popularity-based method')
            print('13. recommend a book for a user using user-based collaborative filtering')
            print('14. exit')
            print('15. reset database')
            print('============================================================')
            menu = int(input('Select your action: '))

            if menu == 1:
                initialize_database()
            elif menu == 2:
                print_books()
            elif menu == 3:
                print_users()
            elif menu == 4:
                insert_book()
            elif menu == 5:
                remove_book()
            elif menu == 6:
                insert_user()
            elif menu == 7:
                remove_user()
            elif menu == 8:
                checkout_book()
            elif menu == 9:
                return_and_rate_book()
            elif menu == 10:
                print_borrowing_status_for_user()
            elif menu == 11:
                search_books()
            elif menu == 12:
                recommend_popularity()
            elif menu == 13:
                recommend_item_based()
            elif menu == 14:
                print('Bye!')
                break
            elif menu == 15:
                reset()
            else:
                print('Invalid action')
        
        connection.close()


if __name__ == "__main__":
    main()

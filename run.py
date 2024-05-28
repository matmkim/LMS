from mysql.connector import connect
import pandas

# TABLE INFORMATION
TABLES = {}
TABEL_NAMES=['books','users','ratings','borrow']
TABLES['books'] = (
    "create table `books` ("
    "   `b_id` int auto_increment,"
    "   `b_title` varchar(50) not null,"
    "   `b_author` varchar(30) not null,"
    "   primary key(`b_id`)"
    ")"
)
TABLES['users'] = (
    "create table `users` ("
    "   `u_id` int auto_increment,"
    "   `u_name` varchar(10) not null,"
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
    try:
        for table in TABEL_NAMES:
                cursor.execute(TABLES[table])
    except:
        for table in reversed(TABEL_NAMES):
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


def reset():
    # YOUR CODE GOES HERE
    pass

#데이터베이스에 존재하는 모든 도서의 정보를 출력한다.
#- 각 column은 도서 ID, 도서명, 저자명, 평균 평점, 대출가능 권 수 순으로 출력한다.
#- [참고1-평균평점규칙]
#도서의 평균 평점은 해당 도서에 남겨진 평점들의 산술평균이다.
#한 회원이 같은 도서에 평점을 여러 번 남기는 경우에는, 가장 최근의 평점 1건만 계산에 반영된다.
#도서에 대한 평점이 존재하지 않는다면 'None' 을 출력한다.
#- 각 row는 도서 ID를 기준으로 오름차순으로 출력한다

def print_books():
    print("-------------------------------------------------------------------------------------------------------------------")
    print(f'{"id".ljust(8)}{"title".ljust(50)}{"author".ljust(30)}{"avg.rating".ljust(16)}{"quantity".ljust(10)}')
    print("-------------------------------------------------------------------------------------------------------------------")
    cursor.execute("select books.b_id as id, books.b_title as title, books.b_author as author, avg(b_u_rating) as avg_rating, 1-count(borrow.u_id) as quantity "
                   "from books left join borrow on books.b_id = borrow.b_id left join ratings on books.b_id = ratings.b_id "
                   "group by books.b_id order by books.b_id")
    books = cursor.fetchall()
    for book in books:
        print(f"{str(book['id']).ljust(8)}{book['title'].ljust(50)}{book['author'].ljust(30)}{str(round(book['avg_rating'],1)).ljust(16)}{str(book['quantity']).ljust(10)}")
    print("-------------------------------------------------------------------------------------------------------------------")
    
def print_users():
    print("--------------------------------------------------------------------------------")
    print(f'{"id".ljust(8)}{"name".ljust(16)}')
    print("--------------------------------------------------------------------------------")
    cursor.execute("select * from users order by u_id")
    users = cursor.fetchall()
    for user in users:
        print(f"{str(user['u_id']).ljust(8)}{user['u_name'].ljust(16)}")
    print("--------------------------------------------------------------------------------")

def insert_book():
    title = input('Book title: ')
    author = input('Book author: ')

    if not 1<=len(title)<=50:
        print("Title length should range from 1 to 50 characters")
        return
    
    if not 1<=len(author)<=30:
        print("Author length should range from 1 to 30 characters")
        return 
    
    cursor.execute(f"select * from books where b_title = '{title}' and b_author = '{author}'")
    book = cursor.fetchall()
    if book:
        print(f"Book ({title}, {author}) already exists")
        return
    
    cursor.execute(f"insert into books(b_title, b_author) values ('{title}','{author}')")
    connection.commit()

def remove_book():
    book_id = input('Book ID: ')
    # YOUR CODE GOES HERE
    # print msg
    cursor.execute(f"delete from books where b_id = {book_id}")
    connection.commit()

def insert_user():
    name = input('User name: ')
    # YOUR CODE GOES HERE
    # print msg
    cursor.execute("select max(u_id) as max from users")
    x = cursor.fetchall()[0]['max']
    cursor.execute(f"insert into users values ({x+1},'{name}')")

def remove_user():
    user_id = input('User ID: ')
    # YOUR CODE GOES HERE
    # print msg
    cursor.execute(f"delete from users where u_id = {user_id}")
    connection.commit()

def checkout_book():
    book_id = input('Book ID: ')
    user_id = input('User ID: ')
    # YOUR CODE GOES HERE
    # print msg
    cursor.execute(f"insert into borrow values ({book_id},{user_id})")

def return_and_rate_book():
    book_id = input('book ID: ')
    user_id = input('User ID: ')
    rating = input('Ratings (1~5): ')
    # YOUR CODE GOES HERE
    # print msg
    cursor.execute(f"delete from borrow where b_id = {book_id} and u_id = {user_id}")
    cursor.execute(f"insert into ratings values ({book_id},{user_id},{rating})")
    connection.commit()

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

def drop():
    for table in reversed(TABEL_NAMES):
        cursor.execute(f"drop table {table}")

def master():
    query = input()
    cursor.execute(query)
    print(cursor.fetchall())


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
            elif menu == 16:
                master()
            else:
                drop()
                print('Invalid action')
        
        connection.close()


if __name__ == "__main__":
    main()

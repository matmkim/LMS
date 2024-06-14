from mysql.connector import connect
import pandas as pd

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
    "   foreign key(`b_id`) references `books`(`b_id`) on delete cascade,"
    "   foreign key(`u_id`) references `users`(`u_id`) on delete cascade,"
    "   check(`b_u_rating` in (1,2,3,4,5))"
    ")"
)
TABLES['borrow'] = (
    "create table `borrow` ("
    "   `b_id` int,"
    "   `u_id` int,"
    "   primary key(`b_id`,`u_id`),"
    "   foreign key(`b_id`) references `books`(`b_id`) on delete cascade,"
    "   foreign key(`u_id`) references `users`(`u_id`) on delete cascade"
    ")"
)

# select query executor
def executor(query):
    cursor.execute(query)
    return cursor.fetchall()

def initialize_database():
    csvFile = pd.read_csv('data.csv',encoding='utf-8')  # upload csv data

    for table in TABEL_NAMES:
        try:
            cursor.execute(TABLES[table])
        except: # 해당 table이 이미 존재
            cursor.execute(f"delete from {table}")

    row_list = csvFile.values.tolist()
    for row in row_list:
        b_id, b_title, b_author, u_id, u_name, b_u_rating = row
        # 같은 record는 무시하도록 ignore 추가
        cursor.execute(f"insert ignore into books values ({b_id}, '{b_title}', '{b_author}')")
        cursor.execute(f"insert ignore into users values ({u_id}, '{u_name}')")
        cursor.execute(f"insert ignore into ratings values ({b_id}, {u_id}, {b_u_rating})")
    connection.commit()

    print('Database successfully initialized')

def reset():
    reset = input("Reset?(y/n): ")
    if reset == "y":
        # drop all the tables
        try:
            for table in reversed(TABEL_NAMES):
                cursor.execute(f"drop table {table}")
        except:
            pass
    else:
        return
    connection.commit()
    # initiailize
    csvFile = pd.read_csv('data.csv',encoding='utf-8')

    row_list = csvFile.values.tolist()
    for row in row_list:
        b_id, b_title, b_author, u_id, u_name, b_u_rating = row
        cursor.execute(f"insert ignore into books values ({b_id}, '{b_title}', '{b_author}')")
        cursor.execute(f"insert ignore into users values ({u_id}, '{u_name}')")
        cursor.execute(f"insert ignore into ratings values ({b_id}, {u_id}, {b_u_rating})")
    connection.commit()

    print('Database successfully initialized')

def print_books():
    # print all book infos
    print("-------------------------------------------------------------------------------------------------------------------")
    print(f'{"id".ljust(8)}{"title".ljust(50)}{"author".ljust(30)}{"avg.rating".ljust(16)}{"quantity".ljust(10)}')
    print("-------------------------------------------------------------------------------------------------------------------")
    # query for fetching book info
    books = executor("select T.id as id, title, author, avg(b_u_rating) as avg_rating, quantity "
                   "from (select books.b_id as id, books.b_title as title, books.b_author as author, 1-count(borrow.u_id) as quantity from books left join borrow on books.b_id = borrow.b_id group by books.b_id) as T "
                   "left join ratings on T.id = ratings.b_id "
                   "group by T.id order by T.id")
    for book in books:
        print(f"{str(book['id']).ljust(8)}{book['title'].ljust(50)}{book['author'].ljust(30)}{str(None if book['avg_rating'] is None else round(book['avg_rating'],1)).ljust(16)}{str(book['quantity']).ljust(10)}")
    print("-------------------------------------------------------------------------------------------------------------------")
    
def print_users():
    # print all user infos
    print("--------------------------------------------------------------------------------")
    print(f'{"id".ljust(8)}{"name".ljust(16)}')
    print("--------------------------------------------------------------------------------")
    users = executor("select * from users order by u_id")
    for user in users:
        print(f"{str(user['u_id']).ljust(8)}{user['u_name'].ljust(16)}")
    print("--------------------------------------------------------------------------------")

def insert_book():
    title = input('Book title: ')
    author = input('Book author: ')

    # book length
    if not 1<=len(title)<=50:
        print("Title length should range from 1 to 50 characters")
        return
    
    # author length
    if not 1<=len(author)<=30:
        print("Author length should range from 1 to 30 characters")
        return 
    
    # already existing book
    book = executor(f"select * from books where b_title = '{title}' and b_author = '{author}'")
    if book:
        print(f"Book ({title}, {author}) already exists")
        return
    
    # insert the book
    cursor.execute(f"insert into books(b_title, b_author) values ('{title}','{author}')")
    connection.commit()

    print("One book successfully inserted")

def remove_book():
    book_id = input('Book ID: ')
    exist = executor(f"select * from books where b_id = {book_id}")

    # not existing book
    if not exist:
        print(f"Book {book_id} does not exist")
        return
    
    borrow = executor(f"select * from borrow where b_id = {book_id}")

    # currently borrowed book
    if borrow:
        print("Cannot delete a book that is currently borrowed")
        return 
    
    cursor.execute(f"delete from books where b_id = {book_id}")
    connection.commit()
    print("One book successfully removed")

def insert_user():
    name = input('User name: ')

    # username length
    if not 1<=len(name)<=10:
        print("Username length should range from 1 to 10 characters")
        return
    
    cursor.execute(f"insert into users(u_name) values ('{name}')")
    connection.commit()
    print("One user successfully inserted")

def remove_user():
    user_id = input('User ID: ')

    exist = executor(f"select * from users where u_id = {user_id}")
    # not existing user
    if not exist:
        print(f"User {user_id} does not exist")
        return
    borrow = executor(f"select * from borrow where u_id = {user_id}")

    # user borrowed book
    if borrow:
        print("Cannot delete a user with borrowed books")
        return 
    
    cursor.execute(f"delete from users where u_id = {user_id}")
    connection.commit()
    print("One user successfully removed")

def checkout_book():
    book_id = input('Book ID: ')
    user_id = input('User ID: ')

    book_exist = executor(f"select * from books where b_id = {book_id}")
    # not existing book
    if not book_exist:
        print(f"Book {book_id} does not exist")
        return
    
    user_exist = executor(f"select * from users where u_id = {user_id}")
    # not existing user
    if not user_exist:
        print(f"User {user_id} does not exist")
        return
    
    borrow= executor(f"select * from borrow where b_id ={book_id}")
    # currently borrowed book
    if borrow:
        print("Cannot check out a book that is currently borrowed")
        return
    
    borrow_count = executor(f"select count(*) as cnt from borrow where u_id = {user_id}")
    # maximum borrowing limit
    if borrow_count[0]['cnt']>=2:
        print(f"User {user_id} exceeded the maximum borrowing limit")
        return

    cursor.execute(f"insert into borrow values ({book_id},{user_id})")
    connection.commit()
    print("Book successfully checked out")

def return_and_rate_book():
    book_id = input('Book ID: ')
    user_id = input('User ID: ')
    rating = input('Ratings (1~5): ')
    
    book_exist = executor(f"select * from books where b_id = {book_id}")
    # not existing book
    if not book_exist:
        print(f"Book {book_id} does not exist")
        return
    
    user_exist = executor(f"select * from users where u_id = {user_id}")
    # not existing user
    if not user_exist:
        print(f"User {user_id} does not exist")
        return

    # invalid rating
    if rating not in ['1','2','3','4','5']:
        print("Rating should range from 1 to 5")
        return
    
    borrow = executor(f"select * from borrow where b_id = {book_id} and u_id = {user_id}")
    # not currently borrowed book
    if not borrow:
        print("Cannot return and rate a book that is not currently borrowed for this user")
        return

    cursor.execute(f"delete from borrow where b_id = {book_id} and u_id = {user_id}")

    rating_exist = executor(f"select * from ratings where b_id = {book_id} and u_id = {user_id}")
    # update if already rated
    if rating_exist:
        cursor.execute(f"update ratings set b_u_rating = {rating} where b_id = {book_id} and u_id = {user_id}")
    else:
        cursor.execute(f"insert into ratings values ({book_id},{user_id},{int(rating)})")
    connection.commit()

    print("Book successfully returned and rated")

def print_borrowing_status_for_user():
    user_id = input('User ID: ')

    user_exist = executor(f"select * from users where u_id = {user_id}")
    # not existing user
    if not user_exist:
        print(f"User {user_id} does not exist")
        return
    
    # fetch borrowing status
    borrow = executor(f"select books.b_id as id, books.b_title as title, books.b_author as author, avg(b_u_rating) as rating from books left join borrow on books.b_id = borrow.b_id "
                   f"left join ratings on books.b_id = ratings.b_id where borrow.u_id = {user_id} group by books.b_id order by books.b_id")

    print("-------------------------------------------------------------------------------------------------------------------")
    print(f'{"id".ljust(8)}{"title".ljust(50)}{"author".ljust(30)}{"avg.rating".ljust(16)}')
    print("-------------------------------------------------------------------------------------------------------------------")
    for book in borrow:
        print(f"{str(book['id']).ljust(8)}{book['title'].ljust(50)}{book['author'].ljust(30)}{str(None if book['rating'] is None else round(book['rating'],1)).ljust(16)}")
    print("-------------------------------------------------------------------------------------------------------------------")

def search_books():
    query = input('Query: ')
    # search book with title
    print("-------------------------------------------------------------------------------------------------------------------")
    print(f'{"id".ljust(8)}{"title".ljust(50)}{"author".ljust(30)}{"avg.rating".ljust(16)}{"quantity".ljust(10)}')
    print("-------------------------------------------------------------------------------------------------------------------")
    books = executor("select T.id as id, title, author, avg(b_u_rating) as avg_rating, quantity "
                   "from (select books.b_id as id, books.b_title as title, books.b_author as author, 1-count(borrow.u_id) as quantity from books left join borrow on books.b_id = borrow.b_id group by books.b_id) as T "
                   "left join ratings on T.id = ratings.b_id "
                   f"where lower(T.title) like lower('%{query}%') "
                   "group by T.id order by T.id")
    for book in books:
        print(f"{str(book['id']).ljust(8)}{book['title'].ljust(50)}{book['author'].ljust(30)}{str(None if book['avg_rating'] is None else round(book['avg_rating'],1)).ljust(16)}{str(book['quantity']).ljust(10)}")
    print("-------------------------------------------------------------------------------------------------------------------")

def recommend_popularity():
    user_id = input('User ID: ')
    user_exist = executor(f"select * from users where u_id = {user_id}")
    # not existing user
    if not user_exist:
        print(f"User {user_id} does not exist")
        return
    
    print("-------------------------------------------------------------------------------------------------------------------")
    print("Rating-based")
    print("-------------------------------------------------------------------------------------------------------------------")
    print(f'{"id".ljust(8)}{"title".ljust(50)}{"author".ljust(30)}{"avg.rating".ljust(16)}')
    print("-------------------------------------------------------------------------------------------------------------------")
    # highest average rating
    books = executor("select books.b_id as id, books.b_title as title, books.b_author as author, S.avg as avg "
                   f"from (select T.b_id as id, avg(b_u_rating) as avg, count(*) as cnt from (select books.b_id as b_id from books left join (select * from ratings where u_id = {user_id}) as ratings "
                   "on books.b_id = ratings.b_id where ratings.b_id is null) as T left join ratings on T.b_id = ratings.b_id "
                   f"group by T.b_id order by T.b_id) as S join books on books.b_id = S.id order by avg, books.b_id")
    print(f"{str(books[0]['id']).ljust(8)}{books[0]['title'].ljust(50)}{books[0]['author'].ljust(30)}{str(None if books[0]['avg'] is None else round(books[0]['avg'],1)).ljust(16)}")
    
    print("-------------------------------------------------------------------------------------------------------------------")
    print("Popularity-based")
    print("-------------------------------------------------------------------------------------------------------------------")
    print(f'{"id".ljust(8)}{"title".ljust(50)}{"author".ljust(30)}{"avg.rating".ljust(16)}')
    print("-------------------------------------------------------------------------------------------------------------------")
    # most ratings
    books = executor(f"select books.b_id as id, books.b_title as title, books.b_author as author, S.avg as avg, S.cnt as cnt "
                   f"from (select T.b_id as id, avg(b_u_rating) as avg, count(*) as cnt from (select books.b_id as b_id from books left join (select * from ratings where u_id = {user_id}) as ratings "
                   "on books.b_id = ratings.b_id where ratings.b_id is null) as T left join ratings on T.b_id = ratings.b_id "
                   f"group by T.b_id order by T.b_id) as S join books on books.b_id = S.id order by cnt, books.b_id")
    print(f"{str(books[0]['id']).ljust(8)}{books[0]['title'].ljust(50)}{books[0]['author'].ljust(30)}{str(None if books[0]['avg'] is None else round(books[0]['avg'],1)).ljust(16)}")
    print("-------------------------------------------------------------------------------------------------------------------")

# fill the NaN entry (recommend_item_based)
def fill_nan(row):
    if row.isna().all():
        return row.fillna(0)
    else:
        return row.fillna(row.mean())

# cosine similarity of two rows (recommend_item_based)
def cosine_similarity(row1, row2):
    dot_product = (row1 * row2).sum()
    norm_row1 = (row1**2).sum()**0.5
    norm_row2 = (row2**2).sum()**0.5
    if norm_row1 == 0 or norm_row2 == 0:
        return 0
    else:
        return dot_product / (norm_row1 * norm_row2)

def recommend_item_based():
    user_id = input('User ID: ')

    user_exist = executor(f"select * from users where u_id = {user_id}")
    # not existing user
    if not user_exist:
        print(f"User {user_id} does not exist")
        return
    
    ratings = executor(f"select * from ratings")

    # fetch all user id
    users = executor(f"select u_id from users")
    users = [user['u_id'] for user in users]

    # fetch all book id
    books = executor(f"select b_id from books")
    books = [book['b_id'] for book in books]

    # create matrix for calculation
    raw_matrix = pd.DataFrame(index=users, columns=books)
    matrix = pd.DataFrame(index=users, columns=books)
    raw_matrix = matrix.astype(float)
    matrix = matrix.astype(float)

    # insert the rating info to matrix
    for row in ratings:
        raw_matrix.at[row['u_id'], row['b_id']] = row['b_u_rating']

    matrix = raw_matrix.apply(fill_nan, axis=1) # apply fill_nan

    # create similarity matrix
    similarity_matrix = pd.DataFrame(index=users, columns=users)

    # insert cosine similarity
    for i in users:
        for j in users:
            similarity_matrix.at[i, j] = cosine_similarity(matrix.loc[i], matrix.loc[j])

    user_id = int(user_id)
    user_ratings = raw_matrix.loc[user_id] # rating from the user
    other_users = matrix.index[matrix.index != user_id] # list of other user
    predictions = {}
    
    for book_id in matrix.columns:
        # calculate the predicted ratings (formula from the spec pdf)
        if pd.isna(user_ratings[book_id]):
            numerator = 0
            denominator = 0
            for other_user in other_users:
                if not pd.isna(matrix.at[other_user, book_id]):
                    similarity = similarity_matrix.at[user_id, other_user]
                    rating = matrix.at[other_user, book_id]
                    numerator += similarity * rating
                    denominator += similarity
            if denominator != 0:
                predictions[book_id] = numerator / denominator
            else:
                predictions[book_id] = 0
    
    best_book_id, pred_rating = sorted(predictions.items(), key=lambda x: (-x[1], x[0]))[0]
    
    print("-------------------------------------------------------------------------------------------------------------------")
    print(f'{"id".ljust(8)}{"title".ljust(50)}{"author".ljust(30)}{"avg.rating".ljust(16)}{"exp.rating".ljust(10)}')
    print("-------------------------------------------------------------------------------------------------------------------")
    # fetch info about the recommendation book
    books = executor("select books.b_id as id, b_title, b_author, avg(b_u_rating) as avg_rating "
                   f"from books left join ratings on books.b_id = ratings.b_id where books.b_id={best_book_id}")
    for book in books:
        print(f"{str(book['id']).ljust(8)}{book['b_title'].ljust(50)}{book['b_author'].ljust(30)}{str(None if book['avg_rating'] is None else round(book['avg_rating'],1)).ljust(16)}{round(pred_rating,2)}")
    print("-------------------------------------------------------------------------------------------------------------------")    

def main():
    # SQL connection setting
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
            menu = input('Select your action: ')
            try:
                menu = int(menu)
                if menu == 1:
                    initialize_database() # 데이터 베이스 초기화
                elif menu == 2:
                    print_books() # 모든 책 출력
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
            except: print('Invalid action')
        
        connection.close()

if __name__ == "__main__":
    main()

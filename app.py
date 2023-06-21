from flask import Flask, render_template, request , session , redirect, url_for
import mysql.connector
from datetime import datetime,timedelta
import stripe
from mail import send_email
app = Flask(__name__)
app.secret_key = b'\x04qw\xa5)\xf02o\xb3\xc1\x11\x83\xab\x12=\x1f6\xba)\x0bO\x96S\xd6\x86\x1d\xbe\xa3\xcf\xae\xfa\xc1'
# Establish a connection to the MySQL database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="system",
    database="codegnan"
)

@app.route("/")
def index():
    return render_template('home.html')

@app.route('/admin_home')
def admin_home():
    return render_template('admin_page.html')

@app.route('/student_home')
def student_home():
    return render_template('student_page.html')

# Admin signup page
@app.route("/admin/signup", methods=['GET', 'POST'])
def admin_signup():
    if request.method == 'POST':
        user_id = request.form['id']
        username = request.form['username']
        mail = request.form['mail']
        password = request.form['password']
        
        cursor = db.cursor()
        
        # Create a new admin user
        try:
            cursor.execute("INSERT INTO admin_users (id,username,mail,password) VALUES (%s,%s,%s,%s)", (user_id,username,mail,password))
            db.commit()
            success_message = "Account created successfully. You can now log in."
            return render_template('admin_login.html', success_message=success_message)
        except mysql.connector.Error as error:
            error_message = f"Failed to create account: {error}"
            return render_template('admin_signup.html', error_message=error_message)
    
    return render_template('admin_signup.html')

# Admin login page
@app.route("/admin/login", methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        user_id = request.form['id']
        password = request.form['password']
        
        cursor = db.cursor()
        
        # Check if username and password are valid for admin users
        cursor.execute("SELECT * FROM admin_users WHERE id = %s AND password = %s", (user_id, password))
        admin_user = cursor.fetchone()
        # print(admin_user[0])
        # print(admin_user[1])
        # print(admin_user[2])
        if admin_user:
            session['id'] = admin_user[0]
            session['role'] = 'admin'
            return render_template('admin_page.html',data=admin_user[0])
        else:
            error_message = "Invalid username/password"
            return render_template('admin_login.html', error_message=error_message)
    
    return render_template('admin_login.html')


@app.route("/student/signup", methods=['GET', 'POST'])
def student_signup():
    if request.method == 'POST':
        user_id = request.form['id']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        gender = request.form['gender']
        branch = request.form['branch']
        email = request.form['email']
        phoneno = request.form['phoneno']
        password = request.form['password']
        
        cursor = db.cursor()
        
        # Create a new student user
        try:
            cursor.execute("INSERT INTO student_users (id,first_name,last_name,gender,branch,email_id,phone_no,password) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", (user_id,first_name,last_name,gender,branch,email,phoneno,password))
            db.commit()
            success_message = "Account created successfully."
            return render_template('student_login.html', success_message=success_message)
        except mysql.connector.Error as error:
            error_message = "Student id already exists"
            return render_template('student_signup.html', error_message=error_message)
    
    return render_template('student_signup.html')

# Student login page
@app.route("/student/login", methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        user_id = request.form['id']
        password = request.form['password']
        
        cursor = db.cursor()
        
        # Check if username and password are valid for student users
        cursor.execute("SELECT * FROM student_users WHERE id = %s AND password = %s", (user_id, password))
        student_user = cursor.fetchone()
        
        if student_user:
            session['id'] = student_user[0]
            session['role'] = 'student'
            return render_template('student_page.html',data=student_user[0])
        else:
            error_message = "Invalid username or password."
            return render_template('student_login.html', error_message=error_message)
    
    return render_template('student_login.html')

@app.route('/forgot_password/student',methods = ['GET','POST'])
def sutdent_password():

    if request.method == 'POST':

        id = request.form['id']
        new_pass = request.form['password']
        pass_again = request.form['pass']
        if new_pass == pass_again:
            cursor = db.cursor()
            cursor.execute('select * from student_users where id =%s',(id,))
            data = cursor.fetchone()
            if data is not None:
                cursor.execute('update student_users set password=%s where id =%s',(new_pass,id))
                db.commit()
                success_message= 'student password changed'
                return render_template('student_login.html',success_message= success_message)
            else:
                error_message = 'student id not found'
                return render_template('forgot_password.html',error_message=error_message)
        else:
            error_message = 'password not matched'
            return render_template('forgot_password.html',error_message=error_message)

    return render_template('forgot_password.html')

@app.route('/forgot_password/admin',methods = ['GET','POST'])
def admin_password():

    if request.method == 'POST':

        id = request.form['id']
        new_pass = request.form['password']
        pass_again = request.form['pass']
        if new_pass == pass_again:
            cursor = db.cursor()
            cursor.execute('select * from admin_users where id =%s',(id,))
            data = cursor.fetchone()
            if data is not None:
                cursor.execute('update admin_users set password=%s where id =%s',(new_pass,id))
                db.commit()
                success_message= 'admin password changed'
                return render_template('admin_login.html',success_message= success_message)
            else:
                error_message = 'admin id not found'
                return render_template('admin_forgot.html',error_message=error_message)
        else:
            error_message = 'password not matched'
            return render_template('admin_forgot.html',error_message=error_message)
        
    return render_template('admin_forgot.html')

@app.route('/logout',methods=['GET'])
def logout():
    session.clear()
    success_message = "successfully logged out"
    return render_template('home.html',success_message = success_message)

#admin page
@app.route("/books/add", methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        id = request.form['book_id']
        title = request.form['title']
        author = request.form['author']
        genre = request.form['genre']
        copies = int(request.form['copies'])
        price  = int(request.form['price'])
        cursor = db.cursor()

        cursor.execute("select * from books where title =%s and author =%s",(title,author))
        
        data = cursor.fetchone()
        if data:
            
            total_copies = data[4] + copies
            available_copies=data[5] + copies
            cursor.execute("update books set copies = %s where id = %s",(total_copies,data[0]))
            cursor.execute("update books set available_copies = %s where id =%s",(available_copies,data[0]))
            db.commit()
            success_message = "book copy successfully added"
            return render_template("book_add.html",success_message=success_message)
        
        # Insert the book data into the books table
        else:
            try:

                cursor.execute("INSERT INTO books (id,title, author,genre,copies,available_copies,price) VALUES (%s,%s, %s, %s,%s,%s,%s)",
                           (id,title, author, genre,copies,copies,price))
                db.commit()
                success_message = "Book added successfully."
                return render_template('book_add.html', success_message=success_message)
            except mysql.connector.Error as error:
                error_message = "Failed to add book"
                return render_template('book_add.html', error_message=error_message)
    
    return render_template('book_add.html')

#admin,student page
@app.route('/books/display' ,methods=['Get'])
def display_book():

    cursor = db.cursor()
    cursor.execute('select * from books')
    data = cursor.fetchall()
    return render_template('display_books.html',books=data)

#admin page
@app.route('/delete_books',methods=['GET','POST'])
def delete_books():
    if request.method == 'POST':

        book_id = request.form['bookid']
        cursor = db.cursor()
        cursor.execute('select * from books where id = %s',(book_id,))
        data = cursor.fetchone()
        if data is not None:
            cursor.execute('delete from books where id =%s',(book_id,))
            success_message = "deleted successfully"
            return render_template('delete_books.html',success_message=success_message)
        else:
            error_message="book id not found"
            return render_template('delete_books.html',error_message=error_message)
    return render_template('delete_books.html')
        
#admin page
@app.route('/search', methods=['GET'])
def search():
    
    keyword = request.args.get('search_query','')
    cursor = db.cursor()
    query = "SELECT * FROM books WHERE title LIKE %s OR author LIKE %s"
    search_keyword = f"%{keyword}%"
    cursor.execute(query, (search_keyword, search_keyword))
    results = cursor.fetchall()
    cursor.close()
    return render_template('display_books.html', books=results)
    


#admin page
@app.route("/rental", methods=['POST','GET'])
def rental():
    
    if request.method == 'POST':
        student_id = request.form['id']
        book_id = request.form['book_id']
        date = request.form['date']

        cursor = db.cursor()
        
        # Check if the book is available
        cursor.execute("SELECT * FROM books WHERE id = %s AND available_copies > 0 ", (book_id,))
        book = cursor.fetchone()
        
        if book:
            avail_copies = book[5]
            rental_copies = book[6]
            rental_date = datetime.now().date()
            due_date = date
            due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
            difference = due_date -rental_date
            day_differ = difference.days
            print(day_differ)
            fine = day_differ * book[7]
            cursor.execute("SELECT id FROM student_users WHERE id = %s", (student_id,))
            data =cursor.fetchone()
            if data is not None:
                user_id = data[0]
                cursor.execute("INSERT INTO rentals (book_id, user_id, rental_date, due_date,fine) VALUES (%s, %s, %s,%s,%s)",
                            (book_id, user_id, rental_date, due_date,fine))
                
                cursor.execute("update books set available_copies = %s where id = %s",(avail_copies-1,book_id))
                cursor.execute("update books set rental_count = %s where id = %s",(rental_copies+1,book_id))
                cursor.execute("select mail from admin_users where id =%s",(session['id'],)) 
                sender_data= cursor.fetchone()[0]
                print(sender_data)
                cursor.execute("select email_id from student_users where id =%s",(student_id,))
                receiver_data = cursor.fetchone()[0]
                print(sender_data)
                print(receiver_data)
                db.commit()

                success_message ="book issued"
                sender_email = sender_data
                receiver_email = receiver_data
                subject = 'Email Confirmation'
                message = f"Greetings! You have taken a book with ID {book_id}. Please remember to return it before the due date to avoid any fines. Thank you!" 

                send_email(sender_email, receiver_email, subject, message)                

                return render_template('rental.html', success_message=success_message)

            else:
                error_message = "student id not found"
                return render_template('rental.html',error_message=error_message)
        else:
            error_message = "Book not available for rental."
            return render_template('rental.html', error_message=error_message)
    
    return render_template('rental.html')
    
#student page
@app.route('/display/rentals',methods=['GET'])
def display_rentals():
    # update_fines()
    payment_eligibility = []
    cursor = db.cursor()
    cursor.execute("select id from student_users where id =%s",(session['id'],))
    user_id = cursor.fetchone()[0]
    cursor.execute("select * from rentals where user_id =%s",(user_id,))
    data = cursor.fetchall()
    print(data)
    for x in data:
        eligible_to_pay = False
        if x[5] >0 and x[6] == 'not_returned':
            eligible_to_pay = True
            payment_eligibility.append(eligible_to_pay)
        else:
            payment_eligibility.append(eligible_to_pay)
    db.commit()
    
    combined_data = zip(data,payment_eligibility)
    return render_template('display_rental.html',combined_data = combined_data)

#admin page
@app.route('/books/rental',methods=['GET'])
def rental_books():
    cursor = db.cursor()
    cursor.execute("select * from rentals")
    data = cursor.fetchall()
    db.commit()
    return render_template('rental_display.html',data=data)

stripe.api_key = 'sk_test_51NK13RSAYoh2SIQsMB5FUgsPZ4fWxu68pmGfR5p77CIVc7Mo39QBF4iwRFBGbhCce9mIRpBHeFLubnoa5brw4nwz00RvrTVkDV'

#student page
@app.route('/pay_fine/<float:fine>/<string:bookid>/<string:userid>', methods=['POST'])
def pay_fine(fine,bookid,userid):
    # Retrieve the fine amount from the form or database
    print(fine)
    fine_amount = float(fine)

    # Create a Checkout Session
    checkout_session = stripe.checkout.Session.create(
        success_url=url_for('payment_success',fine=fine,bookid = bookid,userid=userid,_external=True),
        cancel_url=url_for('payment_cancel', _external=True),
        payment_method_types=['card'],
        line_items=[
            {
                'price_data': {
                    'currency': 'INR',
                    'unit_amount': int(fine_amount)*100,  
                    'product_data': {
                        'name': 'Book Fine Payment',
                    },
                },
                'quantity': 1,
            }
        ],
        mode='payment',
    )

    return redirect(checkout_session.url)


@app.route('/payment_success/<float:fine>/<string:bookid>/<string:userid>')
def payment_success(fine,bookid,userid):       
    
    cursor=db.cursor()
    cursor.execute("update rentals set status=%s where user_id= %s and book_id=%s",('returned',userid,bookid))
    cursor.execute('select * from books where id=%s',(bookid,))
    data= cursor.fetchone()
    avail_copies= data[5]
    rental_copies = data[6]
    cursor.execute("update books set available_copies = %s,rental_count =%s where id = %s",(avail_copies+1,rental_copies-1,bookid))

    cursor.execute("select email_id from student_users where id = %s",(userid,))
    receiver_data = cursor.fetchone()[0]
    cursor.execute('select mail from admin_users')
    sender_data = cursor.fetchone()[0]

    sender_email = sender_data
    receiver_email = receiver_data
    subject = 'Email Confirmation'
    message = f"You have paid fine of {fine} rupees for book with id {bookid}.Thank you!" 
    send_email(sender_email, receiver_email, subject, message)  


    db.commit()
    success_message= 'payment successful'
    return render_template('student_page.html',success_message = success_message)


@app.route('/payment_cancel')
def payment_cancel():
    # Handle payment cancellation
    return render_template('payment_cancel.html')

#student page
@app.route('/addsuggestion',methods=['GET','POST'])
def addsuggestions():
    if request.method == 'POST':
        id = request.form['id']
        branch = request.form['section']
        suggestion = request.form['suggestion']
        cursor = db.cursor()
        cursor.execute("insert into suggestions (id,branch,suggestion) values (%s,%s,%s)",(id,branch,suggestion))
        db.commit()
        return redirect('/')
    return render_template('add_suggestion.html')


#admin page
@app.route('/displaysuggestion',methods=['GET'])
def displaysuggestion():
    
    cursor = db.cursor()
    cursor.execute('select * from suggestions')
    data = cursor.fetchall()
    return render_template('display_suggestion.html',data=data)

if __name__  == "__main__":
    app.run(debug = True)


import datetime

# --- Configuration ---
DEFAULT_BORROWING_PERIOD_DAYS = 14  # How long can someone keep a book? (2 weeks)
PENALTY_RATE_PER_DAY = 0.50  # Penalty amount (e.g., $0.50 or ֏200) per day overdue


class Book:
    def __init__(self, book_id, title, author):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.is_borrowed = False

    def __str__(self):
        status = "Borrowed" if self.is_borrowed else "Available"
        return f"ID: {self.book_id}, Title: '{self.title}' by {self.author} ({status})"


class Student:
    def __init__(self, student_id, name):
        self.student_id = student_id
        self.name = name

    def __str__(self):
        return f"ID: {self.student_id}, Name: {self.name}"


class BorrowRecord:
    def __init__(self, student_id, book_id, checkout_date, due_date):
        self.student_id = student_id
        self.book_id = book_id
        self.checkout_date = checkout_date
        self.due_date = due_date
        self.return_date = None  # Set when the book is returned
        self.penalty_paid = 0.0

    def calculate_days_overdue(self, return_date):
        """Calculates how many days overdue a book is."""
        if return_date > self.due_date:
            return (return_date - self.due_date).days
        return 0

    def calculate_penalty(self, return_date):
        """Calculates the penalty based on the return date."""
        days_overdue = self.calculate_days_overdue(return_date)
        return days_overdue * PENALTY_RATE_PER_DAY

    def __str__(self):
        returned_status = f"Returned: {self.return_date.strftime('%Y-%m-%d')}" if self.return_date else "Not Returned Yet"
        penalty_info = f", Penalty Paid: ${self.penalty_paid:.2f}" if self.return_date else ""  # Or use ֏ for Dram
        return (f"Student ID: {self.student_id}, Book ID: {self.book_id}, "
                f"Checked Out: {self.checkout_date.strftime('%Y-%m-%d')}, "
                f"Due: {self.due_date.strftime('%Y-%m-%d')}, "
                f"{returned_status}{penalty_info}")


class Library:
    """Manages books, students, and borrowing records."""

    def __init__(self):
        self.books = {}  # book_id -> Book object
        self.students = {}  # student_id -> Student object
        self.borrow_records = []  # List of BorrowRecord objects (active and historical)
        self.active_borrows = {}  # BorrowRecord object (for quick lookup of active borrows)

    def add_book(self, book_id, title, author):
        if book_id in self.books:
            print(f"Book ID {book_id} already exists. No duplicates, fam.")
            return None
        book = Book(book_id, title, author)
        self.books[book_id] = book
        print(f"Book added: {book}")
        return book

    def add_student(self, student_id, name):
        if student_id in self.students:
            print(f" Student ID {student_id} already exists.")
            return None
        student = Student(student_id, name)
        self.students[student_id] = student
        print(f"Student added: {student}")
        return student

    def checkout_book(self, student_id, book_id):
        # --- Validations ---
        if student_id not in self.students:
            print(f" Error: Student ID {student_id} not found. Add the student first.")
            return False
        if book_id not in self.books:
            print(f"Error: Book ID {book_id} not found.")
            return False

        book = self.books[book_id]
        if book.is_borrowed:
            print(f"Error: Book '{book.title}' (ID: {book_id}) is already borrowed.")
            return False

        # --- Process Checkout ---
        checkout_date = datetime.date.today()
        due_date = checkout_date + datetime.timedelta(days=DEFAULT_BORROWING_PERIOD_DAYS)

        record = BorrowRecord(student_id, book_id, checkout_date, due_date)
        self.borrow_records.append(record)
        self.active_borrows[book_id] = record  # Track active borrow by book ID

        book.is_borrowed = True

        print(f" Checkout successful!")
        print(f"   Student: {self.students[student_id].name} (ID: {student_id})")
        print(f"   Book: '{book.title}' (ID: {book_id})")
        print(f"   Checkout Date: {checkout_date.strftime('%Y-%m-%d')}")
        print(f"   Due Date: {due_date.strftime('%Y-%m-%d')}")
        return True

    def return_book(self, book_id):
        if book_id not in self.books:
            print(f"Error: Book ID {book_id} not found.")
            return False

        book = self.books[book_id]
        if not book.is_borrowed or book_id not in self.active_borrows:
            print(f" Error: Book '{book.title}' (ID: {book_id}) wasn't marked as borrowed or no active record found.")
            return False

        # --- Process Return ---
        record = self.active_borrows[book_id]
        return_date = datetime.date.today()
        record.return_date = return_date

        penalty = record.calculate_penalty(return_date)
        days_overdue = record.calculate_days_overdue(return_date)

        book.is_borrowed = False
        del self.active_borrows[book_id]  # Remove from active borrows

        print(f"   Return successful!")
        print(f"   Book: '{book.title}' (ID: {book_id})")
        print(f"   Student: {self.students[record.student_id].name} (ID: {record.student_id})")
        print(f"   Return Date: {return_date.strftime('%Y-%m-%d')}")
        print(f"   Due Date was: {record.due_date.strftime('%Y-%m-%d')}")

        if days_overdue > 0:
            print(f"    Overdue by: {days_overdue} days")
            print(f"    Penalty Due: ${penalty:.2f}")
            #  adding logic to track if the penalty was actually paid
            record.penalty_paid = penalty  # Assuming it's paid on return for simplicity
        else:
            print("    Returned on time or early. Noice!")

        return True

    def list_all_books(self):
        print("\n--- Library Book Catalog ---")
        if not self.books:
            print("No books in the library yet.")
            return
        for book in self.books.values():
            print(book)
        print("--------------------------\n")

    def list_all_students(self):
        print("\n--- Registered Students ---")
        if not self.students:
            print("No students registered yet.")
            return
        for student in self.students.values():
            print(student)
        print("-------------------------\n")

    def list_borrowed_books(self, student_id=None):
        print("\n--- Currently Borrowed Books ---")
        if not self.active_borrows:
            print("No books are currently borrowed.")
            return

        found_any = False
        for book_id, record in self.active_borrows.items():
            if student_id is None or record.student_id == student_id:
                book = self.books[book_id]
                student = self.students[record.student_id]
                print(f"- '{book.title}' (ID: {book.book_id}) borrowed by {student.name} (ID: {student.student_id}) "
                      f"on {record.checkout_date.strftime('%Y-%m-%d')}, Due: {record.due_date.strftime('%Y-%m-%d')}")
                found_any = True

        if student_id is not None and not found_any:
            print(f"Student {student_id} has no books currently borrowed.")
        elif not found_any:  # Should not happen if active_borrows is not empty
            print("No matching borrowed books found.")
        print("-----------------------------\n")

    def list_overdue_books(self):
        print("\n--- Overdue Books ---")
        today = datetime.date.today()
        found_overdue = False
        for book_id, record in self.active_borrows.items():
            if record.due_date < today:
                book = self.books[book_id]
                student = self.students[record.student_id]
                days_overdue = (today - record.due_date).days
                penalty = record.calculate_penalty(today)  # Calculate penalty up to today
                print(f"- '{book.title}' (ID: {book.book_id}) borrowed by {student.name} (ID: {student.student_id})")
                print(f"  Due: {record.due_date.strftime('%Y-%m-%d')} ({days_overdue} days overdue)")
                print(f"  Current Penalty: ${penalty:.2f}")
                found_overdue = True

        if not found_overdue:
            print("No books are currently overdue. We love to see it!")
        print("---------------------\n")


# --- Main Program / Example Usage ---
if __name__ == "__main__":
    my_library = Library()

    # Add some students
    my_library.add_student("S001", "Narek G")
    my_library.add_student("S002", "Ani P")
    my_library.add_student("S003", "Lia S")

    # Add some books
    my_library.add_book("B001", "Clean Code", "Robert C. Martin")
    my_library.add_book("B002", "The Pragmatic Programmer", "Andrew Hunt")
    my_library.add_book("B003", "Eloquent JavaScript", "Marijn Haverbeke")
    my_library.add_book("B004", "Designing Data-Intensive Applications", "Martin Kleppmann")

    my_library.list_all_books()
    my_library.list_all_students()

    # Simulate checkouts
    print("\n--- Simulating Checkouts ---")
    my_library.checkout_book("S001", "B001")  # Narek checks out Clean Code
    my_library.checkout_book("S002", "B003")  # Ani checks out Eloquent JS
    my_library.checkout_book("S001", "B004")  # Narek checks out DDIA
    my_library.checkout_book("S001", "B003")  # Try checking out already borrowed book (fail)
    my_library.checkout_book("S999", "B002")  # Try checking out with non-existent student (fail)
    print("--------------------------\n")

    my_library.list_borrowed_books()
    my_library.list_borrowed_books(student_id="S001")  # List only Narek's books
    my_library.list_borrowed_books(student_id="S003")  # List Lia's books (none)

    # --- !!! For testing overdue/penalties !!! ---
    # Let's pretend a book was checked out long ago
    if "B001" in my_library.active_borrows:
        print("\n--- !!! Hacking time to test overdue !!! ---")
        record_to_hack = my_library.active_borrows["B001"]
        past_checkout_date = datetime.date.today() - datetime.timedelta(days=30)  # Checked out 30 days ago
        past_due_date = past_checkout_date + datetime.timedelta(days=DEFAULT_BORROWING_PERIOD_DAYS)  # Due 16 days ago
        record_to_hack.checkout_date = past_checkout_date
        record_to_hack.due_date = past_due_date
        print(
            f"Manually set Book B001 checkout date to {past_checkout_date.strftime('%Y-%m-%d')}, due date to {past_due_date.strftime('%Y-%m-%d')}")
        print("---------------------------------------------\n")

    my_library.list_overdue_books()

    print("\n--- Simulating Returns ---")
    my_library.return_book("B001")  # Narek returns Clean Code (likely overdue now)
    my_library.return_book("B003")  # Ani returns Eloquent JS (likely on time)
    my_library.return_book("B002")  # Try returning a book not borrowed (fail)
    print("------------------------\n")

    my_library.list_borrowed_books()  # See what's left
    my_library.list_all_books()  # Check availability status

    print("\n--- Final Check for Overdue ---")
    my_library.list_overdue_books()  # Should be empty now unless B004 is overdue too
    print("-----------------------------\n")

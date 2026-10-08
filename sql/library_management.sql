-- ============================================================
-- LIBRARY MANAGEMENT DASHBOARD
-- MySQL 8.0.16+
-- ============================================================

DROP DATABASE IF EXISTS library_management;
CREATE DATABASE library_management;
USE library_management;

CREATE TABLE books (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    isbn VARCHAR(20) NOT NULL UNIQUE,
    title VARCHAR(150) NOT NULL,
    author VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    publisher VARCHAR(100),
    publication_year YEAR,
    total_copies INT NOT NULL DEFAULT 1,
    available_copies INT NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_book_total_copies CHECK (total_copies > 0),
    CONSTRAINT chk_book_available_copies CHECK (available_copies >= 0),
    CONSTRAINT chk_book_copy_limit CHECK (available_copies <= total_copies)
);

CREATE TABLE members (
    member_id INT AUTO_INCREMENT PRIMARY KEY,
    member_code VARCHAR(20) NOT NULL UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(15),
    address VARCHAR(200),
    membership_date DATE NOT NULL DEFAULT (CURRENT_DATE),
    status ENUM('Active', 'Inactive') NOT NULL DEFAULT 'Active',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE loans (
    loan_id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    member_id INT NOT NULL,
    issue_date DATE NOT NULL DEFAULT (CURRENT_DATE),
    due_date DATE NOT NULL,
    return_date DATE NULL,
    status ENUM('Borrowed', 'Returned', 'Overdue') NOT NULL DEFAULT 'Borrowed',
    fine DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_loan_book FOREIGN KEY (book_id) REFERENCES books(book_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_loan_member FOREIGN KEY (member_id) REFERENCES members(member_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_due_date CHECK (due_date >= issue_date),
    CONSTRAINT chk_return_date CHECK (return_date IS NULL OR return_date >= issue_date),
    CONSTRAINT chk_fine CHECK (fine >= 0)
);

CREATE INDEX idx_books_title ON books(title);
CREATE INDEX idx_books_category ON books(category);
CREATE INDEX idx_members_status ON members(status);
CREATE INDEX idx_loans_due_date ON loans(due_date);
CREATE INDEX idx_loans_member ON loans(member_id);
CREATE INDEX idx_loans_book ON loans(book_id);
CREATE INDEX idx_loans_status ON loans(status);

INSERT INTO books
(isbn,title,author,category,publisher,publication_year,total_copies,available_copies)
VALUES
('9780131103627','The C Programming Language','Brian Kernighan','Programming','Prentice Hall',1988,5,5),
('9780132350884','Clean Code','Robert C. Martin','Programming','Prentice Hall',2008,4,4),
('9780262033848','Introduction to Algorithms','Thomas H. Cormen','Computer Science','MIT Press',2009,3,3),
('9780134685991','Effective Java','Joshua Bloch','Programming','Addison-Wesley',2018,3,3),
('9781491950357','Designing Data-Intensive Applications','Martin Kleppmann','Database','O''Reilly Media',2017,2,2),
('9780596007126','Head First Design Patterns','Eric Freeman','Programming','O''Reilly Media',2004,4,4),
('9780131101630','The Pragmatic Programmer','David Thomas','Programming','Addison-Wesley',1999,5,5),
('9780261103303','The Lord of the Rings','J.R.R. Tolkien','Fiction','HarperCollins',1954,3,3);

INSERT INTO members
(member_code,first_name,last_name,email,phone,address,membership_date,status)
VALUES
('MEM001','Rahul','Sharma','rahul.sharma@email.com','9876543210','Kolkata','2026-01-10','Active'),
('MEM002','Priya','Das','priya.das@email.com','9876543211','New Town, Kolkata','2026-01-15','Active'),
('MEM003','Arjun','Roy','arjun.roy@email.com','9876543212','Salt Lake, Kolkata','2026-02-01','Active'),
('MEM004','Ananya','Sen','ananya.sen@email.com','9876543213','Howrah','2026-02-10','Active'),
('MEM005','Rohan','Ghosh','rohan.ghosh@email.com','9876543214','Kolkata','2026-03-05','Inactive'),
('MEM006','Sneha','Paul','sneha.paul@email.com','9876543215','Rajarhat','2026-03-12','Active');

DELIMITER $$

CREATE TRIGGER trg_loans_before_insert
BEFORE INSERT ON loans
FOR EACH ROW
BEGIN
    IF NEW.return_date IS NOT NULL THEN
        SET NEW.status = 'Returned';
    ELSEIF NEW.due_date < CURRENT_DATE THEN
        SET NEW.status = 'Overdue';
    ELSE
        SET NEW.status = 'Borrowed';
    END IF;
END$$

CREATE TRIGGER trg_loans_before_update
BEFORE UPDATE ON loans
FOR EACH ROW
BEGIN
    IF NEW.return_date IS NOT NULL THEN
        SET NEW.status = 'Returned';
    ELSEIF NEW.due_date < CURRENT_DATE THEN
        SET NEW.status = 'Overdue';
    ELSE
        SET NEW.status = 'Borrowed';
    END IF;
END$$

CREATE TRIGGER trg_loans_after_insert
AFTER INSERT ON loans
FOR EACH ROW
BEGIN
    IF NEW.return_date IS NULL THEN
        UPDATE books SET available_copies = available_copies - 1
        WHERE book_id = NEW.book_id;
    END IF;
END$$

CREATE TRIGGER trg_loans_after_update
AFTER UPDATE ON loans
FOR EACH ROW
BEGIN
    IF OLD.return_date IS NULL AND NEW.return_date IS NOT NULL THEN
        UPDATE books SET available_copies = available_copies + 1
        WHERE book_id = NEW.book_id;
    END IF;
END$$

DROP PROCEDURE IF EXISTS issue_book$$
CREATE PROCEDURE issue_book(IN p_book_id INT, IN p_member_id INT, IN p_days INT)
BEGIN
    DECLARE v_available INT DEFAULT 0;
    DECLARE v_member_status VARCHAR(20);
    DECLARE v_active_loans INT DEFAULT 0;

    IF p_days <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Loan period must be greater than zero.';
    END IF;

    SELECT available_copies INTO v_available FROM books WHERE book_id = p_book_id;
    IF v_available IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Book does not exist.';
    END IF;

    SELECT status INTO v_member_status FROM members WHERE member_id = p_member_id;
    IF v_member_status IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Member does not exist.';
    END IF;

    IF v_member_status <> 'Active' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Only active members can borrow books.';
    END IF;

    SELECT COUNT(*) INTO v_active_loans
    FROM loans WHERE member_id = p_member_id AND return_date IS NULL;

    IF v_active_loans >= 5 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Member has reached the maximum of 5 active loans.';
    END IF;

    IF v_available <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No available copies of this book.';
    END IF;

    INSERT INTO loans(book_id,member_id,issue_date,due_date)
    VALUES(p_book_id,p_member_id,CURRENT_DATE,
           DATE_ADD(CURRENT_DATE,INTERVAL p_days DAY));

    SELECT LAST_INSERT_ID() AS new_loan_id;
END$$

DROP PROCEDURE IF EXISTS return_book$$
CREATE PROCEDURE return_book(IN p_loan_id INT)
BEGIN
    DECLARE v_returned DATE;
    DECLARE v_due DATE;
    DECLARE v_fine DECIMAL(10,2);

    SELECT return_date,due_date INTO v_returned,v_due
    FROM loans WHERE loan_id = p_loan_id;

    IF v_due IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Loan does not exist.';
    END IF;

    IF v_returned IS NOT NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'This book has already been returned.';
    END IF;

    SET v_fine = GREATEST(DATEDIFF(CURRENT_DATE,v_due),0) * 5.00;

    UPDATE loans
    SET return_date = CURRENT_DATE, fine = v_fine
    WHERE loan_id = p_loan_id;

    SELECT p_loan_id AS loan_id,CURRENT_DATE AS return_date,v_fine AS fine;
END$$

DELIMITER ;

-- Demo loan records. The triggers automatically adjust available_copies.
INSERT INTO loans(book_id,member_id,issue_date,due_date)
VALUES (1,1,'2026-09-20','2026-10-05');
INSERT INTO loans(book_id,member_id,issue_date,due_date)
VALUES (2,2,'2026-09-01','2026-09-15');
INSERT INTO loans(book_id,member_id,issue_date,due_date,return_date,fine)
VALUES (3,3,'2026-09-05','2026-09-15','2026-09-14',0.00);
INSERT INTO loans(book_id,member_id,issue_date,due_date)
VALUES (5,4,'2026-09-28','2026-10-12');
INSERT INTO loans(book_id,member_id,issue_date,due_date)
VALUES (6,6,'2026-08-20','2026-09-03');
INSERT INTO loans(book_id,member_id,issue_date,due_date,return_date,fine)
VALUES (8,1,'2026-08-01','2026-08-15','2026-08-20',50.00);

CREATE OR REPLACE VIEW available_books AS
SELECT book_id,isbn,title,author,category,total_copies,available_copies
FROM books WHERE available_copies > 0;

CREATE OR REPLACE VIEW active_loans AS
SELECT l.loan_id,l.book_id,l.member_id,b.title AS book_title,
       CONCAT(m.first_name,' ',m.last_name) AS member_name,
       l.issue_date,l.due_date,l.return_date,
       CASE WHEN l.due_date < CURRENT_DATE THEN 'Overdue' ELSE 'Borrowed' END AS current_status,
       l.fine
FROM loans l
JOIN books b ON b.book_id=l.book_id
JOIN members m ON m.member_id=l.member_id
WHERE l.return_date IS NULL;

CREATE OR REPLACE VIEW overdue_books AS
SELECT l.loan_id,b.book_id,b.title AS book_title,b.author,
       m.member_id,m.member_code,
       CONCAT(m.first_name,' ',m.last_name) AS member_name,
       m.email,m.phone,l.issue_date,l.due_date,
       DATEDIFF(CURRENT_DATE,l.due_date) AS days_overdue,
       DATEDIFF(CURRENT_DATE,l.due_date)*5.00 AS calculated_fine
FROM loans l
JOIN books b ON b.book_id=l.book_id
JOIN members m ON m.member_id=l.member_id
WHERE l.return_date IS NULL AND l.due_date < CURRENT_DATE;

CREATE OR REPLACE VIEW dashboard_summary AS
SELECT
 (SELECT COUNT(*) FROM books) AS title_count,
 (SELECT COALESCE(SUM(total_copies),0) FROM books) AS total_copies,
 (SELECT COALESCE(SUM(available_copies),0) FROM books) AS available_copies,
 (SELECT COUNT(*) FROM members) AS total_members,
 (SELECT COUNT(*) FROM members WHERE status='Active') AS active_members,
 (SELECT COUNT(*) FROM loans WHERE return_date IS NULL) AS active_loans,
 (SELECT COUNT(*) FROM overdue_books) AS overdue_loans,
 (SELECT COALESCE(SUM(fine),0) FROM loans) AS total_fines;

CREATE OR REPLACE VIEW category_summary AS
SELECT category,COUNT(*) AS title_count,
       SUM(total_copies) AS total_copies,
       SUM(available_copies) AS available_copies
FROM books GROUP BY category;

CREATE OR REPLACE VIEW popular_books AS
SELECT b.book_id,b.title,b.author,COUNT(l.loan_id) AS times_borrowed
FROM books b
LEFT JOIN loans l ON l.book_id=b.book_id
GROUP BY b.book_id,b.title,b.author;

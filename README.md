# 📚 Library Management Dashboard

A full-stack Library Management System built with **MySQL + Python/FastAPI + HTML/CSS/JavaScript**.

This is designed as a portfolio/GitHub project and demonstrates relational database design, REST APIs, business logic, CRUD operations, views, triggers, stored procedures, and a responsive dashboard.

## ✨ Features

- Dashboard KPI cards
- Books CRUD/search
- Members CRUD/search
- Issue and return books
- Automatic inventory updates
- Automatic overdue detection
- Fine calculation
- Overdue-books report
- Category report
- Most-borrowed-books report
- MySQL views
- MySQL triggers
- MySQL stored procedures
- FastAPI REST API
- Interactive API documentation
- Responsive vanilla JavaScript frontend

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Database | MySQL 8.0.16+ |
| Backend | Python 3.10+ / FastAPI |
| API server | Uvicorn |
| Frontend | HTML5 / CSS3 / JavaScript |
| Database driver | mysql-connector-python |
| Validation | Pydantic |
| Version control | Git / GitHub |

## 📁 Project Structure

```text
library-management-dashboard/
│
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── book.py
│   │   ├── member.py
│   │   └── loan.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── books.py
│   │   ├── dashboard.py
│   │   ├── loans.py
│   │   └── members.py
│   └── requirements.txt
│
├── frontend/
│   ├── index.html
│   ├── books.html
│   ├── members.html
│   ├── loans.html
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── dashboard.js
│       ├── books.js
│       ├── members.js
│       └── loans.js
│
├── sql/
│   └── library_management.sql
│
├── docs/
│   └── er-diagram.md
│
├── .env.example
├── .gitignore
├── README.md
└── LICENSE
```

## 🚀 Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/library-management-dashboard.git
cd library-management-dashboard
```

### 2. Create the MySQL database

Open MySQL Workbench and run:

```text
sql/library_management.sql
```

The script creates:

- `books`
- `members`
- `loans`
- views
- triggers
- stored procedures
- sample data

### 3. Create a Python virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r backend/requirements.txt
```

### 5. Configure MySQL

Copy:

```text
.env.example
```

to:

```text
.env
```

Then edit the values:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=library_management
```

**Do not commit `.env` to GitHub.** It is already ignored by `.gitignore`.

### 6. Start the application

From the project root:

```bash
uvicorn backend.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

The dashboard should load.

## 🔌 API Documentation

FastAPI automatically generates interactive documentation.

Open:

```text
http://127.0.0.1:8000/docs
```

Useful endpoints:

```text
GET    /api/health
GET    /api/dashboard/summary
GET    /api/dashboard/categories
GET    /api/dashboard/popular-books

GET    /api/books
POST   /api/books
GET    /api/books/{book_id}
PATCH  /api/books/{book_id}
DELETE /api/books/{book_id}

GET    /api/members
POST   /api/members
GET    /api/members/{member_id}
PATCH  /api/members/{member_id}

GET    /api/loans
GET    /api/loans/overdue
POST   /api/loans
POST   /api/loans/{loan_id}/return
```

## 📊 Dashboard

The dashboard displays:

- Book titles
- Total physical copies
- Available copies
- Active members
- Active loans
- Overdue loans
- Overdue books
- Most borrowed books
- Books by category

## 📚 Book Management

Books can be:

- searched
- added
- deleted when they have no loan history

The database prevents duplicate ISBNs.

## 👥 Member Management

Members can be:

- searched
- added
- activated
- deactivated

Member email addresses and member codes are unique.

## 🔄 Loan System

The issue-book workflow uses a stored procedure:

```sql
CALL issue_book(book_id, member_id, days);
```

The procedure checks:

1. The book exists.
2. A copy is available.
3. The member exists.
4. The member is active.
5. The member has fewer than five active loans.

The return workflow uses:

```sql
CALL return_book(loan_id);
```

The procedure:

- records the return date
- calculates the fine
- marks the loan as returned
- restores the available book count

The demonstration fine rate is:

```text
₹5 per overdue day
```

## ⚠️ Overdue Books

The main SQL view is:

```sql
SELECT *
FROM overdue_books
ORDER BY days_overdue DESC;
```

It automatically calculates:

```text
days_overdue = CURRENT_DATE - due_date
```

and:

```text
calculated_fine = days_overdue × ₹5
```

## 🧠 Database Concepts Demonstrated

### Constraints

- PRIMARY KEY
- FOREIGN KEY
- UNIQUE
- NOT NULL
- DEFAULT
- CHECK
- ENUM
- ON UPDATE CASCADE
- ON DELETE RESTRICT

### Views

- `available_books`
- `active_loans`
- `overdue_books`
- `dashboard_summary`
- `category_summary`
- `popular_books`

### Triggers

- Automatic loan-status calculation
- Automatic book inventory decrease
- Automatic book inventory restoration

### Stored Procedures

- `issue_book`
- `return_book`

### Indexes

Indexes are provided for common book, member and loan lookups.

## 🧪 Testing

Check the API:

```text
http://127.0.0.1:8000/api/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "library-management-api"
}
```

Check the database:

```sql
USE library_management;

SELECT * FROM dashboard_summary;

SELECT * FROM overdue_books;

SELECT * FROM active_loans;
```

## 🔐 Security Notes

This is a portfolio project rather than a production deployment.

For production, add:

- authentication
- role-based access
- HTTPS
- stricter CORS
- password hashing
- database secrets management
- request rate limiting
- audit logging
- automated tests

## 🔮 Future Improvements

Good next steps for version 2:

- React frontend
- JWT authentication
- Admin/librarian roles
- Book cover images
- Pagination
- Advanced filtering
- Email reminders for overdue books
- Docker Compose
- Unit/integration tests
- CI/CD with GitHub Actions
- Cloud deployment

## 📄 License

MIT License.

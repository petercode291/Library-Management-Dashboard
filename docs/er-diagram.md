# Entity Relationship Diagram

```mermaid
erDiagram
    BOOKS {
        INT book_id PK
        VARCHAR isbn UK
        VARCHAR title
        VARCHAR author
        VARCHAR category
        VARCHAR publisher
        YEAR publication_year
        INT total_copies
        INT available_copies
    }

    MEMBERS {
        INT member_id PK
        VARCHAR member_code UK
        VARCHAR first_name
        VARCHAR last_name
        VARCHAR email UK
        VARCHAR phone
        VARCHAR address
        DATE membership_date
        ENUM status
    }

    LOANS {
        INT loan_id PK
        INT book_id FK
        INT member_id FK
        DATE issue_date
        DATE due_date
        DATE return_date
        ENUM status
        DECIMAL fine
    }

    BOOKS ||--o{ LOANS : has
    MEMBERS ||--o{ LOANS : makes
```

## Relationships

- One book can have many loan records.
- One member can have many loan records.
- Each loan references exactly one book.
- Each loan references exactly one member.

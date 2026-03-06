# PostgreSQL vs MySQL: Complete Differences Reference

A comprehensive guide covering SQL clauses, queries, constraints, data types, transactions, and more — with examples and migration tips.

---

## Table of Contents

1. [Overview](#overview)
2. [PostgreSQL-Only Features](#postgresql-only-features)
3. [MySQL-Only Features](#mysql-only-features)
4. [Constraints & Index Differences](#constraints--index-differences)
5. [Data Types](#data-types)
6. [Transactions & Concurrency](#transactions--concurrency)
7. [Window Functions & CTEs](#window-functions--ctes)
8. [Views & Materialized Views](#views--materialized-views)
9. [Indexes (Advanced)](#indexes-advanced)
10. [Replication](#replication)
11. [Security & Row-Level Security](#security--row-level-security)
12. [String & Function Differences](#string--function-differences)
13. [Sequences & Identity](#sequences--identity)
14. [Migration Tips & Cheat Sheet](#migration-tips--cheat-sheet)

---

## Overview

PostgreSQL ("psql") and MySQL are both popular relational databases using SQL, but they support different SQL features and syntax.

| Category | PostgreSQL | MySQL |
|---|---|---|
| SQL Compliance | More ANSI-SQL compliant | Has proprietary extensions |
| Default Isolation | READ COMMITTED | REPEATABLE READ |
| DDL in Transactions | ✅ Supported | ❌ Auto-commits |
| JSON Binary Storage | ✅ JSONB | ❌ JSON only |
| Materialized Views | ✅ Supported | ❌ Not supported |
| Row-Level Security | ✅ Supported | ❌ Not supported |
| Full Outer Join | ✅ Native | ❌ Must emulate |
| INTERSECT / EXCEPT | ✅ Native | ⚠️ Experimental (8.0.40+) |

---

## PostgreSQL-Only Features

### 1. `RETURNING` Clause

Returns modified rows from `INSERT`, `UPDATE`, `DELETE`, or `MERGE` without a separate query.

```sql
-- PostgreSQL
INSERT INTO users (firstname, lastname)
VALUES ('Joe', 'Cool')
RETURNING id;

-- UPDATE with RETURNING
UPDATE users SET active = false WHERE id = 5
RETURNING id, active;

-- DELETE with RETURNING
DELETE FROM users WHERE id = 5
RETURNING *;
```

> ❌ MySQL has no `RETURNING`. Use `LAST_INSERT_ID()` or a follow-up `SELECT` instead.

---

### 2. `ON CONFLICT` (Upsert)

Handles unique-key conflicts during `INSERT`.

```sql
-- PostgreSQL
INSERT INTO customers (id, name) VALUES (1, 'Alice')
ON CONFLICT (id) DO UPDATE
  SET name = EXCLUDED.name;

-- Do nothing on conflict
INSERT INTO customers (id, name) VALUES (1, 'Alice')
ON CONFLICT (id) DO NOTHING;
```

> ❌ MySQL uses `ON DUPLICATE KEY UPDATE` instead (see MySQL-only section).

---

### 3. `ILIKE` (Case-Insensitive LIKE)

```sql
-- PostgreSQL
SELECT * FROM users WHERE name ILIKE '%smith%';
-- Matches: Smith, SMITH, smith, SmItH
```

> ❌ MySQL has no `ILIKE`. Use `LIKE` with a case-insensitive collation, or `LOWER(col) LIKE '%smith%'`.

---

### 4. `SIMILAR TO` (SQL-Standard Regex)

```sql
-- PostgreSQL
SELECT * FROM users WHERE name SIMILAR TO '(Alice|Bob)%';
```

> ❌ MySQL uses `REGEXP` / `RLIKE` instead.

---

### 5. `FULL OUTER JOIN`

```sql
-- PostgreSQL
SELECT a.id, b.id
FROM table_a a
FULL OUTER JOIN table_b b ON a.id = b.id;
```

> ❌ MySQL does not support `FULL OUTER JOIN`. Emulate with:
> ```sql
> SELECT * FROM a LEFT JOIN b ON a.id = b.id
> UNION
> SELECT * FROM a RIGHT JOIN b ON a.id = b.id;
> ```

---

### 6. `INTERSECT` and `EXCEPT`

```sql
-- PostgreSQL
SELECT a FROM table1
INTERSECT
SELECT a FROM table2;

SELECT a FROM table1
EXCEPT
SELECT a FROM table2;
```

> ❌ MySQL has no native `INTERSECT` or `EXCEPT` (experimental in MySQL 8.0.40). Simulate with `INNER JOIN` or subqueries.

---

### 7. Partial Indexes

Create indexes only on a subset of rows.

```sql
-- PostgreSQL
CREATE UNIQUE INDEX idx_active_users
ON users(email)
WHERE active = true;

-- Only active users are indexed — smaller, faster index
```

> ❌ MySQL does not support partial indexes through standard syntax.

---

### 8. `FILTER` on Aggregates

```sql
-- PostgreSQL
SELECT
  COUNT(*) FILTER (WHERE status = 'active')   AS active_count,
  COUNT(*) FILTER (WHERE status = 'inactive') AS inactive_count
FROM users;
```

> ❌ MySQL has no `FILTER`. Use `SUM(status = 'active')` or `CASE` expressions instead.

---

### 9. Writable CTEs

```sql
-- PostgreSQL: DELETE and INSERT in one atomic CTE
WITH moved_rows AS (
  DELETE FROM job_queue
  WHERE status = 'done'
  RETURNING *
)
INSERT INTO job_archive
SELECT * FROM moved_rows;
```

> ❌ MySQL CTEs are read-only — you cannot `INSERT`, `UPDATE`, or `DELETE` inside a CTE.

---

### 10. `CREATE INDEX CONCURRENTLY`

Build indexes on live tables without blocking writes.

```sql
-- PostgreSQL
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
-- No table lock — reads and writes proceed normally
```

> ❌ MySQL index builds lock the table (though `ALTER TABLE ... ALGORITHM=INPLACE` reduces this in some cases).

---

### 11. Materialized Views

Cache query results for fast repeated access.

```sql
-- PostgreSQL
CREATE MATERIALIZED VIEW sales_summary AS
SELECT region, SUM(amount) AS total
FROM sales
GROUP BY region;

-- Manually refresh the cache
REFRESH MATERIALIZED VIEW sales_summary;

-- Refresh without locking reads
REFRESH MATERIALIZED VIEW CONCURRENTLY sales_summary;
```

> ❌ MySQL has no materialized views. You must manually maintain a summary table.

---

### 12. Row-Level Security (RLS)

Enforce data access policies at the database level.

```sql
-- PostgreSQL
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

CREATE POLICY user_sees_own_orders ON orders
  USING (user_id = current_setting('app.current_user_id')::INT);

-- Now users can ONLY see their own rows, even with SELECT *
```

> ❌ MySQL has no row-level security. Must be enforced at the application level.

---

### 13. `UNLOGGED` Tables

Faster writes (no WAL logging), but data lost on crash.

```sql
-- PostgreSQL
CREATE UNLOGGED TABLE session_cache (
  session_id TEXT PRIMARY KEY,
  data JSONB,
  expires_at TIMESTAMPTZ
);
```

> ❌ No MySQL equivalent.

---

### 14. DDL Inside Transactions

```sql
-- PostgreSQL: schema changes are fully transactional
BEGIN;
ALTER TABLE users ADD COLUMN score INT DEFAULT 0;
CREATE INDEX idx_score ON users(score);
-- Something went wrong?
ROLLBACK; -- Both changes are fully undone ✅
```

> ❌ MySQL auto-commits DDL statements. `ROLLBACK` has no effect on `ALTER TABLE`, `CREATE INDEX`, etc.

---

## MySQL-Only Features

### 1. `AUTO_INCREMENT`

```sql
-- MySQL
CREATE TABLE animals (
  id   INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(30)
);
```

```sql
-- PostgreSQL equivalent (two options):
CREATE TABLE animals (
  id   SERIAL PRIMARY KEY,   -- Traditional
  name TEXT
);

-- Or modern standard:
CREATE TABLE animals (
  id   INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name TEXT
);
```

---

### 2. `ON DUPLICATE KEY UPDATE`

```sql
-- MySQL upsert
INSERT INTO products (id, name, price)
VALUES (1, 'Phone', 999)
ON DUPLICATE KEY UPDATE
  name  = VALUES(name),
  price = VALUES(price);
```

> PostgreSQL equivalent: `INSERT ... ON CONFLICT (id) DO UPDATE SET ...`

---

### 3. `REPLACE INTO`

Deletes the conflicting row and inserts a new one.

```sql
-- MySQL
REPLACE INTO products (id, name) VALUES (1, 'Tablet');
-- If id=1 exists: DELETE it, then INSERT
```

> ❌ No PostgreSQL equivalent. Use `ON CONFLICT DO UPDATE` instead.

---

### 4. `INSERT IGNORE`

```sql
-- MySQL: silently skips rows that cause errors
INSERT IGNORE INTO users (id, email)
VALUES (1, 'alice@example.com');
-- Duplicate? No error, just skipped.
```

> PostgreSQL equivalent: `INSERT ... ON CONFLICT DO NOTHING`

---

### 5. `SHOW` and `DESCRIBE` Commands

```sql
-- MySQL
SHOW TABLES;
SHOW DATABASES;
DESCRIBE users;
SHOW CREATE TABLE users;
SHOW INDEX FROM users;
USE mydb;
```

PostgreSQL uses system catalogs or `psql` meta-commands:

```sql
-- PostgreSQL psql equivalents
\dt              -- list tables
\d users         -- describe table
\l               -- list databases
\c mydb          -- connect to database
SELECT * FROM information_schema.tables;
```

---

### 6. `GROUP_CONCAT`

```sql
-- MySQL
SELECT dept, GROUP_CONCAT(name ORDER BY name SEPARATOR ', ') AS employees
FROM staff
GROUP BY dept;
```

```sql
-- PostgreSQL equivalent
SELECT dept, STRING_AGG(name, ', ' ORDER BY name) AS employees
FROM staff
GROUP BY dept;
```

---

### 7. Storage Engine Options

```sql
-- MySQL
CREATE TABLE logs (
  id   INT PRIMARY KEY AUTO_INCREMENT,
  msg  TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

> PostgreSQL has no storage engine concept — one unified storage engine.

---

### 8. `REGEXP` / `RLIKE`

```sql
-- MySQL
SELECT * FROM users WHERE email REGEXP '^[a-z]+@';
SELECT * FROM users WHERE email RLIKE '^[a-z]+@';  -- same thing
```

```sql
-- PostgreSQL equivalents
SELECT * FROM users WHERE email ~  '^[a-z]+@';   -- case-sensitive
SELECT * FROM users WHERE email ~* '^[a-z]+@';   -- case-insensitive
SELECT * FROM users WHERE email !~ '^[a-z]+@';   -- NOT match
```

---

### 9. Backtick Identifiers

```sql
-- MySQL (backticks for identifiers)
SELECT `first name`, `order` FROM `user table`;

-- PostgreSQL (double quotes per SQL standard)
SELECT "first name", "order" FROM "user table";
```

---

## Constraints & Index Differences

### Foreign Keys

```sql
-- PostgreSQL: inline REFERENCES is fully enforced ✅
CREATE TABLE orders (
  order_id    SERIAL PRIMARY KEY,
  customer_id INT REFERENCES customers(id) ON DELETE CASCADE
);

-- MySQL: inline REFERENCES is PARSED BUT IGNORED ❌
CREATE TABLE orders (
  order_id    INT PRIMARY KEY AUTO_INCREMENT,
  customer_id INT REFERENCES customers(id) ON DELETE CASCADE
  -- ⚠️ This FK is silently ignored in MySQL!
);

-- MySQL: must use explicit FOREIGN KEY clause ✅
CREATE TABLE orders (
  order_id    INT PRIMARY KEY AUTO_INCREMENT,
  customer_id INT,
  FOREIGN KEY (customer_id) REFERENCES customers(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);
```

---

### CHECK Constraints

```sql
-- PostgreSQL: always enforced ✅
CREATE TABLE employees (
  age INT CHECK (age >= 18),
  salary NUMERIC CHECK (salary > 0)
);

-- MySQL < 8.0.16: parsed but NOT enforced ❌
CREATE TABLE employees (
  age INT CHECK (age >= 18)
  -- CHECK is silently ignored — any age is accepted
);

-- MySQL >= 8.0.16: enforced ✅
-- Same syntax works, but verify your MySQL version
```

---

### Deferrable Constraints

```sql
-- PostgreSQL: constraints can be deferred to end of transaction
CREATE TABLE orders (
  order_id    SERIAL PRIMARY KEY,
  customer_id INT REFERENCES customers(id) DEFERRABLE INITIALLY DEFERRED
);

BEGIN;
INSERT INTO orders (customer_id) VALUES (999); -- customer 999 doesn't exist yet
INSERT INTO customers (id, name) VALUES (999, 'New Customer');
COMMIT; -- FK checked here, passes ✅
```

> ❌ MySQL checks foreign keys immediately — no deferrable constraint support.

---

### Exclusion Constraints (PostgreSQL only)

Prevent overlapping ranges or conflicting values.

```sql
-- PostgreSQL: no two rooms can be booked in the same period
CREATE TABLE room_bookings (
  room_id    INT,
  during     TSTZRANGE,
  EXCLUDE USING gist (room_id WITH =, during WITH &&)
);
```

> ❌ No MySQL equivalent.

---

### NULL Behavior in UNIQUE Constraints

Both PostgreSQL and MySQL allow multiple `NULL` values in a `UNIQUE` column (since `NULL ≠ NULL`).

```sql
-- Both databases: this is allowed
CREATE TABLE t (email VARCHAR(100) UNIQUE);
INSERT INTO t VALUES (NULL);
INSERT INTO t VALUES (NULL); -- ✅ both NULLs accepted
```

PostgreSQL 15+ adds `NULLS NOT DISTINCT` for stricter behavior:

```sql
-- PostgreSQL 15+: treat NULLs as equal in UNIQUE
CREATE UNIQUE INDEX idx ON t(email) NULLS NOT DISTINCT;
```

---

## Data Types

| Type / Use Case | PostgreSQL | MySQL |
|---|---|---|
| Auto-increment | `SERIAL` / `GENERATED AS IDENTITY` | `AUTO_INCREMENT` |
| Arrays | `INT[]`, `TEXT[]` (native) | ❌ Not supported |
| JSON (text) | `JSON` | `JSON` |
| JSON (binary, indexable) | `JSONB` | ❌ Not available |
| UUID | `UUID` (native type) | `VARCHAR(36)` or `BINARY(16)` |
| IP Address | `INET`, `CIDR` (native) | ❌ No native type |
| Boolean | `BOOLEAN` (`true`/`false`) | `TINYINT(1)` (0/1) |
| Custom Enum | `CREATE TYPE mood AS ENUM (...)` | `ENUM('val1','val2')` inline |
| Composite Types | `CREATE TYPE address AS (...)` | ❌ Not supported |
| Ranges | `INT4RANGE`, `TSTZRANGE`, etc. | ❌ Not supported |
| Large Text | `TEXT` (unlimited) | `TEXT` (64KB), `MEDIUMTEXT`, `LONGTEXT` |
| Geometric | Native geometry types | Requires spatial extensions |
| Currency | `MONEY` | `DECIMAL` |

### Array Example (PostgreSQL only)

```sql
-- PostgreSQL
CREATE TABLE products (
  id    SERIAL PRIMARY KEY,
  tags  TEXT[],
  scores INT[]
);

INSERT INTO products (tags, scores)
VALUES ('{electronics, sale}', '{95, 87, 92}');

-- Query: find products with 'sale' tag
SELECT * FROM products WHERE 'sale' = ANY(tags);

-- Append to array
UPDATE products SET tags = tags || '{new}' WHERE id = 1;
```

### JSONB Example (PostgreSQL only)

```sql
-- PostgreSQL JSONB: stored as binary, indexable
CREATE TABLE events (
  id      SERIAL PRIMARY KEY,
  payload JSONB
);

INSERT INTO events (payload)
VALUES ('{"user": "alice", "action": "login", "ip": "1.2.3.4"}');

-- Query nested keys efficiently
SELECT payload->>'user' AS username
FROM events
WHERE payload @> '{"action": "login"}';

-- Create a GIN index for fast JSONB queries
CREATE INDEX idx_events_payload ON events USING GIN(payload);
```

---

## Transactions & Concurrency

### Default Isolation Levels

| | PostgreSQL | MySQL (InnoDB) |
|---|---|---|
| Default | `READ COMMITTED` | `REPEATABLE READ` |
| Gap Locking | ❌ No | ✅ Yes (in REPEATABLE READ) |
| MVCC | ✅ Yes | ✅ Yes |

### DDL Transactionality

```sql
-- PostgreSQL: DDL is transactional ✅
BEGIN;
CREATE TABLE temp_import (id INT, data TEXT);
ALTER TABLE users ADD COLUMN verified BOOLEAN DEFAULT false;
-- Oops, something failed:
ROLLBACK;
-- Both the CREATE and ALTER are fully rolled back ✅

-- MySQL: DDL auto-commits ❌
BEGIN;
CREATE TABLE temp_import (id INT, data TEXT);  -- auto-commits here!
ROLLBACK;  -- table still exists, rollback had no effect
```

### Setting Isolation Level

```sql
-- Both databases support this syntax:
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
BEGIN;
-- ... your queries
COMMIT;
```

---

## Window Functions & CTEs

Both databases support window functions and CTEs, but with key differences.

### Writable CTEs (PostgreSQL only)

```sql
-- PostgreSQL: multi-step atomic operation
WITH
  deleted AS (
    DELETE FROM shopping_cart
    WHERE checked_out = true
    RETURNING *
  ),
  inserted AS (
    INSERT INTO order_history
    SELECT * FROM deleted
    RETURNING id
  )
SELECT COUNT(*) FROM inserted;
```

### Recursive CTEs

```sql
-- Both support RECURSIVE, but syntax is the same:
WITH RECURSIVE org_chart AS (
  -- Anchor: top-level employees
  SELECT id, name, manager_id, 1 AS level
  FROM employees
  WHERE manager_id IS NULL

  UNION ALL

  -- Recursive: subordinates
  SELECT e.id, e.name, e.manager_id, oc.level + 1
  FROM employees e
  JOIN org_chart oc ON e.manager_id = oc.id
)
SELECT * FROM org_chart ORDER BY level;
```

---

## Views & Materialized Views

### Regular Views (Both)

```sql
CREATE VIEW active_users AS
SELECT id, name, email
FROM users
WHERE active = true;
```

### Materialized Views (PostgreSQL only)

```sql
-- Create materialized view
CREATE MATERIALIZED VIEW monthly_revenue AS
SELECT
  DATE_TRUNC('month', order_date) AS month,
  SUM(total)                      AS revenue
FROM orders
GROUP BY 1
ORDER BY 1;

-- Query it (reads cached data — very fast)
SELECT * FROM monthly_revenue WHERE month >= '2024-01-01';

-- Refresh (update the cache)
REFRESH MATERIALIZED VIEW monthly_revenue;

-- Refresh without blocking reads (requires unique index)
CREATE UNIQUE INDEX ON monthly_revenue(month);
REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_revenue;
```

> 💡 Use materialized views for expensive aggregations, reports, and dashboards where slightly stale data is acceptable.

---

## Indexes (Advanced)

### Index Types

| Type | PostgreSQL | MySQL |
|---|---|---|
| B-tree (default) | ✅ | ✅ |
| Hash | ✅ | ✅ |
| GIN (full-text, arrays, JSONB) | ✅ | ❌ |
| GiST (geo, ranges, exclusion) | ✅ | ❌ |
| BRIN (time-series, large tables) | ✅ | ❌ |
| Full-text | ✅ (via GIN) | ✅ |
| Spatial | ✅ (via GiST) | ✅ (extensions) |
| Partial (WHERE clause) | ✅ | ❌ |
| Expression/Functional | ✅ | ✅ (MySQL 8.0+) |
| INCLUDE (covering) | ✅ | ⚠️ Partial support |
| Concurrent build (no lock) | ✅ | ❌ |

### Partial Index Example

```sql
-- PostgreSQL: index only unprocessed orders (much smaller index)
CREATE INDEX idx_pending_orders
ON orders(created_at)
WHERE status = 'pending';
```

### Expression Index Example

```sql
-- PostgreSQL
CREATE INDEX idx_lower_email ON users(LOWER(email));
-- Enables fast: WHERE LOWER(email) = 'alice@example.com'

-- MySQL 8.0+
CREATE INDEX idx_lower_email ON users((LOWER(email)));
-- Note the extra parentheses required in MySQL
```

### INCLUDE (Covering Index)

```sql
-- PostgreSQL: include extra columns to avoid table lookup
CREATE INDEX idx_orders_user ON orders(user_id)
INCLUDE (total, status);
-- Query for user_id, total, status never hits the table
```

---

## Replication

| Feature | PostgreSQL | MySQL |
|---|---|---|
| Physical replication | Streaming replication | Binary log replication |
| Logical replication | `CREATE PUBLICATION` / `SUBSCRIPTION` | Binary log (row-based) |
| Sync replication | `synchronous_standby_names` | Group Replication |
| Selective replication | ✅ (per table via logical replication) | ✅ (binlog filtering) |
| Built-in HA clustering | External (Patroni, etc.) | InnoDB Cluster built-in |

```sql
-- PostgreSQL logical replication
-- On publisher:
CREATE PUBLICATION my_pub FOR TABLE users, orders;

-- On subscriber:
CREATE SUBSCRIPTION my_sub
  CONNECTION 'host=primary dbname=mydb'
  PUBLICATION my_pub;
```

---

## Security & Row-Level Security

### Row-Level Security (PostgreSQL only)

```sql
-- Step 1: Enable RLS on the table
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Step 2: Create a policy
CREATE POLICY owner_policy ON documents
  FOR ALL
  USING (owner_id = current_setting('app.user_id')::INT);

-- Step 3: Set the user context in your app
SET app.user_id = '42';
SELECT * FROM documents;
-- Only returns rows where owner_id = 42, even with SELECT *
```

```sql
-- Multiple policies for different operations
CREATE POLICY read_policy ON documents
  FOR SELECT
  USING (is_public = true OR owner_id = current_setting('app.user_id')::INT);

CREATE POLICY write_policy ON documents
  FOR INSERT WITH CHECK (owner_id = current_setting('app.user_id')::INT);
```

> ❌ MySQL has no row-level security. All access control is at table/column level only.

---

## String & Function Differences

### Concatenation

```sql
-- PostgreSQL
SELECT 'Hello' || ' ' || 'World';        -- ✅ pipe operator
SELECT CONCAT('Hello', ' ', 'World');    -- ✅ also works

-- MySQL
SELECT CONCAT('Hello', ' ', 'World');    -- ✅ works
SELECT 'Hello' || ' ' || 'World';       -- ❌ means OR in MySQL!
```

### String Aggregation

```sql
-- PostgreSQL
SELECT dept, STRING_AGG(name, ', ' ORDER BY name) FROM staff GROUP BY dept;

-- MySQL
SELECT dept, GROUP_CONCAT(name ORDER BY name SEPARATOR ', ') FROM staff GROUP BY dept;
```

### Regex

```sql
-- PostgreSQL operators
WHERE col ~  'pattern'   -- case-sensitive match
WHERE col ~* 'pattern'   -- case-insensitive match
WHERE col !~ 'pattern'   -- case-sensitive NOT match
WHERE col !~* 'pattern'  -- case-insensitive NOT match

-- MySQL
WHERE col REGEXP 'pattern'          -- case-insensitive by default
WHERE col REGEXP BINARY 'pattern'   -- case-sensitive
WHERE col NOT REGEXP 'pattern'
```

### Case Sensitivity (Default Behavior)

```sql
-- PostgreSQL: case-SENSITIVE by default
SELECT * FROM users WHERE name = 'Alice';  -- won't match 'alice'

-- Use ILIKE or LOWER() for case-insensitive search:
SELECT * FROM users WHERE name ILIKE 'alice';
SELECT * FROM users WHERE LOWER(name) = 'alice';

-- MySQL: case-INSENSITIVE by default (depends on collation)
SELECT * FROM users WHERE name = 'Alice';  -- matches 'alice', 'ALICE', etc.
```

### Common Function Equivalents

| Purpose | PostgreSQL | MySQL |
|---|---|---|
| Current timestamp | `NOW()` / `CURRENT_TIMESTAMP` | `NOW()` / `CURRENT_TIMESTAMP` |
| String length | `LENGTH()` / `CHAR_LENGTH()` | `LENGTH()` (bytes) / `CHAR_LENGTH()` (chars) |
| Substring | `SUBSTRING(s, 1, 3)` | `SUBSTRING(s, 1, 3)` |
| String repeat | `REPEAT(str, n)` | `REPEAT(str, n)` |
| Random | `RANDOM()` (0–1) | `RAND()` (0–1) |
| Integer division | `DIV` or `/` with cast | `DIV` |
| Modulo | `%` or `MOD()` | `%` or `MOD()` |
| Conditional | `CASE` / `COALESCE` / `NULLIF` | `CASE` / `COALESCE` / `NULLIF` / `IF()` |
| Null-safe compare | `IS NOT DISTINCT FROM` | `<=>` |
| Type casting | `CAST(x AS INT)` or `x::INT` | `CAST(x AS SIGNED)` |
| Epoch to timestamp | `TO_TIMESTAMP(epoch)` | `FROM_UNIXTIME(epoch)` |

---

## Sequences & Identity

### PostgreSQL: Standalone Sequences

```sql
-- Create a standalone sequence (sharable across tables)
CREATE SEQUENCE order_number_seq
  START WITH 10000
  INCREMENT BY 1
  NO MAXVALUE
  CACHE 10;

-- Use in multiple tables or contexts
INSERT INTO orders (order_num) VALUES (NEXTVAL('order_number_seq'));
INSERT INTO invoices (inv_num) VALUES (NEXTVAL('order_number_seq'));

-- Check current value
SELECT CURRVAL('order_number_seq');
SELECT LASTVAL(); -- last used in current session
```

```sql
-- Modern identity columns (SQL standard, PostgreSQL 10+)
CREATE TABLE invoices (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  amount NUMERIC
);
```

### MySQL: Table-Bound AUTO_INCREMENT

```sql
-- MySQL AUTO_INCREMENT is always tied to one specific table
CREATE TABLE orders (
  id INT PRIMARY KEY AUTO_INCREMENT
);

-- Check current value
SELECT AUTO_INCREMENT
FROM information_schema.TABLES
WHERE TABLE_NAME = 'orders';

-- Reset the counter
ALTER TABLE orders AUTO_INCREMENT = 1000;
```

---

## Migration Tips & Cheat Sheet

### Common Syntax Conversions

| Task | PostgreSQL | MySQL |
|---|---|---|
| Upsert | `INSERT ... ON CONFLICT DO UPDATE` | `INSERT ... ON DUPLICATE KEY UPDATE` |
| Skip on conflict | `ON CONFLICT DO NOTHING` | `INSERT IGNORE` |
| Get inserted ID | `INSERT ... RETURNING id` | `LAST_INSERT_ID()` |
| Case-insensitive search | `ILIKE` | `LIKE` (with ci collation) |
| Concatenate strings | `\|\|` or `CONCAT()` | `CONCAT()` |
| Regex match | `~` / `~*` | `REGEXP` / `RLIKE` |
| Aggregate strings | `STRING_AGG()` | `GROUP_CONCAT()` |
| Auto-increment | `SERIAL` / `IDENTITY` | `AUTO_INCREMENT` |
| Full outer join | Native | Emulate with `UNION` |
| Intersect | `INTERSECT` | Emulate with `INNER JOIN` |
| Set difference | `EXCEPT` | Emulate with `NOT IN` / `LEFT JOIN` |

### Full Outer Join Emulation for MySQL

```sql
-- PostgreSQL (native)
SELECT * FROM a FULL OUTER JOIN b ON a.id = b.id;

-- MySQL (emulated)
SELECT * FROM a LEFT  JOIN b ON a.id = b.id
UNION
SELECT * FROM a RIGHT JOIN b ON a.id = b.id;
```

### INTERSECT Emulation for MySQL

```sql
-- PostgreSQL
SELECT city FROM customers
INTERSECT
SELECT city FROM suppliers;

-- MySQL equivalent
SELECT DISTINCT city FROM customers
WHERE city IN (SELECT city FROM suppliers);
```

### EXCEPT Emulation for MySQL

```sql
-- PostgreSQL
SELECT city FROM customers
EXCEPT
SELECT city FROM suppliers;

-- MySQL equivalent
SELECT DISTINCT city FROM customers
WHERE city NOT IN (SELECT city FROM suppliers);

-- Or with LEFT JOIN (handles NULLs better)
SELECT DISTINCT c.city
FROM customers c
LEFT JOIN suppliers s ON c.city = s.city
WHERE s.city IS NULL;
```

### Foreign Key — Safe Pattern for Both

```sql
-- Always use explicit FOREIGN KEY clause (works correctly in both)
CREATE TABLE orders (
  order_id    INT         PRIMARY KEY,  -- use AUTO_INCREMENT for MySQL, SERIAL for PostgreSQL
  customer_id INT         NOT NULL,
  FOREIGN KEY (customer_id) REFERENCES customers(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);
```

### CHECK Constraints — Safe Pattern

```sql
-- Works in PostgreSQL always, MySQL 8.0.16+
CREATE TABLE products (
  price NUMERIC CHECK (price >= 0),
  stock INT   CHECK (stock >= 0)
);

-- For older MySQL: use a trigger instead
DELIMITER //
CREATE TRIGGER check_price_before_insert
BEFORE INSERT ON products
FOR EACH ROW
BEGIN
  IF NEW.price < 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Price cannot be negative';
  END IF;
END; //
DELIMITER ;
```

---

## Quick Reference Summary

### Features Unique to PostgreSQL
- `RETURNING` clause
- `ON CONFLICT` upsert syntax
- `ILIKE` operator
- `FULL OUTER JOIN` (native)
- `INTERSECT` / `EXCEPT` (native)
- Partial indexes (`WHERE` on index)
- `FILTER` on aggregates
- Writable CTEs
- `CREATE INDEX CONCURRENTLY`
- Materialized views
- Row-level security
- DDL transactions (rollbackable schema changes)
- `UNLOGGED` tables
- Native arrays, JSONB, UUID, INET/CIDR, range types
- Deferrable constraints
- Exclusion constraints
- Standalone sequences
- GIN, GiST, BRIN index types

### Features Unique to MySQL
- `AUTO_INCREMENT`
- `ON DUPLICATE KEY UPDATE`
- `REPLACE INTO`
- `INSERT IGNORE`
- `SHOW` / `DESCRIBE` / `USE` commands
- `GROUP_CONCAT()`
- `REGEXP` / `RLIKE` operators
- Backtick identifiers
- Storage engine options (`ENGINE=InnoDB`)
- `<=>` null-safe equality operator
- `IF()` function

---

*This document covers PostgreSQL 15+ and MySQL 8.0+. Some features differ in older versions — always verify against your specific database version.*
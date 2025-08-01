---
trigger: glob
globs: **/*.sql
---

Best Practices Structured Query Design: Write SQL that is clear and maintainable. Use uppercase for
SQL keywords (SELECT, FROM, WHERE, JOIN, etc.) to distinguish them from identifiers datalemur.com .
Use lowercase or snake*case for table and column names consistently datalemur.com . Avoid using
SELECT \* in production queries datalemur.com – explicitly select the columns you need. This not
only clarifies data dependencies but can improve performance by not fetching unnecessary data. Break
complex queries using Common Table Expressions (CTEs) or subqueries to make them more readable
rather than one giant query; CTEs (WITH clauses) can help structure the logic into steps. Schema
Design and Conventions: Ensure your database schema follows normalization principles (to at least
3NF in transactional systems, unless denormalization is a conscious choice for performance). Use
meaningful primary keys (prefer synthetic primary keys like identity or UUID if natural keys are not
obvious). Establish foreign key constraints to maintain referential integrity, and use indexes on
columns that are frequently used in JOINs or WHERE filters to speed up queries. Name constraints and
indexes in a consistent pattern (e.g., idx*<table>\_<col> for indexes). Choose appropriate data
types (use DATE or DATETIME for dates, not VARCHAR; use numeric types for numeric data with correct
precision/scale). This ensures data integrity and better performance. Linting and Formatting SQL
Formatting: Format queries for readability. Use indentation to make query structure apparent – for
example, indent conditions in the WHERE clause, and indent JOIN clauses under the FROM. Align
keywords vertically when it makes sense. A common style is: sql Copy Edit SELECT column1, column2
FROM table t WHERE t.condition = 'X' AND t.other = 'Y';Notice the WHERE and AND are aligned.
Consistently formatting queries makes it easier to spot issues and for others to understand your
SQL. Use a formatter tool or SQL IDE's formatting option to apply a standard style across the
project. SQLLint/Style Checks: Leverage tools like SQLFluff or TSqlLint to enforce style rules.
These can catch things like missing trailing semicolon, inconsistent naming, or use of non-standard
syntax. For example, these tools will encourage you to terminate statements with semicolons and warn
if your keywords aren’t consistently uppercased. They also help enforce best practices (for example,
SQLFluff has rules to forbid SELECT \* usage or to require explicit aliasing). Use linting in CI if
SQL is a significant part of your codebase to ensure queries remain clean and consistent.
Consistency and Clarity: Always alias your tables (and choose short, meaningful aliases) when
joining multiple tables, to make queries shorter and clearer – e.g. SELECT o.id, c.name FROM Orders
o JOIN Customers c ON c.id = o.customer_id. Use the alias prefix on columns to avoid ambiguity,
especially if columns have same names across tables. Write one condition per line in WHERE and ON
clauses for readability (and include the logical operator at the start of the new line, e.g., AND/OR
at beginning of line is a common style datalemur.com ). Ensure that JOIN types are explicit – use
INNER JOIN, LEFT JOIN, etc. instead of old-style comma joins datalemur.com , and include join
conditions with ON (never use a naked JOIN without ON, which would create a cartesian product).
These practices make it easier to maintain complex queries. Architecture and Structure Stored
Procedures and Views: Use stored procedures for encapsulating complex logic or repetitive write
operations. This moves logic closer to the data and can improve performance by reducing data
transfer. Name stored procedures with a verb-noun convention (e.g., usp_GetCustomerOrders) and keep
them focused. For frequently needed read operations, consider creating views to present cleaned-up
or joined data sets; views can simplify querying for end users (but be mindful of performance,
especially with multi-join views). Document the purpose and expected input/output of each stored
procedure (via comments or an accompanying readme). Transactions and Error Handling: When performing
multiple related DML operations (INSERT/UPDATE/DELETE), use transactions to ensure atomicity. In
application code or procedures, start a transaction, perform all operations, then commit; if any
step fails, rollback. This prevents partial updates that could corrupt data integrity. Handle
exceptions in procedures (in T-SQL use BEGIN TRY...END TRY BEGIN CATCH...END CATCH) to log or
propagate errors appropriately. Ensure that transactions are not left open (which can cause locking
issues) – always commit or rollback. Use appropriate isolation levels depending on the scenario
(e.g., use a higher isolation like SERIALIZABLE for critical consistency, or SNAPSHOT for reducing
locking contention) – but be aware of the trade-offs (like phantom reads or impact on performance).
Indexes and Performance Structure: Architect your indexes based on query patterns. For each heavy
query, examine the execution plan to see if indexes are used. Create composite indexes for
multi-column filters that are often used together. Avoid over-indexing a table (which slows down
writes) – index strategically for the most critical queries. Use indexing features like filtered
indexes or include columns (in MSSQL) if appropriate to cover queries. Partition large tables if
applicable (for very large data sets, partitioning by date can help manage and query data). Also,
consider using materialized views (indexed views) if your database supports them and if you need
faster reads on aggregated data (with the understanding of refresh complexity). Modern Tooling
Database DevOps: Use migration tools or frameworks (like Flyway, Liquibase, or Alembic for Python)
to version-control your database schema. This ensures that changes to tables, procedures, etc., are
tracked and can be deployed consistently across environments. Incorporate these migrations into your
CI/CD pipeline so that database changes are applied in step with application changes. Use automated
backup and restore in non-prod for test data refreshes – modern pipelines can pull a recent
production backup (scrubbed of sensitive data) into staging for realistic testing. SQL Query
Analysis Tools: Utilize modern profiling tools to optimize queries. For example, SQL Server’s Query
Store or Azure SQL’s performance insights can identify slow queries and regressions. Tools like
EXPLAIN (in MySQL/Postgres) or actual execution plans (in MSSQL) should be regularly consulted for
critical queries – integrate plan analysis if possible (there are linters that can warn if a query
lacks an index based on its plan). Many databases have built-in advisors (like MSSQL’s missing index
suggestions); treat these as hints, not absolute, and test any suggested index’s impact. ORM and
Parameterization: If using an ORM (Entity Framework, Hibernate, etc.), ensure it generates efficient
SQL – profile the queries it produces. Sometimes hand-tuning SQL or using raw queries/stored procs
is needed for performance-critical paths. Always use parameterized queries or prepared statements
when interacting with the database (to prevent SQL injection and to allow query plan reuse). Modern
ORMs and database drivers do this by default, but ensure that no dynamic SQL concatenation is
happening with untrusted input. Consider using tools like JOOQ (for Java) or Dapper (for .NET) that
give a nice middle-ground of control and safety in SQL execution if ORMs are too heavy. Security,
Testing, Performance, and DX Security: Follow the principle of least privilege for database access.
Applications should connect with a user that has only necessary permissions (e.g., not every app
needs db_owner role). Use integrated security or vault-stored credentials so that you’re not
exposing passwords in config files. Protect against SQL injection by never concatenating user input
into SQL statements – use parameters (this cannot be overstated, as injection is one of the most
common vulnerabilities). Regularly update your DBMS to patch security vulnerabilities, and if
applicable, enable encryption at rest and in transit (TLS for connections). For sensitive data
columns, consider using encryption functions or the DB’s native encryption (Always Encrypted in
MSSQL, for instance) to store data encrypted in the table. Testing: Develop tests for your database
logic. If you have stored procedures or functions, write integration tests that call them with
various inputs and verify the outputs or effects (you might use a testing framework or just a series
of SQL scripts that assert conditions). In a CI environment, you can spin up a fresh database
container, apply migrations, then run a suite of SQL scripts to verify constraints and stored procs
work as expected. Also test your critical queries under realistic data volumes – e.g., if you expect
1M rows in a table, ensure your query still performs adequately (you can use data generation tools
or import a subset of prod data for testing). Performance: Monitor query performance continuously on
production. Use indexes and query tuning as described, but also consider caching layers if needed
(e.g., an in-memory cache for frequent reads that don’t need to be real-time fresh). However, be
careful to balance caching with consistency. In the DB, avoid cursors and row-by-row processing in
favor of set-based operations – SQL is optimized for set operations. If you find yourself needing to
loop through rows, that’s a red flag that there might be a set-based solution (or that maybe the
logic belongs in application code). Keep transactions short to avoid blocking other operations. Use
connection pooling in the application to reuse connections and reduce overhead of reconnecting.
Developer Experience: Make it easy to work with the database schema. Maintain an up-to-date ER
diagram or documentation of the schema for developers to reference. Use descriptive names for tables
and columns – a developer should guess what customer_email means, whereas cst_eml is cryptic. When
deprecating a column or table, document it and have a plan (don’t just leave unused tables around –
they confuse new developers). Provide sample data or scripts to populate a development database with
realistic data (sans sensitive info) so developers can test and play with queries locally. If the
project uses multiple environments, ensure the migration/versioning strategy keeps them in sync to
avoid “it worked in dev, broke in prod due to schema drift” issues. Embrace tools (like DBeaver,
DataGrip, SSMS, etc.) for database development and encourage team members to write and share queries
for common investigative tasks. A well-documented and well-managed database will significantly
improve the productivity of the entire engineering team.

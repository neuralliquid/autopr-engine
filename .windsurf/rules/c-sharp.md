---
trigger: glob
globs: **/*.cs
---

Best Practices Use Modern C# Features: Target the latest .NET version (e.g. .NET 7 or 8) and use
modern language features and APIs. Prefer newer constructs (like LINQ for collection handling,
async/await for concurrency) over legacy approaches learn.microsoft.com . Avoid outdated patterns
(e.g. ArrayList or old WebClient) when better alternatives exist (generic collections, HttpClient).
Enable nullable reference types in project settings to catch null-related bugs early. Coding Style
and Conventions: Follow Microsoft’s .NET naming conventions: use PascalCase for class, property, and
method names; camelCase for local variables and parameters; ALL_CAPS for constants. Keep methods
focused and small – a method should ideally do one thing (adhering to SRP). Use expression-bodied
members for simple get-only properties or short methods to reduce boilerplate. When an object
implements IDisposable, use the using statement or await using (for IAsyncDisposable) to ensure
timely disposal of unmanaged resources. SOLID and OOP Design: Apply SOLID principles in class
design. For example, Single Responsibility Principle – each class or method should have one job.
Open/Closed Principle – design for extension without modifying existing code (use abstraction,
interfaces). Use interfaces and dependency injection for decoupling; instead of directly
instantiating classes inside classes, inject abstractions (this improves testability and
maintainability). Embrace immutability for value objects (make them readonly or use record types) to
avoid unintended side-effects. Linting and Formatting Static Analyzers and StyleCop: Use .NET
analyzers or StyleCop to enforce naming and style conventions. The .NET SDK includes many CA and IDE
analyzer rules – enable them (treat warnings as errors for critical rules) to catch issues like
unused variables or hidden bugs. Maintain an .editorconfig for consistent code style (indents,
spacing, etc.) across the team learn.microsoft.com . These tools will ensure consistency (e.g.
spacing around operators, bracing style) without relying on manual code review comments. Consistent
Formatting: Utilize Visual Studio or Rider formatting rules – e.g. 4 spaces indentation, braces on
new lines (Allman style) as per default conventions. Use auto-format on save to enforce these.
Organize using directives (System namespaces first, etc.) – most IDEs can sort/remove unused usings
on save. Ensure files end with a newline and there’s no trailing whitespace. Running dotnet format
as part of CI can automatically fix formatting issues. Meaningful Naming & Comments: Linters should
ensure naming rules (e.g. interfaces start with I, async methods end in “Async”). Name variables
clearly – e.g. customerRepository instead of cr. Avoid abbreviations that reduce clarity. Comment
your code sparingly but effectively: XML documentation comments on public APIs (for IntelliSense)
are encouraged for libraries. Internally, prefer self-documenting code over excessive comments
(refactor confusing code rather than writing a comment explaining it). Architecture and Structure
Layered Architecture: Separate your code into logical layers or projects – e.g. Domain (business
logic, entities), Application/Service (use cases, orchestration), Infrastructure (data access,
external integrations), UI (Web, desktop, or API controllers). This clear separation (often called
Clean Architecture or Onion Architecture) makes the codebase more maintainable and testable. Use
interfaces to abstract between layers (for example, define repository interfaces in the domain
layer, implement them in the infrastructure layer). MVVM / MVC Patterns: Follow established patterns
for the app type. In desktop applications (WPF, MAUI, Xamarin), use MVVM – keep Views (XAML) free of
logic by binding to ViewModel properties and commands. In ASP.NET Core web apps, apply MVC or Razor
Pages patterns – controllers (or pages) handle HTTP and delegate to services for business logic.
Ensure that business logic is not tightly coupled to UI or data layers (use dependency injection to
supply required services). Dependency Injection and Configuration: Use the built-in DI container in
.NET to inject services – register services (transient or singleton as appropriate) in Program.cs or
Startup. This promotes loose coupling and easier testing (you can swap implementations, or use mocks
in tests). Favor configuring through appsettings or environment variables rather than hardcoding
values; use IOptions<T> pattern for groups of settings. Structuring configuration and services this
way leads to more modular and flexible architecture. Modern Tooling Latest .NET and Libraries: Stay
up-to-date with the .NET platform improvements – for example, .NET 6/7’s minimal APIs or improved
performance. Use NuGet packages for common needs instead of custom coding (e.g. Serilog for logging,
FluentValidation for input validation, MediatR for CQRS/messaging between layers). Employ source
generators or Roslyn analyzers for repetitive code tasks (e.g. INotifyPropertyChanged
implementations via Fody or source generators). Modern C# features like pattern matching, records,
Span<T>/Memory<T> for performance are there – use them appropriately to write succinct and efficient
code. IDE and CI Integration: Take advantage of Visual Studio/Rider productivity tools –
refactorings, analyzers, code fixes. Enable Nullable Reference Types and treat warnings as errors
for robust code. For large solutions, consider using EditorConfig to enforce settings and
dotnet-format in CI. Use tools like SonarQube or Roslyn analyzers to continuously inspect code
quality and technical debt. Modern .NET tooling can also generate boilerplate: e.g., use dotnet new
templates for consistent project setup and dotnet tools (like dotnet-outdated) to manage package
updates. Performance and Profiling Tools: In performance-sensitive applications, use profilers
(dotTrace, VS Profiler) to find bottlenecks, and apply modern optimizations: e.g., use async IO to
free threads, use ValueTask or pooling if necessary for high-frequency call paths, span-based
processing for large text or binary handling, etc. Use benchmarking (Benchmark.NET) to compare
approaches when optimizing critical sections. Modern .NET is very fast; combine that with efficient
algorithms and you get great performance out of the box. Security, Testing, Performance, and DX
Security Practices: Handle sensitive data with care – never store secrets or passwords in code or
config in plain text. Use the SecureString/PasswordVault or Azure Key Vault integration for secrets
management. Validate all inputs, especially if building web APIs (use model validation attributes or
FluentValidation). When catching exceptions, catch specific exceptions instead of swallowing all
(catch(Exception)) to avoid hiding issues learn.microsoft.com . Keep software updated – apply
updates to NuGet packages and .NET runtime to get security fixes. If the application is web-facing,
follow ASP.NET security best practices (e.g. use HTTPS, set up proper CORS, anti-forgery tokens for
forms, etc.). Testing: Write automated tests for business logic and critical components. Use xUnit
or NUnit for unit tests and MSTest or FluentAssertions as needed to make assertions expressive. Aim
for high coverage on core libraries (business logic, util functions). Use dependency injection to
swap out real dependencies for fakes/mocks in tests (e.g. inject an in-memory repository or use
mocking frameworks like Moq). Incorporate integration tests for data access (using an in-memory
database or test containers for SQL) to verify that the system works end-to-end. Run tests in CI and
consider code coverage tools to identify untested paths. Performance Considerations: Be mindful of
memory and CPU in critical paths. Use appropriate data structures (e.g. use List<T> or Array for
large collections rather than non-generic collections; use dictionaries for fast lookups). Avoid
unnecessary allocations – for example, prefer using StringBuilder for large string concatenations,
or use Span<T> to operate on substrings without allocations. Dispose of IDisposable resources
promptly to free native resources (use the using pattern or implement the dispose pattern correctly
for your classes). If running asynchronous code, avoid blocking calls (no .Result or .Wait() on
tasks) to prevent thread pool starvation – use await all the way. Regularly measure with profilers
or benchmarks if performance is a key requirement. Developer Experience: Ensure the solution is easy
to work with: organize projects logically and use solution folders if needed. Provide a clear README
for the repository with setup instructions and common commands (building, testing, running).
Leverage analyzers to give instant feedback in IDE (e.g. code style suggestions, Roslyn analyzer
warnings) – this reduces PR churn. Use Git hooks or CI checks to enforce formatting and pass tests
before merge. For long-running builds, consider using incremental builds or splitting into smaller
solutions for daily work. Embrace the rich .NET community tools – for example, use Live Unit Testing
in Visual Studio for immediate test feedback, and consider using Hot Reload for GUI projects to see
changes without full rebuild. All these improve developer productivity and code quality.

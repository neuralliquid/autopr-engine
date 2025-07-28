---
trigger: glob
globs: **/*.ps1, **/*.psm1, **/*.pst1
---

Best Practices
Cmdlet Design & Naming: Follow PowerShell’s standard verbs – use approved verbs for function/cmdlet names
(Get/Set/New/Remove, etc.) rather than ad-hoc names
learn.microsoft.com
. Use singular nouns for cmdlet names (e.g. Get-User not Get-Users) to align with conventions. Functions should be
defined with a proper param block and support common parameters if needed. Avoid using aliases in scripts; always use
full cmdlet names for clarity and reliability
learn.microsoft.com
.
Scripting Practices: Enable strict mode (Set-StrictMode -Version Latest) at the top of scripts to catch undefined variables and other issues early. Place Param(...) at the top for any script parameters and define types for parameters (including [switch] for flags). Use Pipeline where appropriate – design functions to take pipeline input (using Process block or value from pipeline) for flexibility. However, avoid excessively long pipeline chains in one line; break into readable steps or use intermediate variables for clarity.
Linting and Formatting
PSScriptAnalyzer: Use PSScriptAnalyzer to statically check your PowerShell code for style and best practices. It will
warn against common pitfalls like using aliases (% instead of ForEach-Object)
learn.microsoft.com
, or missing ShouldProcess. Address PSScriptAnalyzer warnings, e.g. add SupportsShouldProcess=$true for functions that
perform changes, so users can run with -WhatIf safely
learn.microsoft.com
. Also configure it to catch formatting issues (like inconsistent indentation).
Readable Formatting: Indent two or four spaces consistently (two is common in PS). Align pipeline characters |
vertically if a command is split across lines, and use line breaks after each pipeline segment to improve readability.
Use syntax coloring (in editors like VS Code) to your advantage – for example, quote strings properly so they appear as
strings. Write one logical command per line; if a line is too long, use backticks sparingly or, better, use splatting
(@params) or sub-expressions to wrap lines. Add comments on separate lines (prefaced with #), not at end-of-line after
code, for better clarity.
Architecture and Structure
Modularization: For larger scripts or toolkits, organize code into functions and modules. Encapsulate reusable logic in
functions with clear names, and group related functions into a module (.psm1) so they can be imported and shared. Avoid
sprawling one-file scripts with global variables (PowerShell global state can lead to hard-to-track bugs)
learn.microsoft.com
. Instead, return data from functions (objects or hashtables) and have calling code consume those outputs.
Error Handling: Use try { ... } catch { ... } finally { ... } blocks to handle exceptions as needed, but avoid empty
catch blocks that swallow errors
learn.microsoft.com
. In catch, use Write-Error $_ or rethrow (throw) after logging, unless you have a specific recovery. Utilize
$ErrorActionPreference = 'Stop' or the -ErrorAction Stop on cmdlets to make non-terminating errors act as terminating
within try/catch. For expected errors, consider handling via conditions or checking return values (like $? or checking
$LASTEXITCODE for external commands).
Logging and Output: Distinguish between output meant for end-users vs. output meant for pipelines. Use Write-Output (or
just output values) for pipeline data, and Write-Verbose, Write-Warning, Write-Error for messaging. Avoid using
Write-Host unless absolutely necessary for host-only output
learn.microsoft.com
 (since it writes directly to console and not to any stream). Structure scripts with an explicit Main process (if
 complex): parse params, perform actions, output results; this improves clarity especially if someone needs to read or
 modify the script.
Modern Tooling
Latest PowerShell & Modules: Use PowerShell 7+ (PowerShell Core) for modern script development – it offers better
performance and is cross-platform. Leverage modules (from PSGallery or internal repositories) rather than writing
everything from scratch – e.g. use Azure Az modules for Azure tasks, or Pester for testing. Keep modules updated and
import them via Import-Module with required version if necessary.
Pester Testing: Incorporate Pester tests for your PowerShell functions, especially for modules. Write unit tests that
call your functions with sample inputs and verify expected outputs. This not only guards against regressions but also
serves as usage examples. You can automate running Pester in CI pipelines to ensure your scripts continue to work as
expected after changes.
Dev Experience: Use Visual Studio Code with the PowerShell extension for an improved experience – it provides
IntelliSense, inline help, and integrates PSScriptAnalyzer and Pester test runner. Leverage snippets or templates for
new scripts (to include things like param blocks, comment help, etc.). For example, ensure every function has
comment-based help with .SYNOPSIS, .DESCRIPTION, etc., so running Get-Help YourFunction shows useful info
learn.microsoft.com
. This makes your scripts feel professional and is considered a best practice in PowerShell scripting.
Security, Testing, Performance, and DX
Security: Avoid hardcoding credentials or sensitive information in scripts. If credentials are needed, use
Get-Credential to prompt for them, or secure them using the built-in Credential object (PSCredential) rather than
plaintext user/password parameters
learn.microsoft.com
. If you must store a password, use ConvertTo-SecureString and store the secure string (or better, use a secret
management module). Be careful with Invoke-Expression – it can lead to security issues; prefer safer alternatives or at
least validate inputs heavily if you must use it
learn.microsoft.com
. Also, sign your scripts (or dot-sourced ps1 files) in environments that require execution policy compliance – this
ensures integrity.
Testing: In addition to Pester unit tests, do integration testing of your scripts in a safe environment. For example,
if a script modifies system state (like AD user creation or VM deployment), test those portions against a test
environment or with -WhatIf to ensure they perform as expected. Always support -WhatIf and -Confirm in functions that
make changes to allow dry-runs
learn.microsoft.com
. Review usage of common parameters to ensure your script plays nicely with pipeline input, -Verbose, and -ErrorAction.
Performance: PowerShell is powerful but can be slower than C# for heavy tasks; mitigate this by using pipeline
efficiently and native cmdlets where possible (they’re usually faster in C++). Avoid needless loops over large data
when a cmdlet can do the work (for example, use Measure-Object for sums or Where-Object with filters instead of manual
accumulating in a loop). When dealing with very large datasets, consider moving some logic to .NET (C#) via Add-Type or
inline C# for speed, or use parallelism (PowerShell 7’s ForEach-Object -Parallel or Start-Job/ThreadJob for
concurrency). Also, prefer filtering early in the pipeline to reduce the amount of objects processed downstream.
Developer Experience: Make your script self-documenting and user-friendly. Provide clear help and usage examples in comment-based help. Use parameter validation ([ValidateRange()], [ValidateSet()], etc.) to catch incorrect usage automatically and give helpful errors. For long-running scripts, output status updates or use Write-Progress to show progress to the user. In source control, treat your PowerShell like code – do code reviews for scripts, and use tools like GitHub Actions or Azure DevOps pipelines to run linting and tests on your PowerShell code. Adhering to these practices will make working on PowerShell code in a team more pleasant and error-free.

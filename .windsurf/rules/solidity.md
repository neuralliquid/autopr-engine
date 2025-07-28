---
trigger: glob
globs: **/*.sol
---

Best Practices
Compiler Version and Pragmas: Specify a fixed pragma or narrow range for Solidity compiler (e.g. pragma solidity
0.8.19;) – do not use overly broad ^ for production contracts, as it could compile with unintended future versions. Always use the latest stable compiler version for new contracts
moldstud.com
, as updates include important security fixes and improvements. Include an SPDX license identifier at the top of each
file (e.g. // SPDX-License-Identifier: MIT).
Secure Contract Patterns: Follow known secure patterns. Use Checks-Effects-Interactions for state-changing functions:
first validate inputs and preconditions, then update state, and only then interact with external contracts (calls) to
minimize reentrancy risk
dev.to
. When calling external contracts, prefer using function calls with return checks or the low-level call with proper
boolean check on result and a fixed gas stipend. Include reentrancy guards (nonReentrant from OpenZeppelin’s
ReentrancyGuard) on functions that modify state and then call external contracts as an extra safety net
dev.to
. Use OpenZeppelin libraries (SafeMath, Ownable, ERC standards implementations) rather than writing your own – they are
community-vetted for security
dev.to
dev.to
. Avoid using tx.origin for authentication and do not use deprecated constructs like suicide (use selfdestruct with
caution, or better, avoid selfdestruct in upgradable patterns).
Readable and Auditable Code: Write clear code because it will likely be audited. Use descriptive names for contracts
and variables (e.g., rewardRate instead of rr). Break large contracts into smaller ones or use libraries for
modularity. Favor composition (contracts calling library functions) over inheritance when possible to reduce complexity
(but use inheritance for well-established patterns like Ownable, ERC20 etc.). Include NatSpec comments for functions
and critical sections – this helps others (and automated tools) understand your intentions. For example, /// @notice
Explain what this function does... above a function will be valuable for auditors and users.
Linting and Formatting
Solidity Linters: Use Solhint or Solium to enforce style and catch common mistakes. These linters can warn about
missing function visibility, using var (avoid, use explicit types), and many security patterns (like calls not handling
return values, etc.). Fix all compiler warnings – treat them seriously; for instance, if the compiler warns about a
function state mutability, explicitly mark functions pure/view when appropriate to make intention clear. Enable
optimizer settings appropriately for your contract (usually enable optimization for production to reduce gas cost, but
ensure you test with those settings).
Consistent Style: Adopt a consistent code style: 4 spaces indentation, capitalize contract names (PascalCase), function
and variable names in mixedCase. Order the sections of your contract logically – e.g., state variables at top, then
events, then constructor, then functions (public before internal for readability, or grouped by functionality). Use the
Solidity Style Guide as a reference. For example, explicitly mark the visibility of functions and state variables
(public/private/internal/external) – not only is it required for functions, but it improves clarity for state vars.
Also, label functions with modifiers like payable, view, or pure as appropriate – this both communicates intent and
saves gas (view/pure functions can be optimized by the compiler).
Formatting and Comments: Use a formatter (the Solidity extension for VS Code or prettier-plugin-solidity) to
auto-format your code – this will standardize things like spacing around operators, line breaks, etc. Break long
expressions or require statements onto multiple lines for readability. Comment your code, but avoid redundant comments
that restate code – focus on the why, not the what. For complex math or logic, a short comment can prevent
misunderstandings. Ensure comments are updated when code changes (outdated comments can mislead auditors).
Architecture and Structure
Smart Contract Design: Keep contracts small and focused. A contract should ideally represent one core concept (ERC20
token, CrowdSale, etc.). If one contract grows too large (approaching block gas limits for deployment or the 24kB
contract size limit), refactor into multiple contracts and use interfaces to communicate between them. Use libraries
for utility functions (math, array operations) to avoid repetitive code and to benefit from library deployment (which
can save space if used by multiple contracts).
Upgradeability Considerations: If you need upgradeable contracts, use well-known proxy patterns (like OpenZeppelin’s
Transparent or UUPS proxy). Design your logic contract’s storage layout carefully and never change the order of state
variables in an upgrade – append only. If not using upgradeable patterns, make it clear in the code (perhaps by
commenting) that the contract is intended to be immutable post-deployment. Many security issues arise from incorrect
upgrade implementations, so leverage community-audited frameworks rather than inventing your own.
Separation of Concerns: Separate concerns between contracts. For example, if building a DeFi system, you might have one
contract for token logic, another for governance, and another for treasury – rather than one mega-contract that does
everything. Use interfaces (interface IERC20 { ... }) to interact with external contracts or to define expected
behavior, instead of contract types, to reduce compilation dependencies and clarify external calls. Keep in mind the
EVM limitations: too much logic in one contract not only costs more gas but increases risk. It’s often better to have
multiple contracts each responsible for a piece of functionality than one large contract that is a single point of failure.
Modern Tooling
Development Frameworks: Use a modern development framework like Hardhat or Truffle for development and testing. These
frameworks provide local blockchain environments, testing libraries, and plugins (for coverage, gas reporting,
linting). Hardhat in particular (as of 2025) is widely used – leverage Hardhat’s console logging (console.log) in
Solidity during development for debugging, and its extensive plugin ecosystem (such as verifying contracts on explorers
automatically, measuring gas, etc.).
Static Analysis and Audits: Utilize static analysis tools like Slither by Crytic to analyze your contracts for
vulnerabilities. Slither can detect reentrancy possibilities, unused return values, shadowed variables and more. It’s a
great automated check in your CI pipeline to catch low-hanging issues. Additionally, consider formal verification for
critical contracts or invariants using tools like Scribble or Certora, which can mathematically prove certain
properties (though these require expertise). At minimum, engage in peer reviews or third-party audits for any contract
that will handle significant value – an extra set of eyes (or many, in case of community audits) is invaluable.
Testing and Gas Analysis: Write extensive tests in JavaScript/TypeScript (Hardhat, Foundry or Truffle) or using Foundry
(in Solidity) to ensure contract behavior. Cover not just the “happy paths” but also edge cases (e.g., arithmetic
overflow – though with Solidity 0.8+, overflow will throw, still test boundary conditions; test ownership restrictions;
test failure cases like withdrawing too much). Use property-based testing or fuzzing (Foundry’s fuzz tests or Echidna)
for critical invariants – e.g., “no one except owner can call X”, “the sum of all user balances equals total supply”
etc. Track gas costs of functions (Hardhat Gas Reporter or Foundry’s gas reports) – ensure they are within reasonable
bounds for expected usage. If a function is too gas-heavy (close to block limit), consider refactoring to offload some
work off-chain or splitting functionality.
Security, Testing, Performance, and DX
Security Practices: Assume all external calls can be malicious – use reentrancy guards and check-effects-interactions as noted
dev.to
. Validate inputs thoroughly: use require statements to enforce valid ranges, non-zero addresses, array lengths
matching, etc., with clear error messages. Never use delegatecall with untrusted contracts. Keep fallback functions
(fallback()/receive()) simple – do not have complex logic in fallback to avoid gas griefing; typically, they should
just revert or accept funds and nothing more. Use emit events for critical actions (transfers, ownership changes) for
transparency. If your contract is upgradable or uses proxies, lock the implementation contract’s initializer (to
prevent others from initializing it and taking ownership). And finally, stay updated on known Solidity vulnerabilities
and best practices via official docs or community (for instance, know about front-running issues if relevant, and use
techniques like commit-reveal schemes or OpenZeppelin’s library solutions to mitigate them).
Comprehensive Testing: Aim for 100% coverage of reachable Solidity code. Test normal scenarios and failure scenarios
(e.g., “should revert if non-owner calls”, “should not allow withdrawal above balance”). Use frameworks’ ability to
impersonate addresses or fast-forward time (Hardhat and Foundry allow time manipulation) to test time-dependent logic.
Test with different accounts to ensure only the intended roles can do actions. If your contract integrates with another
protocol, write integration tests on a fork of mainnet (Hardhat fork feature) to ensure it behaves as expected with
real contracts. Performance test critical functions by simulating worst-case inputs (e.g., loops over max array size)
to ensure gas costs stay within limits and no block gas limit issues.
Performance Optimizations: Solidity has certain optimization techniques to reduce gas: use immutable for variables that
are set once in constructor and never change (saves gas on each access), use constant for truly constant values, pack
storage variables efficiently (place same type or smaller types together to avoid storage slot wastage), and minimize
storage writes (since they are expensive). For example, reading a state variable multiple times in a function costs gas
– cache it in a local variable if used often. Be mindful that extensive use of loops can be problematic – try to limit
loop iterations, or break logic into multiple calls if needed (though that shifts burden to caller). Evaluate
trade-offs: sometimes a bit of complexity (e.g., computing something on the fly) can save storage gas at the cost of
computation gas, which might be worth it depending on usage patterns. Use gas profiling tools or Hardhat’s console to
measure the impact of changes.
Developer Experience: Invest in your contract’s documentation and tooling. Provide a README or docs explaining how to
deploy and interact with the contracts. For your team (or open source contributors), supply scripts for common tasks
(deployment, verification, running tests) in package.json or a task runner. Use Git hooks or CI to run solhint/slither
so code enters review already vetted. During development, use a personal testnet or local node for quick iterations;
for staging, use testnets (Goerli, Sepolia, etc.) and possibly have a script to populate testnet with some scenario (so
colleagues can play with the contract on testnet UI). Good DX also means using consistent commit messages and perhaps a
changelog for contract changes (especially if multiple people work on it). Finally, when deploying to production
(mainnet), double-check everything: addresses, constructor params, compiler optimization settings, etc., and consider a
small “beta” deployment first. Solid developer practices ensure that the path from code to deployed bytecode is smooth and error-free, which is crucial when real money is on the line.

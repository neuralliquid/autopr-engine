---
trigger: glob
globs: **/*.ts, **/*.tsx
---

Best Practices
Embrace Type Safety: Enable the strictest compiler options (e.g. "strict": true in tsconfig.json) to catch null/undefined issues early
dev.to
. Avoid using any in code – use generics or unknown as safer alternatives for values of uncertain type
javascript.plainenglish.io
javascript.plainenglish.io
. Define explicit types for function inputs/outputs and leverage TypeScript’s inference for internal variables.
Clean, Modular Design: Organize code into modules by feature or domain for maintainability. Use interfaces or type aliases to define data shapes clearly (interfaces for object contracts, type aliases for unions/tuples, etc.). Favor composition over inheritance in React components – build small, pure functions and components that do one thing well. Ensure each React component is focused (e.g. presentational vs. container logic separated) following single-responsibility principles.
React Best Practices: In TSX (React), use functional components with Hooks instead of class components for stateful logic. Type component props and state with interfaces/types for clarity
dev.to
. Avoid heavy logic in the render; move data processing to outside functions or use Hooks (e.g. useMemo for expensive calculations). Prevent prop drilling by using Context or state management libraries for globally needed state.
Linting and Formatting
ESLint and Prettier: Adopt ESLint with TypeScript-specific rules and integrate Prettier for consistent code style
dev.to
. Extend configs like plugin:@typescript-eslint/recommended and prettier to catch potential errors (unused variables, improper any, etc.) and automatically format code
dev.to
. This ensures uniform spacing, quote usage, and catches anti-patterns across the team.
Code Style Conventions: Follow a consistent style – e.g. 2 spaces (or tabs) for indentation depending on project standard, semicolons for termination (Prettier default), and use single vs. double quotes uniformly as configured. Name variables and functions in camelCase, classes in PascalCase. Enforce no trailing whitespace and include newline at end of files for Git diffs sanity. Use meaningful naming; avoid abbreviations. Linters should flag any deviance, so treat linter warnings as errors.
Automated Fixes: Use eslint --fix and Prettier on save or in CI to auto-format. Configure import ordering (via ESLint or tools like import/order) to sort imports by module domain. These automations reduce nitpicks in code reviews and keep the codebase idiomatic.
Architecture and Structure
Project Organization: Structure the codebase by features or layers. For example, group related components, hooks, and utilities in one folder. In larger apps, consider a monorepo or modular structure (e.g. using Nx) to separate front-end, back-end, and shared code. Use barrel files (index.ts) to re-export modules for cleaner imports.
React Component Structure: Design components to be reusable and predictable. Keep presentational (UI) components separate from logic (use custom Hooks or controller components for data fetching and state). Follow the pattern of “lift state up” – hoist state to the nearest common parent to avoid duplicate state. Use context for global concerns (theme, user auth) rather than passing props deeply.
State Management: Favor React’s built-in state and context for most cases. If the app grows complex, introduce state libraries (like Redux Toolkit, Zustand, or context + reducer) but keep TypeScript types in sync with state shape. Define clear interfaces for state slices and actions if using Redux or similar. Leverage TypeScript’s discriminated unions for action types instead of strings to get compiler-checked exhaustiveness.
Modern Tooling
Build and Frameworks: Use modern build tools like Vite or Next.js which have first-class TypeScript support for faster builds and DX
dev.to
. These provide hot-reload and efficient bundling. If building an SPA, consider Next.js or Remix for structure; for libraries, use tsup or tsc with bundlers for packaging.
Utility Libraries: Integrate modern TS-centric libraries – e.g. Zod for runtime schema validation to complement TypeScript types
javascript.plainenglish.io
javascript.plainenglish.io
, ensuring external data matches your expected types. Use Tailwind CSS (with TypeScript-ready frameworks) for utility-first styling to speed up UI development. Leverage component kits or headless UI libraries typed for TypeScript to avoid reinventing the wheel.
Monorepo and Modules: In large projects, use tools like Nx or Turborepo to manage multiple TypeScript packages with shared configs. Take advantage of TypeScript Project References for clean boundaries between modules. Ensure consistent tsconfig base settings across packages. Modern testing tools like Vitest or Jest with TS support should be in place for fast feedback in development.
Security, Testing, Performance, and DX
Security Practices: Never trust external input types blindly – always validate (for example, parse JSON responses with Zod schemas before use). Avoid any or @ts-ignore which can mask unsafe operations
javascript.plainenglish.io
. In React, guard against XSS by avoiding dangerouslySetInnerHTML unless necessary (and if so, sanitize inputs). Keep dependencies updated to patch vulnerabilities, and enable DOM-based security lint rules (ESLint plugin) to flag risky code.
Testing: Write tests for critical logic and components. Use Jest or Vitest for unit tests with TS support, and React Testing Library for components to ensure they render and behave correctly. Aim for a good coverage on pure functions and complex components (logic branches, state updates). Leverage TypeScript in tests for auto-complete and to catch API misuse. Run type checking (tsc --noEmit) and linting in CI, so any type errors fail the build.
Performance: Utilize React performance optimizations: memoize expensive calculations with useMemo, wrap pure components in React.memo if they re-render excessively, and use dynamic import(import()) for code-splitting heavy modules
dev.to
. Monitor bundle size (using tools like Webpack Bundle Analyzer or Vite’s visualizer) and tree-shake unused code. In TS, prefer native data structures and algorithms that are efficient – e.g. use array methods and maps wisely to avoid O(n²) pitfalls.
Developer Experience: Ensure the development environment is robust: include TypeScript type checking in your workflow (e.g. VS Code or IDE integration). Provide an npm run dev script that runs the app with hot reload and a npm run test for running tests easily. Maintain good documentation via JSDoc or Storybook for components, making it easier for developers to use and update code. Strive for clear compiler error messages by explicitly typing ambiguous returns and avoiding overly complex generics that produce cryptic errors. When issues arise, prefer compile-time solutions or tooling (types, linters) over leaving it to runtime. A clean, typed codebase with consistent rules will significantly enhance maintainability and onboarding.

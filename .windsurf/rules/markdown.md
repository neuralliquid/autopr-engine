---
trigger: glob
globs: **/*.md, **/*.mdx
---

Best Practices Use Proper Markdown Structure: Start documents with a single H1 (# Title) and avoid
multiple top-level H1s in one file xiangxing98.github.io . Structure content hierarchically with
headings in descending order (H2, H3, etc.) – do not skip levels (e.g., don’t jump from H1 to H3) to
maintain a logical outline xiangxing98.github.io . Keep paragraphs short and focused (generally 1-3
sentences in markdown context) to enhance readability. When writing lists, use consistent bullet
styles (commonly - or \*) and indentation. For ordered lists, just use “1.” for all items – Markdown
will auto-number, and it avoids re-numbering diffs if you add items in the middle. MDX
Considerations: In MDX (Markdown extended with JSX), you can embed React components. Treat MDX files
as primarily Markdown – use JSX sparingly for interactive or dynamic content. Keep any imports at
the top of the MDX file (before any content) and ensure they are used (unused imports can cause MDX
compilation issues). Avoid exporting from MDX unless necessary (MDX supports export, but that’s
usually for page metadata in some frameworks – follow your framework’s conventions). Use MDX for
things like embedding custom components, but do not put heavy logic in MDX – any complex logic
should reside in the component imported, not inline, to keep content readable. Linting and
Formatting Markdownlint: Use markdownlint (or its CLI markdownlint-cli2) to catch common issues.
This enforces rules like: headings should be surrounded by blank lines xiangxing98.github.io , no
trailing whitespace, ordered list items in sequence, etc. Configure a .markdownlint.json if you need
to adjust defaults (for example, you might set MD013 (line length) to allow longer lines for
tables/URLs). Regularly run this linter or integrate it in pre-commit hooks to keep docs consistent.
Prettier for Markdown: Enable Prettier for Markdown/MDX to automatically wrap text and format lists.
A consistent line length (commonly 80 or 120 characters) is helpful; Prettier by default will wrap
prose. Prettier will also ensure lists and indentation are consistent. Use it to format code blocks
within markdown as well – specify the language after the triple backticks for syntax highlighting
and to leverage any formatting (e.g., "json"). For example, use “js” for JavaScript, “```bash” for
shell, etc., which improves readability and is a good practice. Blank Lines and Spacing: Ensure you
leave a blank line before and after headings, lists, blockquotes, and code fences
xiangxing98.github.io . This spacing is required by many markdown engines and linters (it also makes
the raw markdown easier to read). Also, no multiple blank lines in a row – one blank line is enough
to separate sections (markdownlint will flag multiple consecutive blank lines as well). In MDX, when
mixing JSX and Markdown, you often need blank lines or explicit line breaks to separate them
correctly – pay attention to how the MDX compiles (e.g., content directly adjacent to JSX might need
an empty line). Architecture and Structure Document Structure: Begin documents with a top-level
heading as the title (or metadata frontmatter if your system uses it). Use subsequent headings to
create a table of contents structure. For longer documents, consider adding a brief introduction
under the title to summarize the content. Use thematic break lines (---) or additional blank lines
sparingly to indicate shifts in topic if needed. If writing documentation, maintain a consistent
structure across pages (e.g., each page starts with an H1, then perhaps an intro, then H2 sections
like "Usage", "Examples", etc.). This consistency helps users navigate and also helps when
generating summary tables of contents. Frontmatter (if MDX in a site): If your MDX/Markdown is part
of a static site (like Docusaurus, Next.js, etc.), use frontmatter YAML at the top for metadata
(between --- lines). Include title, description, tags, or any relevant metadata. This is not
standard markdown, but many frameworks use it – ensure the frontmatter is valid YAML (keys
lowercase, values quoted appropriately). Keep the frontmatter concise; extensive content should be
in the body of the document. MDX Components Usage: Treat custom MDX components as content
enhancements – for example, an <Alert> component for call-out notes, or interactive charts. Place
them inline where appropriate, but ensure the surrounding context still makes sense if the component
doesn’t render (for instance, search engines or certain converters might not handle custom
components). Provide fallback content when possible or use alt text (if it’s an image component).
Additionally, document the usage of these components (perhaps in comments or separate contributor
docs) so others writing MDX know how to use them. Modern Tooling MDX and Framework Integration: Stay
up-to-date with your framework’s MDX version (MDX 2 is current) and capabilities. Leverage plugins
as needed, e.g., MDX embed plugins for common embed content (videos, tweets), rather than writing
raw iframes. If using Next.js, for example, you might use next-mdx-remote or built-in MDX support –
make sure your config (like webpack/loader settings) is properly set to handle MDX. For
documentation sites, tools like Docusaurus or Docz can manage MDX content – use their
theming/components to maintain a consistent look. Live Preview and CI: Use a Markdown/MDX live
preview (VS Code has good Markdown preview, and for MDX, tools like mdx-preview or running a dev
server) to continuously check how your content renders. This helps catch issues like a missing blank
line breaking formatting, or an MDX component not rendering as expected. In CI, if possible,
generate the site or docs and, if using something like automated tests, ensure no broken links or
broken fragments (some CI setups use link checkers or screenshot comparisons for docs).
Documentation Automation: If the markdown is for documentation, consider automating parts of it: for
instance, generate API docs from source code comments (and include via MDX imports or during site
build), or use tools to ensure code examples stay up to date (some use literalinclude or embed code
from actual source files). This reduces drift between docs and code. Also, use lint rules to enforce
that code fences in docs compile or meet certain criteria (for example, run a linter on code blocks
in markdown via tools like markdownlint or custom scripts). Modern docs frameworks allow embedding
interactive code sandboxes or using components like LiveCodeBlock – take advantage of that in MDX to
provide a better developer experience, where appropriate. Security, Testing, Performance, and DX
Security in Markdown/MDX: Generally, markdown is text and not a security risk, but MDX does allow
JSX – be cautious not to include sensitive data in MDX, as it will be publicly visible. Also, if
user-generated content is being included via MDX, ensure it’s sanitized (to prevent XSS through MDX,
which can execute JSX). If your MDX components accept props that are printed to the DOM, treat them
as potentially unsafe if coming from untrusted sources (escape or sanitize as needed). Testing Docs:
Treat documentation as code – broken documentation can mislead or frustrate users. If possible, set
up tests for docs: e.g., a link checker that ensures all hyperlinks in markdown are valid (no 404s).
For MDX, if you have critical interactive components, write Jest/React tests for them just as you
would for any React component (you can import the MDX file in a test and render it to ensure it
doesn’t throw). This can catch compilation issues or runtime errors in custom docs components.
Performance and Build: Markdown/MDX processing is usually lightweight, but a lot of MDX pages with
heavy components can slow site builds. Monitor your docs build times; if MDX compilation becomes a
bottleneck, consider splitting content or disabling source maps for MDX in production builds. Also,
large images included in markdown should be optimized (either commit optimized versions or use a
plugin that optimizes images on the fly). For a better user experience, use modern image syntax or
MDX image components that auto-generate srcset/responsive images if your framework supports it.
Ensure that any custom scripts or iframes included via MDX do not excessively impact page
performance; use lazy loading for heavy embeds (like videos) where possible. Developer Experience:
Writing and maintaining docs should be as frictionless as possible. Provide templates or examples
for common doc types (e.g., a tutorial template with sections for Overview, Prerequisites, Steps,
Conclusion). Encourage using Markdown features for clarity: lists, tables, bold and italic for
emphasis, and backticks for inline code or fenced code blocks for code snippets. Enforce a policy
that any code in docs is actual, working code – ideally, have someone run it or test it when
updating docs (nothing is worse than a tutorial that doesn’t actually work). If documentation is
versioned, clearly organize version directories or use tools to version docs so that it’s easy to
update the latest while keeping old versions archived. In summary, treat documentation with the same
care as source code: lint it, test it, and make it easy to update – this ensures it remains an
up-to-date and trustworthy resource.

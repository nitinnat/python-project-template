# Code style
- Avoid the following "AI Slop" patterns
    - Extra comments that a competent senior engineer wouldn’t add or is inconsistent with the rest of the codebase. This includes docstrings - if it's very obvious what a function, class or file does to a senior engineer, then do not add a docstring. Reserve docstrings for crucial information that is not really obvious by looking at the code. Avoid adding Args and Returns information in the docstrings.
    - Avoid extra defensive checks or try/catch blocks that are abnormal for that area of the codebase.
    - Avoid casting a variable to a different type to get around type issues (or other similar patterns).
    - Variables that are only used a single time right after declaration, prefer inlining the RHS.
    - Style or formatting that is inconsistent with the file.
    - Excessive emojis or emoticons unless it's in a README.md file. Do not add emojis in PR descriptions.
- Utilize software engineering principles like SOLID, DRY, KISS, YAGNI and others to write clean, solid and concise code. Think about whether the code you are adding is inline with the existing code in the repository, and avoid adding copious amounts of code, and lean towards conciseness unless it cannot be helped.


# Debugging Issues
- When trying to debug an issue, do the following:
    1. Understand the issue from the ground up, and internalize it. We are not interested in workarounds, simplifications, or hacky patches.
    2. Lay out a plan for how you'll debug the issue.
    3. If you're running around in circles, stop and revise your plan.
    4. Prefer running small, constrained tests to validate the fixes rather than entire test suites, if it can be helped.


# Pull Request Descriptions
- Do not add emojis and emoticons in PR descriptions.
- Provide a small paragraph describing the entire change, and explain the individual changes below that in concise bullet points.
- Do not add "Created by Claude Code" or anything similar in the PR description.

# General Instructions
- You are allowed to write a maximum of 3 documents (md files) per session, UNLESS the user explicitly asks you to write a 4th or 5th document.
- For EVERY new project, you MUST create and maintain an IMPLEMENTATION_LOG.md file where you preserve a concise, chronological, running log of everything you have planned, implemented, debugged and tested in this project. The document should be written and updated in such a way that a senior engineer should just be able to glance at it and understand whatever has been done in this project until now. This file will also be used by future, new Claude sessions to obtain the required context to take over from where the previous session left off.
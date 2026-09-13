---
trigger: always_on
---

# Mem0 Persistent Memory Protocol

You have access to a persistent memory system via the Mem0 MCP server. You **must** follow this protocol to ensure continuity across sessions.

## 1. Recall (Before Starting a Task)
- At the beginning of every new session, or when the user asks a question that might relate to past work, **first** query the Mem0 server for relevant memories.
- Use the `search_memories` tool with a concise query based on the user's request and the current project context.
- Integrate any relevant memories you find into your understanding of the task.

## 2. Remember (During and After a Task)
- When you learn a new, important piece of information about the project (e.g., architectural decisions, user preferences, important API keys, coding standards), **immediately** store it in Mem0.
- Use the `add_memory` tool to save the information. Be concise and specific.
- Examples of what to remember:
    - "The user prefers using `async/await` over Promises."
    - "The project's API endpoint for user data is `/api/v2/users`."
    - "The database connection string is stored in the `DATABASE_URL` environment variable."

## 3. Update and Forget
- If a previously stored memory becomes outdated or incorrect, you must update it. You can do this by adding a new, corrected memory and noting the change.
- If the user explicitly asks you to forget something, use the `delete_memory` tool.

## 4. Be Proactive
- Do not wait for the user to remind you. Proactively use your memory tools to create a seamless experience.
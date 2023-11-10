import os
import json
from dotenv import load_dotenv
import time
import openai
from setup_db import setup_db
from vector_search import vector_search

load_dotenv()

tools = {
    "vector_search": vector_search
}

# Your OpenAI API key should be set in the .env file
openai.api_key = os.getenv("OPENAI_API_KEY")

client = openai.OpenAI(api_key=openai.api_key)

user_prompt = "Do you have any content about sea creatures?"

instructions = '''
**You are the 'VectorizedKnowledgeBot':** A Chatbot with the capability to perform advanced vector-based searches to provide contextually relevant answers to user queries.

**Instructions for Using the 'vector_search' Tool:**

1. **Understanding the Tool:**
   - The "vector_search" tool is designed to perform a contextually aware search based on a string input. It uses vector space modeling to understand the semantics of the query and retrieve the most relevant information.

2. **Identifying the User Query:**
   - Begin by identifying the user's query. Pay attention to the key concepts and specific details the user is interested in.

3. **Formulating the Search String:**
   - Based on the user's query, formulate a concise and targeted search string. Include the most important keywords and terms that are central to the query's context.

4. **Using the Tool:**
   - Pass the formulated search string to the "vector_search" tool as an argument. Ensure that the string is encapsulated in quotes to be recognized as a text input.

5. **Interpreting Results:**
   - Once the "vector_search" returns results, analyze the information to verify its relevance and accuracy in addressing the user's query.

6. **Communicating the Outcome:**
   - Present the findings from the "vector_search" to the user in a clear and informative manner, summarizing the context or providing a direct answer to the query.

**Example Usage:**

If the user asks about "the impact of climate change on polar bear populations," you would:

- Extract keywords: "impact," "climate change," "polar bear populations."
- Formulate the search string: `"climate change impact on polar bear populations"`
- Pass the string to the tool: `vector_search("climate change impact on polar bear populations")`
- Analyze and relay the information back to the user in response to their query.

Remember to maintain the user's original intent in the search string and to ensure that the results from the "vector_search" are well-interpreted before conveying them to the user.
'''


def main():
    try:
        setup_db()

        assistant = client.beta.assistants.create(
            model="gpt-4-1106-preview",
            name="VectorizedKnowledgeBot",
            instructions=instructions,
            tools=[{
                "type": "function",
                "function": {
                    "name": "vector_search",
                    "description": "Perform a vector-based search to retrieve contextually relevant information based on a user's query.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "A targeted search string based on a user query."},
                        },
                        "required": ["query"]
                    }
                },
            }]
        )

        thread = client.beta.threads.create()

        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_prompt
        )

        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id,
        )

        while run.status in ['queued', 'in_progress']:
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
        if run.status == "requires_action":
            if run.required_action.submit_tool_outputs.tool_calls[0].type == 'function':
                tool_function = run.required_action.submit_tool_outputs.tool_calls[0].function
                function_name = getattr(tool_function, 'name')
                arguments = getattr(tool_function, 'arguments')
                # Now call the function from the tools dictionary using the function name
                result = tools[function_name](arguments)
                run = client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=[
                        {
                            "tool_call_id": run.required_action.submit_tool_outputs.tool_calls[0].id,
                            "output": json.dumps(result),
                        },
                    ]
                )
                while run.status in ['queued', 'in_progress']:
                    time.sleep(1)
                    run = client.beta.threads.runs.retrieve(
                        thread_id=thread.id,
                        run_id=run.id
                    )

        messages = client.beta.threads.messages.list(thread_id=thread.id)

        for message in sorted(messages.data, key=lambda x: x.created_at):
            print(
                f'{"Assistant" if message.assistant_id else "User"}: {message.content[0].text.value}')

    except Exception as err:
        print("Error:", err)


if __name__ == '__main__':
    main()

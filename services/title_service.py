from graph import llm

def generate_title(message):

    prompt=f"""
You are an AI that generates chat titles.

Rules:

- Maximum 5 words.
- No punctuation.
- No quotes.
- Return only the title.

User Message:

{message}
"""

    response=llm.invoke(prompt)

    return response.content.strip()
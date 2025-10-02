
from groq import Groq

groq_client = Groq() 

def summarize_code(code_text):
    # Your summarization prompt
    prompt = (
        "Summarize the code in plain English. Briefly describe each class and function/method "
        "(their purpose and role), then give a short overall summary of how they work together. "
        "Avoid low-level details."
    )

    # Combine prompt and code
    full_prompt = f"{prompt}\n\n<CODE>\n{code_text}\n</CODE>"

    # Send to LLM
    messages = [
        {"role": "system", "content": "You are a helpful assistant that explains code clearly."},
        {"role": "user", "content": full_prompt}
    ]

    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages
    )

    return response.choices[0].message.content.strip()

def save_code_and_summary(code_text, summary, filename='save_code_and_summary.md'):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("# 🧠 Code Summary\n\n")
        f.write(f"{summary}\n\n")
        f.write("---\n\n")
        f.write("# 🧾 Source Code\n\n")
        f.write("```python\n")
        f.write(code_text)
        f.write("\n```\n")

    print(f"Saved summary and code to {filename}")

with open("exercise_day2.py", "r", encoding="utf-8") as f:
    code_text = f.read()

summary = summarize_code(code_text)
save_code_and_summary(code_text, summary)


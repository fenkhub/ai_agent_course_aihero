import gradio as gr
import pandas as pd
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error
from openai import OpenAI
from groq import Groq
import markdown
import datetime

# API clients
openai_client = OpenAI(api_key="your-openai-key")
groq_client = Groq(api_key="your-groq-key")

# Chat history
chat_log = []

def query_llm(prompt, provider, model):
    if provider == "OpenAI":
        response = openai_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        reply = response.choices[0].message.content
    else:
        response = groq_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        reply = response.choices[0].message.content
    chat_log.append(f"**User:** {prompt}\n**Bot:** {reply}")
    return reply

def export_markdown():
    filename = f"chat_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(filename, "w") as f:
        f.write("\n\n".join(chat_log))
    return f"Saved as {filename}"

def run_classification(data, target_col):
    X = data.drop(columns=[target_col])
    y = data[target_col]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    return f"Accuracy: {acc:.2f}"

def run_regression(data, target_col):
    X = data.drop(columns=[target_col])
    y = data[target_col]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    model = LinearRegression()
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    mse = mean_squared_error(y_test, preds)
    return f"MSE: {mse:.2f}"

def memory_mnemonics(topic):
    if topic == "classification":
        return "🔍 Think of classification like sorting mail: 📬📦📄. Each item goes into a category!"
    elif topic == "regression":
        return "📈 Regression is like drawing a line through data points to predict future values."
    else:
        return "🧠 Use memory palace: place each ML step in a room of your house!"

# Gradio UI
with gr.Blocks() as app:
    lang = gr.Radio(["English", "Indonesian"], label="Language")
    provider = gr.Dropdown(["OpenAI", "Groq"], label="LLM Provider")
    model = gr.Dropdown(["gpt-3.5-turbo", "mistral-7b", "claude-2"], label="Model")
    prompt = gr.Textbox(label="Prompt")
    response = gr.Textbox(label="LLM Response")
    export_btn = gr.Button("Export Chat to Markdown")

    def chat_fn(p, prov, mod, l):
        reply = query_llm(p, prov, mod)
        if l == "Indonesian":
            reply = "🇮🇩 " + reply  # Simplified bilingual toggle
        return reply

    prompt.submit(chat_fn, inputs=[prompt, provider, model, lang], outputs=response)
    export_btn.click(export_markdown, outputs=response)

    with gr.Tab("Classification"):
        file_c = gr.File(label="Upload CSV")
        target_c = gr.Textbox(label="Target Column")
        output_c = gr.Textbox(label="Result")
        file_c.change(lambda f: pd.read_csv(f.name), inputs=file_c, outputs="data")
        gr.Button("Run Classification").click(run_classification, inputs=["data", target_c], outputs=output_c)

    with gr.Tab("Regression"):
        file_r = gr.File(label="Upload CSV")
        target_r = gr.Textbox(label="Target Column")
        output_r = gr.Textbox(label="Result")
        file_r.change(lambda f: pd.read_csv(f.name), inputs=file_r, outputs="data")
        gr.Button("Run Regression").click(run_regression, inputs=["data", target_r], outputs=output_r)

    with gr.Tab("Memory Techniques"):
        topic = gr.Dropdown(["classification", "regression", "general"], label="Topic")
        mnemonic = gr.Textbox(label="Mnemonic")
        topic.change(memory_mnemonics, inputs=topic, outputs=mnemonic)

app.launch()

# 🧠 Code Summary

**Classes and Functions Overview**

1. **`read_repo_data(repo_owner, repo_name)`**:
   - Purpose: Download and parse all Markdown files from a GitHub repository.
   - Role: Main data ingestion function for the script.

2. **`llm(document, model='llama-3.1-8b-instant')`**:
   - Purpose: Utilize a large language model to divide a given text into logical sections.
   - Role: Secondary data processing function for the script.

3. **`intelligent_chunking(text)`**:
   - Purpose: A wrapper function around `llm()` to simplify the chunking process.
   - Role: Simplifies the process of dividing text into sections.

4. **`save_chunks_to_markdown(data, filename='evidently_chunks2.md')`**:
   - Purpose: Save the processed data to an MD file.
   - Role: Data output and storage function for the script.

5. **`Groq()`**:
   - Purpose: Initialize the Groq API client for interacting with LLMs.
   - Role: Provides API connection for calling the LLM.

**Overall Summary**

The script works by:

1. Downloading Markdown files from two GitHub repositories (`brightdata/mcp` and `patchy631/ai-engineering-hub`) using the `read_repo_data()` function.
2. Using the `llm()` function to divide the contents of each Markdown file into logical sections based on LLM analysis.
3. Iteratively chunking the text of each Markdown file and storing the results in the `evidently_chunks` list.
4. Saving the final list of chunks to an MD file named `evidently_chunks2.md` utilizing the `save_chunks_to_markdown()` function.

The script can be used to extract logical sections from a large collection of Markdown files, making it easier to organize and query the content for Q&A purposes.

---

# 🧾 Source Code

```python
import io
import zipfile
import requests
import frontmatter

def read_repo_data(repo_owner, repo_name):
    """
    Download and parse all markdown files from a GitHub repository.
    
    Args:
        repo_owner: GitHub username or organization
        repo_name: Repository name
    
    Returns:
        List of dictionaries containing file content and metadata
    """
    prefix = 'https://codeload.github.com' 
    url = f'{prefix}/{repo_owner}/{repo_name}/zip/refs/heads/main'
    resp = requests.get(url)
    
    if resp.status_code != 200:
        raise Exception(f"Failed to download repository: {resp.status_code}")

    repository_data = []
    zf = zipfile.ZipFile(io.BytesIO(resp.content))
    
    for file_info in zf.infolist():
        filename = file_info.filename
        filename_lower = filename.lower()

        if not (filename_lower.endswith('.md') 
            or filename_lower.endswith('.mdx')):
            continue
    
        try:
            with zf.open(file_info) as f_in:
                content = f_in.read().decode('utf-8', errors='ignore')
                post = frontmatter.loads(content)
                data = post.to_dict()
                data['filename'] = filename
                repository_data.append(data)
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            continue
    
    zf.close()
    return repository_data
brdt_mcp = read_repo_data('brightdata', 'brightdata-mcp')
ai_docs = read_repo_data('patchy631', 'ai-engineering-hub')

print(f"FAQ documents: {len(brdt_mcp)}")
print(f"Evidently documents: {len(ai_docs)}")

from groq import Groq

groq_client = Groq()  # Or use os.environ.get("GROQ_API_KEY")

prompt_template = """
Split the provided document into logical sections
that make sense for a Q&A system.

Each section should be self-contained and cover
a specific topic or concept.

<DOCUMENT>
{document}
</DOCUMENT>

Use this format:

## Section Name

Section content with all relevant details

---

## Another Section Name

Another section content

---
""".strip()

def llm(document, model='llama-3.1-8b-instant'):
    prompt = prompt_template.format(document=document)

    messages = [
        {"role": "system", "content": "You are a helpful assistant that organizes documents for Q&A systems."},
        {"role": "user", "content": prompt}
    ]

    response = groq_client.chat.completions.create(
        model=model,
        messages=messages
    )

    return response.choices[0].message.content

def intelligent_chunking(text):
    prompt = prompt_template.format(document=text)
    response = llm(prompt)
    sections = response.split('---')
    sections = [s.strip() for s in sections if s.strip()]
    return sections
from tqdm.auto import tqdm

evidently_chunks = []

for doc in tqdm(brdt_mcp):
    doc_copy = doc.copy()
    doc_content = doc_copy.pop('content')

    sections = intelligent_chunking(doc_content)
    for section in sections:
        section_doc = doc_copy.copy()
        section_doc['section'] = section
        evidently_chunks.append(section_doc)

def save_chunks_to_markdown(data, filename='evidently_chunks2.md'):
    if not data:
        print("No data to save.")
        return

    with open(filename, 'w', encoding='utf-8') as f:
        for chunk in data:
            #section_title = chunk.get("title", "Untitled Section")  # Optional: you can skip this if titles aren't available
            section_content = chunk.get("section", "").strip()

            #f.write(f"## {section_title}\n\n")
            f.write(f"{section_content}\n\n")
            f.write("---\n\n")

    print(f"Saved {len(data)} sections to {filename}")

save_chunks_to_markdown(evidently_chunks)
```

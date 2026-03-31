def format_chunk_with_citation(text: str, page_num: int):
    """
    LIMITATION FIX: Explainable AI (XAI) Citations
    Appends page metadata directly into the chunk text so the LLM 
    can confidently cite exactly where it found the information.
    """
    return f"[Source: Page {page_num}]\n{text}"

def generate_xai_prompt(query, context):
    """
    Creates an Explainable AI (XAI) prompt that strictly forces the LLM 
    to append page citations to its answers for easy verification.
    """
    context_text = "\n\n".join(context)
    return f"""You are a professional and secure banking assistant.

--- CONTEXT ---
{context_text}
--- END CONTEXT ---

Question: {query}

Instructions:
- Check if the CONTEXT contains information to answer the question. If so, base your answer on it.
- If the CONTEXT does NOT contain the answer, you MUST use your general banking and financial knowledge to provide a full, helpful answer.
- Answer in a clear, professional, structured manner (use bullet points or numbered steps).
- End with a brief 1-line summary starting with "💡 Summary:".

CRITICAL XAI (Explainable AI) REQUIREMENT:
If you use information from the CONTEXT, you MUST cite the page number at the end of every relevant sentence or bullet point (e.g., "(Page 2)").
You MUST also start your response with EXACTLY ONE of these tags on the very first line:
[SOURCE: Uploaded Documents]
[SOURCE: Gemini General Knowledge]
"""

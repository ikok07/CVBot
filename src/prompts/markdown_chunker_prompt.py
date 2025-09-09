MARKDOWN_CHUNKER_PROMPT = """
    You are an assistant specialized in splitting text into semantically consistent sections.
    
    <instructions>
        <instruction>The text has been divided into chunks, each marked with <|start_chunk_X> and <|end_chunk_X|> tags, where X is the chunk number</instruction>
        <instruction>Identify points where splits should occur, such that consecutive chunks of similar themes stay together</instruction>
        <instruction>Each chunk must be between 200 and 1000 words</instruction>
        <instruction>If chunk 1 and 2 belong together but chunk 3 starts a new topic, suggest a split after chunk 2</instruction>
        <instruction>The chunks must be listed in ascending order</instruction>
        <instruction>Provide your response in the form: 'split_after: 3,5'</instruction>
    </instructions>
    
    This is the document text:
    <document>
    {document_text}
    </document>
    
    Respond only with the IDs of the chunks where you believe a split should occur.
    YOU MUST RESPOND WITH AT LEAST ONE SPLIT.
""".strip()
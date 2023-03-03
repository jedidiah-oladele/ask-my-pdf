"AI (LLM) adapter"
# TODO: replace with ai_bricks.ai_openai

BUTCHER_EMBEDDINGS = None  # this should be None, as it cuts the embedding vector to n first values (for debugging)


import tiktoken

encoder = tiktoken.encoding_for_model("text-davinci-003")


def get_token_count(text):
    tokens = encoder.encode(text)
    return len(tokens)


import openai


def use_key(api_key):
    openai.api_key = api_key


def complete(prompt, temperature=0.0):
    kwargs = dict(
        model="gpt-3.5-turbo",
        max_tokens=4096 - get_token_count(prompt),
        temperature=temperature,
        n=1,
    )
    kwargs["messages"] = [
        {"role": "system", "content": "output only in raw text"},
        {"role": "user", "content": prompt},
    ]
    kwargs["max_tokens"] -= 30  # UGLY: workaround for not counting chat specific tokens
    resp = openai.ChatCompletion.create(**kwargs)  # API CALL

    out = {}
    out["text"] = resp["choices"][0]["message"]["content"]
    out["usage"] = resp["usage"]
    return out


def embedding(text):
    resp = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002",
    )
    out = {}
    out["vector"] = list(resp["data"][0]["embedding"][:BUTCHER_EMBEDDINGS])
    out["usage"] = dict(resp["usage"])
    return out

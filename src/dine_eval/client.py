"""A minimal OpenAI-compatible chat client.

The DINE judge only needs one operation: send a prompt, get back text. Any
callable ``str -> str`` works as a client, so you can plug in your own provider.
``OpenAICompatibleClient`` covers the common case (OpenAI, Azure, Together,
Groq, local vLLM / Ollama OpenAI endpoints, ...) over the standard
``/chat/completions`` route with ``temperature=0`` by default.
"""
from __future__ import annotations
import json
import time
import urllib.request
import urllib.error
from typing import Protocol


class Client(Protocol):
    """Anything that turns a prompt into model text."""

    def complete(self, prompt: str) -> str: ...


class OpenAICompatibleClient:
    def __init__(
        self,
        model: str,
        api_key: str | None = None,
        base_url: str = "https://api.openai.com/v1",
        temperature: float = 0.0,
        system: str = "You are an impartial evaluator. Reply with JSON only.",
        timeout: float = 60.0,
        max_retries: int = 3,
        extra_headers: dict[str, str] | None = None,
    ):
        self.model = model
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.temperature = temperature
        self.system = system
        self.timeout = timeout
        self.max_retries = max_retries
        self.extra_headers = extra_headers or {}

    def complete(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "temperature": self.temperature,
            "messages": [
                {"role": "system", "content": self.system},
                {"role": "user", "content": prompt},
            ],
        }
        headers = {"Content-Type": "application/json", **self.extra_headers}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        data = json.dumps(payload).encode("utf-8")
        url = f"{self.base_url}/chat/completions"

        last_err: Exception | None = None
        for attempt in range(self.max_retries):
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    body = json.loads(resp.read().decode("utf-8"))
                return body["choices"][0]["message"]["content"]
            except urllib.error.HTTPError as e:  # 4xx/5xx
                last_err = e
                if e.code in (429, 500, 502, 503, 504) and attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise
            except (urllib.error.URLError, TimeoutError) as e:
                last_err = e
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise
        raise RuntimeError(f"request failed after {self.max_retries} attempts: {last_err}")


class CallableClient:
    """Wrap any ``str -> str`` function as a Client."""

    def __init__(self, fn, model: str = "custom"):
        self._fn = fn
        self.model = model

    def complete(self, prompt: str) -> str:
        return self._fn(prompt)

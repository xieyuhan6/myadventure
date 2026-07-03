import os
import json
import requests
from openai import OpenAI
from typing import Optional
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from core.prompts import STORY_PROMPT
from models.story import Story, StoryNode
from core.models import StoryLLMRepsonse, StoryNodeLLM
from langchain_core.output_parsers import PydanticOutputParser
from core.config import settings

load_dotenv()

HF_API_TOKEN = settings.HF_API_TOKEN
HF_MODEL = settings.HF_MODEL
print("story_generator using HF_MODEL:", HF_MODEL, "HF_API_TOKEN set:", bool(HF_API_TOKEN))
HF_ROUTER_URL = "https://router.huggingface.co/api/v1/requests"
HF_INFERENCE_URL_TEMPLATE = "https://api-inference.huggingface.co/models/{model}"
USE_LOCAL_HF = settings.USE_LOCAL_HF

def _parse_hf_response(data):
    if isinstance(data, list) and data:
        item = data[0]
        if isinstance(item, dict):
            return item.get("generated_text") or item.get("text") or item.get("content") or str(item)
        return str(item)
    if isinstance(data, dict):
        for k in ("output", "outputs", "generated_text", "text", "result", "prediction", "content"):
            if k in data:
                v = data[k]
                if isinstance(v, list) and v:
                    return v[0] if isinstance(v[0], str) else str(v[0])
                return str(v)
    return str(data)

def _call_local_model(prompt: str, max_new_tokens: int = 512) -> str:
    # lightweight local fallback using transformers (model name from HF_MODEL)
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        import torch
    except Exception as e:
        raise RuntimeError("transformers or torch not installed. Install with: pip install transformers torch") from e

    tokenizer = AutoTokenizer.from_pretrained(HF_MODEL)
    model = AutoModelForCausalLM.from_pretrained(HF_MODEL)
    model.eval()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    with torch.no_grad():
        out_ids = model.generate(**inputs, max_new_tokens=max_new_tokens)
    # strip prompt tokens
    generated = tokenizer.decode(out_ids[0][inputs["input_ids"].shape[-1]:], skip_special_tokens=True)
    return generated

def _build_fallback_story(theme: str) -> str:
    story = {
        "title": f"The {theme.title()} Case",
        "rootNode": {
            "content": f"You arrive in a world shaped by {theme}.",
            "isEnding": False,
            "isWinningEnding": False,
            "options": [
                {
                    "text": "Investigate the strange clue",
                    "nextNode": {
                        "content": "The clue leads you to a hidden chamber.",
                        "isEnding": False,
                        "isWinningEnding": False,
                        "options": [
                            {
                                "text": "Open the glowing door",
                                "nextNode": {
                                    "content": "You solve the mystery and uncover the truth.",
                                    "isEnding": True,
                                    "isWinningEnding": True,
                                    "options": []
                                }
                            },
                            {
                                "text": "Walk away",
                                "nextNode": {
                                    "content": "The trail goes cold and the mystery remains unsolved.",
                                    "isEnding": True,
                                    "isWinningEnding": False,
                                    "options": []
                                }
                            }
                        ]
                    }
                },
                {
                    "text": "Follow the city lights",
                    "nextNode": {
                        "content": "The lights lead you into a risky alley.",
                        "isEnding": True,
                        "isWinningEnding": False,
                        "options": []
                    }
                }
            ]
        }
    }
    return json.dumps(story)

def call_hf_model(prompt: str, max_new_tokens: int = 512, temperature: float = 0.7, timeout: int = 60) -> str:
    # debug: re-read settings and print
    from core.config import settings as _settings
    global HF_MODEL, HF_API_TOKEN
    HF_MODEL = _settings.HF_MODEL
    HF_API_TOKEN = _settings.HF_API_TOKEN
    print("DEBUG call_hf_model HF_MODEL:", HF_MODEL, "HF_API_TOKEN set:", bool(HF_API_TOKEN))

    if not HF_API_TOKEN:
        return _build_fallback_story("adventure")

    client = OpenAI(base_url="https://router.huggingface.co/v1", api_key=HF_API_TOKEN)

    messages = [{"role": "user", "content": prompt}]
    try:
        completion = client.chat.completions.create(
            model=HF_MODEL,
            messages=messages,
            max_tokens=max_new_tokens,
            temperature=temperature,
        )
    except Exception as e:
        print("DEBUG completion error:", e)
        raise RuntimeError(f"Hugging Face Router chat completion failed: {e}")

    # robust extraction of text
    choice = None
    if hasattr(completion, "choices") and completion.choices:
        choice = completion.choices[0]
    elif isinstance(completion, dict) and completion.get("choices"):
        choice = completion["choices"][0]

    if not choice:
        return str(completion)

    msg = getattr(choice, "message", None) or (choice.get("message") if isinstance(choice, dict) else None)
    if not msg:
        text = getattr(choice, "text", None) or (choice.get("text") if isinstance(choice, dict) else None)
        return text if text is not None else str(choice)

    # message content can be str, dict with 'content' or list structures
    content = None
    if isinstance(msg, dict):
        if "content" in msg:
            c = msg["content"]
            if isinstance(c, str):
                content = c
            elif isinstance(c, list) and c:
                # support list of fragments or objects
                if isinstance(c[0], str):
                    content = c[0]
                elif isinstance(c[0], dict):
                    # common structure: {"type":"output_text","text":"..."}
                    content = c[0].get("text") or next((it.get("text") for it in c if isinstance(it, dict) and it.get("text")), None)
        elif "text" in msg:
            content = msg["text"]
    else:
        content = getattr(msg, "content", None) or getattr(msg, "text", None)

    return content if content is not None else str(completion)

class StoryGenerator:

    @classmethod
    def generate_story(cls, db: Session, session_id: str, theme: str = "fantasy") -> Story:
        story_parser = PydanticOutputParser(pydantic_object=StoryLLMRepsonse)
        format_instructions = story_parser.get_format_instructions()

        # Compose a single prompt string for the HF model
        prompt = (
            f"{STORY_PROMPT}\n\n"
            f"Format instructions:\n{format_instructions}\n\n"
            f"Human: create the story with this theme: {theme}\n\n"
            f"Please follow the format instructions exactly."
        )

        raw_text = call_hf_model(prompt)
        # parse with pydantic parser
        story_structure = story_parser.parse(raw_text)

        story_db = Story(title=story_structure.title, session_id=session_id)
        db.add(story_db)
        db.flush()

        root_node_data = story_structure.rootNode
        if isinstance(root_node_data, dict):
            root_node_data = StoryNodeLLM.model_validate(root_node_data)

        cls._process_story_node(db, story_db.id, root_node_data, is_root=True)
        db.commit()
        return story_db

    @classmethod
    def _get_attr(cls, obj, *names, default=None):
        for n in names:
            if hasattr(obj, n):
                return getattr(obj, n)

    @classmethod
    def _process_story_node(cls, db: Session, story_id: int, node_data: StoryNodeLLM, is_root: bool = False) -> StoryNode:
        content = cls._get_attr(node_data, "content", "text", default="")
        is_ending = bool(cls._get_attr(node_data, "isEnding", "is_ending", default=False))
        is_winning = bool(cls._get_attr(node_data, "isWinningEnding", "is_winning_ending", default=False))

        node = StoryNode(
            story_id=story_id,
            content=content,
            is_root=is_root,
            is_ending=is_ending,
            is_winning_ending=is_winning,
            options=[]
        )
        db.add(node)
        db.flush()

        options_list = []
        options_data = cls._get_attr(node_data, "options", default=[]) or []
        if not is_ending and options_data:
            for option_data in options_data:
                opt_text = cls._get_attr(option_data, "text", "option_text", default="")
                next_node = cls._get_attr(option_data, "nextNode", "next_node", default=None)
                if next_node is None:
                    continue
                if isinstance(next_node, dict):
                    next_node = StoryNodeLLM.model_validate(next_node)
                child_node = cls._process_story_node(db, story_id, next_node, is_root=False)
                options_list.append({"text": opt_text, "node_id": child_node.id})

        node.options = options_list
        db.flush()
        return node
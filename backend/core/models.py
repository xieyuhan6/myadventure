from typing import List, Optional, Any
from pydantic import BaseModel, Field

class StoryOptionLLM(BaseModel):
    text: str = Field("", description="Option text shown to the player")
    # accept either camelCase or snake_case shapes from the LLM
    option_text: Optional[str] = None
    nextNode: Optional["StoryNodeLLM"] = None
    next_node: Optional[Any] = None

class StoryNodeLLM(BaseModel):
    content: str = Field("", description="Node content/text")
    # make ending flags optional with defaults and accept both naming styles
    isEnding: bool = Field(False, alias="isEnding")
    isWinningEnding: bool = Field(False, alias="isWinningEnding")
    is_ending: bool = Field(False, alias="is_ending")
    is_winning_ending: bool = Field(False, alias="is_winning_ending")
    options: List[StoryOptionLLM] = Field(default_factory=list)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

# resolve forward refs
StoryOptionLLM.update_forward_refs()

class StoryLLMRepsonse(BaseModel):
    title: str = Field("", description="Story title")
    # accept either camelCase or snake_case for the root node
    rootNode: Optional[StoryNodeLLM] = Field(None, alias="rootNode")
    root_node: Optional[StoryNodeLLM] = Field(None, alias="root_node")

    # pydantic v2-compatible config (keeps backward behavior)
    model_config = {"validate_by_name": True}

# ensure forward refs include the new model
StoryOptionLLM.update_forward_refs()
StoryNodeLLM.update_forward_refs()
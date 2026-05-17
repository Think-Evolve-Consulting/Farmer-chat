"""Anthropic API integration for chat responses."""
from anthropic import Anthropic

from .config import config
from .retriever import ContextRetriever
from .conversation_logger import ConversationLogger


SYSTEM_PROMPT = """You are an AI assistant helping farmers with their questions.
You have access to historical chat transcripts from farming communities AND agricultural product catalogs.
Use the provided context to give relevant, practical advice and recommend suitable products.

Guidelines:
- Draw from the context provided when relevant.
- Be practical and actionable in your advice.
- 💡 PRODUCT RECOMMENDATION: If the context contains product information relevant to the user's farming problem, explicitly suggest these products to the user. Format the product names in **bold**.
- If the context doesn't contain relevant information, say so and provide general guidance.
- Use farming terminology appropriately.
- Be friendly and supportive.

When answering:
1. First check if the context contains relevant advice or products.
2. Reference specific advice from past conversations when applicable.
3. Recommend specific products from the context if they address the farmer's issue.
4. Add your own knowledge to supplement the context.
5. Be clear about what comes from the retrieved data vs general knowledge."""


class FarmerChatClient:
    """Chat client integrating retrieval with Anthropic's Claude."""
    
    def __init__(
        self,
        retriever: ContextRetriever = None,
        api_key: str = None,
        logger: ConversationLogger = None
    ):
        """
        Initialize the chat client.

        Args:
            retriever: Context retriever instance
            api_key: Anthropic API key
            logger: Conversation logger instance
        """
        self.retriever = retriever or ContextRetriever()
        self.client = Anthropic(api_key=api_key or config.anthropic_api_key)
        self.conversation_history: list[dict] = []
        self.logger = logger
    
    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.conversation_history = []
    
    def chat(self, user_message: str, include_context: bool = True) -> tuple[str, list[dict]]:
        """
        Send a message and get a response.

        Args:
            user_message: The user's message
            include_context: Whether to retrieve and include context

        Returns:
            Tuple containing (Claude's response text, list of retrieved context chunks)
        """
        # Retrieve relevant context
        context = ""
        results = []
        if include_context:
            results = self.retriever.retrieve(user_message)
            context = self.retriever.format_context(results)

        # Build the message with context
        if context and context != "No relevant context found.":
            enhanced_message = (
                f"User Question: {user_message}\n\n"
                f"Relevant Context from Farmer Chat Transcripts:\n{context}"
            )
        else:
            enhanced_message = f"User Question: {user_message}"

        # Prepare the current turn with context for the API call
        current_turn = {"role": "user", "content": enhanced_message}
        messages_for_api = self.conversation_history + [current_turn]

        # Add the raw user message to history to save tokens on future turns
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Call Claude API
        response = self.client.messages.create(
            model=config.claude_model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=messages_for_api
        )

        # Extract response text
        assistant_message = response.content[0].text

        # Add response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        # Log the interaction
        if self.logger:
            self.logger.log_interaction(
                query=user_message,
                response=assistant_message,
                context_results=results
            )

        return assistant_message, results
    
    def get_context_only(self, query: str) -> list[dict]:
        """
        Get retrieved context without generating a response.
        
        Args:
            query: The search query
            
        Returns:
            List of retrieved chunks
        """
        return self.retriever.retrieve(query)
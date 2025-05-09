import os
import logging
from typing import Dict, Optional
from groq import Groq
from config.settings import settings

logger = logging.getLogger(__name__)

class LLMIntegration:
    """
    Integration with Groq LLM service.
    This class provides:
    1. Text generation using Groq's language models
    2. Task analysis and structured information extraction
    3. Error handling and logging for LLM operations
    """
    
    def __init__(self, config: Dict = None):
        """
        Initialize the LLM integration.
        This sets up the Groq client with API key and model configuration.
        
        Args:
            config: LLM configuration containing:
                   - api_key: Groq API key
                   - model: Model name to use (e.g., 'llama2-70b-4096')
        """
        self.config = config or {}
        self.api_key = self.config.get('api_key', settings.GROQ_API_KEY)
        self.model = self.config.get('model', settings.GROQ_MODEL)
        
        # Initialize Groq client with API key
        self.client = Groq(api_key=self.api_key)
        logger.info(f"Initialized Groq LLM integration with model: {self.model}")
    
    def generate_response(self, prompt: str, max_tokens: int = 1000) -> Optional[str]:
        """
        Generate a response using the LLM.
        This method:
        1. Creates a chat completion request
        2. Uses a system message to set context
        3. Processes the user's prompt
        4. Returns the generated response
        
        Args:
            prompt: Input prompt for the LLM
            max_tokens: Maximum number of tokens to generate in response
            
        Returns:
            Optional[str]: Generated response text if successful, None if failed
        """
        try:
            # Create chat completion with system and user messages
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7,  # Controls randomness (0.0 = deterministic, 1.0 = creative)
                top_p=0.95,      # Controls diversity via nucleus sampling
                stream=False     # Get complete response at once
            )
            
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}", exc_info=True)
            return None
    
    def analyze_task(self, task_description: str) -> Optional[Dict]:
        """
        Analyze a task description using the LLM.
        This method:
        1. Creates a structured prompt for task analysis
        2. Generates a response using the LLM
        3. Parses the response into structured data
        4. Returns analysis results
        
        Args:
            task_description: Description of the task to analyze
            
        Returns:
            Optional[Dict]: Analysis results containing:
                          - required_capabilities: List of needed capabilities
                          - resource_requirements: Dictionary of resource needs
                          - priority_level: Task priority (1-5)
                          - challenges: List of potential challenges
        """
        try:
            # Create structured prompt for task analysis
            prompt = f"""
            Analyze the following task and provide structured information:
            Task: {task_description}
            
            Provide the analysis in the following format:
            1. Required capabilities
            2. Estimated resource requirements
            3. Priority level (1-5)
            4. Potential challenges
            """
            
            # Generate response from LLM
            response = self.generate_response(prompt)
            if not response:
                return None
            
            # Parse the response into structured data
            lines = response.strip().split('\n')
            analysis = {
                'required_capabilities': [],
                'resource_requirements': {},
                'priority_level': 3,  # Default priority
                'challenges': []
            }
            
            # Process each line of the response
            current_section = None
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Identify current section
                if 'Required capabilities' in line:
                    current_section = 'capabilities'
                elif 'Estimated resource requirements' in line:
                    current_section = 'resources'
                elif 'Priority level' in line:
                    current_section = 'priority'
                elif 'Potential challenges' in line:
                    current_section = 'challenges'
                elif current_section:
                    # Process line based on current section
                    if current_section == 'capabilities':
                        analysis['required_capabilities'].append(line.strip('- '))
                    elif current_section == 'resources':
                        if ':' in line:
                            key, value = line.split(':', 1)
                            analysis['resource_requirements'][key.strip()] = value.strip()
                    elif current_section == 'priority':
                        try:
                            priority = int(line.strip().split()[0])
                            if 1 <= priority <= 5:
                                analysis['priority_level'] = priority
                        except (ValueError, IndexError):
                            pass
                    elif current_section == 'challenges':
                        analysis['challenges'].append(line.strip('- '))
            
            return analysis
        except Exception as e:
            logger.error(f"Error analyzing task: {e}", exc_info=True)
            return None 
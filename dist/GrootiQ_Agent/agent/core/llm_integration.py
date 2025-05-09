import os
import logging
from typing import Dict, Optional
from groq import Groq
from config.settings import settings

logger = logging.getLogger(__name__)

class LLMIntegration:
    """Integration with Groq LLM service."""
    
    def __init__(self, config: Dict = None):
        """
        Initialize the LLM integration.
        
        Args:
            config: LLM configuration
        """
        self.config = config or {}
        self.api_key = self.config.get('api_key', settings.GROQ_API_KEY)
        self.model = self.config.get('model', settings.GROQ_MODEL)
        
        # Initialize Groq client
        self.client = Groq(api_key=self.api_key)
        logger.info(f"Initialized Groq LLM integration with model: {self.model}")
    
    def generate_response(self, prompt: str, max_tokens: int = 1000) -> Optional[str]:
        """
        Generate a response using the LLM.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            Generated response or None if failed
        """
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7,
                top_p=0.95,
                stream=False
            )
            
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}", exc_info=True)
            return None
    
    def analyze_task(self, task_description: str) -> Optional[Dict]:
        """
        Analyze a task description using the LLM.
        
        Args:
            task_description: Description of the task
            
        Returns:
            Analysis results or None if failed
        """
        try:
            prompt = f"""
            Analyze the following task and provide structured information:
            Task: {task_description}
            
            Provide the analysis in the following format:
            1. Required capabilities
            2. Estimated resource requirements
            3. Priority level (1-5)
            4. Potential challenges
            """
            
            response = self.generate_response(prompt)
            if not response:
                return None
            
            # Parse the response into structured data
            lines = response.strip().split('\n')
            analysis = {
                'required_capabilities': [],
                'resource_requirements': {},
                'priority_level': 3,  # Default
                'challenges': []
            }
            
            current_section = None
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if 'Required capabilities' in line:
                    current_section = 'capabilities'
                elif 'Estimated resource requirements' in line:
                    current_section = 'resources'
                elif 'Priority level' in line:
                    current_section = 'priority'
                elif 'Potential challenges' in line:
                    current_section = 'challenges'
                elif current_section:
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
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Image Generator Module

This module handles interactions with the SanaSprint AI image generation API.
"""

import os
import logging
import time
import base64
from typing import Optional, Dict, Any
from pathlib import Path

from gradio_client import Client
from PIL import Image

logger = logging.getLogger(__name__)

class SanaSprintGenerator:
    """Client for interacting with the SanaSprint image generation API."""
    
    def __init__(self, model_size: str = "1.6B", width: int = 512, height: int = 512,
                 guidance_scale: float = 4.5, num_inference_steps: int = 2):
        """
        Initialize the image generator client.
        
        Args:
            model_size: Size of the AI model to use
            width: Width of the generated image
            height: Height of the generated image
            guidance_scale: Guidance scale parameter for image generation
            num_inference_steps: Number of inference steps
        """
        self.client = Client("Efficient-Large-Model/SanaSprint")
        self.model_size = model_size
        self.width = width
        self.height = height
        self.guidance_scale = guidance_scale
        self.num_inference_steps = num_inference_steps
    
    def _convert_to_data_url(self, image_path: str) -> str:
        """
        Convert a local image file to a data URL.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Data URL string
        """
        try:
            # Check if the path exists
            if not os.path.exists(image_path):
                logger.error(f"Image file not found: {image_path}")
                return "ERROR: Image file not found"
            
            # Get the image format
            img_format = Path(image_path).suffix.lstrip(".").lower()
            if img_format == "webp":
                img_format = "webp"
            elif img_format == "jpg" or img_format == "jpeg":
                img_format = "jpeg"
            elif img_format == "png":
                img_format = "png"
            else:
                # Convert to PNG for unsupported formats
                img = Image.open(image_path)
                png_path = image_path.rsplit(".", 1)[0] + ".png"
                img.save(png_path, "PNG")
                image_path = png_path
                img_format = "png"
            
            # Read the file and convert to base64
            with open(image_path, "rb") as f:
                img_data = base64.b64encode(f.read()).decode("utf-8")
            
            # Create the data URL
            data_url = f"data:image/{img_format};base64,{img_data}"
            return data_url
            
        except Exception as e:
            logger.error(f"Error converting image to data URL: {str(e)}")
            return "ERROR: Failed to convert image"
    
    def generate_image(self, prompt: str, randomize_seed: bool = True, seed: int = 0) -> str:
        """
        Generate an image based on the provided prompt.
        
        Args:
            prompt: The text prompt to generate an image from
            randomize_seed: Whether to use a random seed
            seed: The seed to use if not randomizing
            
        Returns:
            URL of the generated image
        """
        logger.info(f"Generating image with prompt: {prompt}")
        
        try:
            # Ensure prompt isn't empty
            if not prompt or prompt.strip() == "":
                prompt = "Simple illustration"
                logger.warning(f"Empty prompt detected, using default: {prompt}")
                
            # For very long prompts, truncate to avoid issues
            if len(prompt) > 500:
                prompt = prompt[:497] + "..."
                logger.warning(f"Prompt truncated due to length: {prompt}")
            
            result = self.client.predict(
                prompt=prompt,
                model_size=self.model_size,
                seed=seed,
                randomize_seed=randomize_seed,
                width=self.width,
                height=self.height,
                guidance_scale=self.guidance_scale,
                num_inference_steps=self.num_inference_steps,
                api_name="/infer"
            )
            
            # Handle different result formats
            if isinstance(result, tuple) and len(result) >= 1:
                # If the result is a tuple (filepath, file_id)
                image_path = result[0]
                logger.info(f"Successfully generated image: {result}")
                
                # Convert local file to data URL for embedding in spreadsheet
                return self._convert_to_data_url(image_path)
            
            elif isinstance(result, list) and len(result) >= 1:
                # If the API returns a list, take the first item
                image_result = result[0]
                
                # Check if it's a local path
                if isinstance(image_result, str) and (image_result.startswith("/") or ":\\" in image_result):
                    return self._convert_to_data_url(image_result)
                
                return image_result
            
            else:
                # Otherwise, assume the result is the image URL or path
                if isinstance(result, str) and (result.startswith("/") or ":\\" in result):
                    return self._convert_to_data_url(result)
                
                return result
                
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            raise Exception(f"Failed to generate image: {str(e)}")
    
    def generate_image_with_params(self, params: Dict[str, Any]) -> str:
        """
        Generate an image with custom parameters.
        
        Args:
            params: Dictionary of parameters to override defaults
            
        Returns:
            URL of the generated image
        """
        prompt = params.get("prompt")
        if not prompt:
            raise ValueError("Prompt is required for image generation")
            
        model_size = params.get("model_size", self.model_size)
        width = params.get("width", self.width)
        height = params.get("height", self.height)
        guidance_scale = params.get("guidance_scale", self.guidance_scale)
        num_inference_steps = params.get("num_inference_steps", self.num_inference_steps)
        randomize_seed = params.get("randomize_seed", True)
        seed = params.get("seed", 0)
        
        try:
            result = self.client.predict(
                prompt=prompt,
                model_size=model_size,
                seed=seed,
                randomize_seed=randomize_seed,
                width=width,
                height=height,
                guidance_scale=guidance_scale,
                num_inference_steps=num_inference_steps,
                api_name="/infer"
            )
            
            # Handle result same as in generate_image
            if isinstance(result, tuple) and len(result) >= 1:
                image_path = result[0]
                return self._convert_to_data_url(image_path)
            
            elif isinstance(result, list) and len(result) >= 1:
                image_result = result[0]
                if isinstance(image_result, str) and (image_result.startswith("/") or ":\\" in image_result):
                    return self._convert_to_data_url(image_result)
                return image_result
            
            else:
                if isinstance(result, str) and (result.startswith("/") or ":\\" in result):
                    return self._convert_to_data_url(result)
                return result
                
        except Exception as e:
            logger.error(f"Error generating image with custom params: {str(e)}")
            raise Exception(f"Failed to generate image with custom params: {str(e)}") 
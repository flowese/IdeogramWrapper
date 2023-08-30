"""
Ideogram Wrapper
Author: Flowese
Version: 0.0.2
Date: 2023-02-30
Description: Generates images from Ideogram API using textual prompts.
"""

import os
import re
import requests
import shutil
import logging
from time import sleep
from datetime import datetime, timedelta

class IdeogramWrapper:
    BASE_URL = "https://ideogram.ai/api/images"
    
    def __init__(
        self,
        session_cookie_token,
        prompt, 
        user_id="-xnquyqCVSFOYTomOeUchbw",  # Argumento con valor predeterminado
        channel_id="LbF4xfurTryl5MUEZ73bDw",
        aspect_ratio="square",
        output_dir="images", 
        enable_logging=False):
    
        if not session_cookie_token:
            raise ValueError("Session cookie token is not defined.")
        if not prompt:
            raise ValueError("Prompt is not defined.")

        self.user_id = user_id
        self.channel_id = channel_id
        self.session_cookie_token = session_cookie_token
        self.prompt = prompt
        self.aspect_ratio = aspect_ratio
        self.output_dir = output_dir
        self.enable_logging = enable_logging

        if self.enable_logging:
            logging.basicConfig(format='[%(asctime)s] [%(levelname)s]: %(message)s', 
                                level=logging.INFO, datefmt='%H:%M:%S')
            logging.info("IdeogramWrapper initialized.")

    def fetch_generation_metadata(self, request_id):
        url = f"{self.BASE_URL}/retrieve_metadata_request_id/{request_id}"
        headers, cookies = self.get_request_params()
        
        try:
            response = requests.get(url, headers=headers, cookies=cookies)
            response.raise_for_status()

            data = response.json()
            if data.get("resolution") == 1024:
                if self.enable_logging:
                    logging.info("Receiving image data...")
                return data
        except requests.RequestException as e:
            logging.error(f"An error occurred: {e}")
        return None

    def inference(self):
        url = f"{self.BASE_URL}/sample"
        headers, cookies = self.get_request_params()
        
        payload = {
            "aspect_ratio": self.aspect_ratio,
            "channel_id": self.channel_id,
            "prompt": self.prompt,
            "raw_or_fun": "raw",
            "speed": "slow",
            "style": "photo",
            "user_id": self.user_id
        }
        
        try:
            response = requests.post(url, headers=headers, 
                                    cookies=cookies, json=payload)
            response.raise_for_status()

            request_id = response.json().get("request_id")
            if self.enable_logging:
                logging.info("Generation request sent. Waiting for response...")
            self.make_get_request(request_id)
        except requests.RequestException as e:
            logging.error(f"An error occurred: {e}")

    def make_get_request(self, request_id):
        end_time = datetime.now() + timedelta(minutes=5)
        
        while datetime.now() < end_time:
            image_data = self.fetch_generation_metadata(request_id)
            if image_data:
                self.download_images(image_data.get("responses", []))
                return
            sleep(1)

    def download_images(self, responses):
        headers, cookies = self.get_request_params()
        
        for i, response in enumerate(responses):
            image_url = f"{self.BASE_URL}/direct/{response['response_id']}"
            file_path = self.download_image(image_url, headers, cookies, i)
            
        if file_path and self.enable_logging:
            logging.info(f"Successfully downloaded {len(responses)} images to {self.output_dir}.")

    def download_image(self, image_url, headers, cookies, index):
        os.makedirs(self.output_dir, exist_ok=True)

        sanitized_prompt = re.sub(r'[^\w\s\'-]', '', self.prompt).replace(' ', '_')
        file_path = os.path.join(self.output_dir, f"{sanitized_prompt}_{index}.jpeg")
        
        try:
            response = requests.get(image_url, headers=headers, 
                                    cookies=cookies, stream=True)
            response.raise_for_status()

            with open(file_path, "wb") as f:
                shutil.copyfileobj(response.raw, f)
            return file_path
        except requests.RequestException as e:
            logging.error(f"An error occurred: {e}")
        return None
    
    def get_request_params(self):
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
        cookies = {
            "session_cookie": self.session_cookie_token
        }
        return headers, cookies
# Backend
Endpoint get_images takes in a song file and returns generated cover art images for them

# Setup
install pipreqs
`pip install pipreqs`

install requirements from requirements.txt
`pip install -r requirements.txt`

if you add more requirements in your code, update requirements.txt
`pipreqs . --force`

create a .env file
`touch .env`

add openAI api key to .env file
`OPENAI_KEY=your_api_key`

# Change your configuration
Go to your configuration (config/yourname.py) file and update code in each function according to doc strings.

import all functions from your configuration in server.py
`from config.yourname import *`

or mix and match function from different configurations by importing them individually

```
from config.default import extract_lyrics, extract_themes, generate_prompts, generate_images
from config.yourname import extract_emotion, GPT_PROMPT
```

Make sure you import all required functions: extract_lyrics, extract_themes, generate_prompts, generate_images, extract_emotion, GPT_PROMPT

# Run the backend
`python3 server.py`

# Test functionality using postman
![postman](https://github.com/CSCI-534/backend/blob/c48e6ca9ef810737a9d68fc271f98fe2904b4310/Screenshot%202023-04-03%20at%202.29.51%20PM.png)

Navigate to body -> form-data and upload a song file with the key "song"

Send POST request to the url http://127.0.0.1:5000/get_images





# AI Integration Setup

The TTRPG DM Toolkit includes AI-powered content generation features, starting with NPC randomization. This document explains how to set up AI integration for both local testing and cloud API usage.

## Quick Start

The AI system supports three methods:
1. **Local Model** (Recommended for testing) - Free, private, runs on your machine
2. **OpenAI API** - Requires API key, pay-per-use
3. **Anthropic Claude API** - Requires API key, pay-per-use

## Local AI Model Setup (Recommended for Testing)

### Prerequisites
- At least 8GB RAM (16GB recommended)
- ~20GB free disk space
- Python 3.8+ (if not using Ollama)

### Option 1: Using Ollama (Easiest)

1. **Install Ollama**
   ```bash
   # macOS
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Or download from https://ollama.ai
   ```

2. **Download the Model**
   ```bash
   # Recommended models (choose one):
   
   # Llama 3.1 8B (fast, good quality, ~4.7GB)
   ollama pull llama3.1:8b
   
   # Llama 3.2 3B (smaller, faster, ~2GB)
   ollama pull llama3.2:3b
   
   # Mistral 7B (alternative, good for creative content)
   ollama pull mistral:7b
   
   # Note: OpenAI's gpt-oss models may not be available via Ollama yet
   # We'll use Llama 3.1 as the default for now
   ```

3. **Start Ollama Service**
   ```bash
   ollama serve
   ```

4. **Verify Setup**
   ```bash
   curl http://localhost:11434/api/tags
   ```

### Option 2: Alternative Local Setup

If you prefer not to use Ollama, you can run the model directly:

1. **Install Required Libraries**
   ```bash
   pip install transformers torch accelerate
   ```

2. **Create a Simple Server** (example script)
   ```python
   # local_ai_server.py
   from transformers import AutoTokenizer, AutoModelForCausalLM
   import torch
   from flask import Flask, request, jsonify
   
   app = Flask(__name__)
   
   # Load model (this will take a while the first time)
   model_name = "openai/gpt-oss-20b"  # or similar
   tokenizer = AutoTokenizer.from_pretrained(model_name)
   model = AutoModelForCausalLM.from_pretrained(
       model_name, 
       torch_dtype=torch.float16,
       device_map="auto"
   )
   
   @app.route("/generate", methods=["POST"])
   def generate():
       data = request.json
       prompt = data.get("prompt", "")
       
       inputs = tokenizer.encode(prompt, return_tensors="pt")
       with torch.no_grad():
           outputs = model.generate(
               inputs,
               max_length=inputs.size(1) + data.get("max_tokens", 500),
               temperature=data.get("temperature", 0.7),
               do_sample=True,
               pad_token_id=tokenizer.eos_token_id
           )
       
       response = tokenizer.decode(outputs[0], skip_special_tokens=True)
       response = response[len(prompt):]  # Remove prompt from response
       
       return jsonify({"response": response})
   
   if __name__ == "__main__":
       app.run(host="0.0.0.0", port=11434)
   ```

3. **Run the Server**
   ```bash
   python local_ai_server.py
   ```

## Cloud API Setup

### OpenAI API Setup

1. **Get API Key**
   - Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
   - Create a new API key
   - Add billing information if needed

2. **Configure Environment**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

   Or set it in your `.env` file:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

### Anthropic Claude API Setup

1. **Get API Key**
   - Go to [Anthropic Console](https://console.anthropic.com/)
   - Create a new API key
   - Add billing information

2. **Configure Environment**
   ```bash
   export ANTHROPIC_API_KEY="your-api-key-here"
   ```

   Or set it in your `.env` file:
   ```
   ANTHROPIC_API_KEY=your-api-key-here
   ```

## Testing the Setup

1. **Start your backend server**
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn app.main:app --reload
   ```

2. **Check AI Status**
   ```bash
   curl http://localhost:8000/ai/status
   ```

   You should see:
   ```json
   {
     "available": true,
     "providers": ["local"]  // or ["openai"], ["anthropic"], etc.
   }
   ```

3. **Test NPC Generation**
   - Open the frontend application
   - Go to any campaign
   - Click "NPCs" → "Create New NPC"
   - Click the "Randomize" button next to the title
   - The form should populate with AI-generated NPC data

## Troubleshooting

### Local Model Issues

**"Model not found" error:**
```bash
# Check available models
ollama list

# Pull the model if missing
ollama pull llama3.1:8b
```

**"Connection refused" error:**
```bash
# Make sure Ollama is running
ollama serve

# Check if the service is up
curl http://localhost:11434/api/tags
```

**Out of memory errors:**
- Try a smaller model: `ollama pull llama3.1:8b` instead of larger models
- Increase your system's virtual memory/swap
- Close other memory-intensive applications

### API Issues

**"Invalid API key" error:**
- Double-check your API key in the environment variables
- Make sure you have billing set up for OpenAI/Anthropic
- Verify the key has the necessary permissions

**"Rate limit exceeded" error:**
- Wait a few minutes before trying again
- Check your API usage limits
- Consider upgrading your API plan

## Performance Tips

1. **Local Models:**
   - Use GPU acceleration if available (CUDA/Metal)
   - Larger models give better results but use more resources
   - Keep the model service running to avoid startup delays

2. **Cloud APIs:**
   - OpenAI GPT-3.5-turbo is fast and cost-effective
   - Claude Haiku is faster, Claude Sonnet gives better quality
   - Monitor your API usage to control costs

## Security Notes

- **Never commit API keys** to version control
- Use environment variables or secure secret management
- Local models keep all data on your machine (more private)
- Cloud APIs send prompts to external services (check their privacy policies)

## Current Features

✅ **Available Now:**
- NPC randomization with full character details
- Fallback system (tries local → OpenAI → Anthropic → predefined template)
- Smart error handling

🚧 **Coming Soon:**
- Campaign-aware generation (uses existing world data)
- Randomizer buttons for locations, organizations, plot hooks, etc.
- Selective field randomization
- Custom prompt templates

For questions or issues, please check the main README or open an issue in the repository.
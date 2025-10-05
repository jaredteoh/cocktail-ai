# CocktAIl 🍸 - Your AI Cocktail Assistant

An intelligent cocktail recommendation system that generates personalized cocktail recipes based on your available ingredients and mood preferences. Built with Retrieval Augmented Generation (RAG) using cocktail recipe books as a knowledge base, the application provides accurate, creative drink suggestions while avoiding LLM hallucinations.

## 🎯 Features

- **Smart Inventory Management**: Organize ingredients by category (Base Spirits, Liqueurs, Bitters, Mixers, Garnishes)
- **Mood-Based Recommendations**: Describe what you're craving (e.g., "something sweet and refreshing") and get tailored suggestions
- **RAG-Enhanced Accuracy**: Uses vector database of cocktail recipe books to ground recommendations in real recipes
- **Flexible Measurements**: Toggle between metric (ml) and imperial (oz) units
- **Ingredient Normalization**: Automatically handles variations in ingredient names and deduplicates entries
- **Session Persistence**: Maintains your inventory across interactions

## 🛠️ Technologies Used

- **LLM Framework**: LangChain for prompt management and chain orchestration
- **Language Model**: Llama 3 (via Ollama) for natural language understanding and generation
- **Vector Database**: [ChromaDB/FAISS/Pinecone - specify which you used] for cocktail recipe storage and retrieval
- **Frontend**: Streamlit for interactive web application
- **Python Libraries**: `langchain`, `langchain-community`, `streamlit`

## 🏗️ Architecture

### RAG Implementation

```
User Input (Mood/Preferences + Inventory)
            ↓
    Query Embedding
            ↓
Vector DB Retrieval (Cocktail Recipe Books)
            ↓
    Relevant Recipes Retrieved
            ↓
Context + User Prompt → LLM (Llama 3)
            ↓
Personalized Cocktail Recommendations
```

**Key Components**:
1. **Retrieval**: Searches vector database of cocktail recipes based on user's mood and available ingredients
2. **Augmentation**: Injects retrieved recipes as context to ground the LLM's responses
3. **Generation**: LLM creates personalized recommendations using real recipe knowledge

### Why RAG?

Traditional LLMs might hallucinate cocktail recipes or suggest non-existent combinations. By grounding recommendations in a curated cocktail recipe database, CocktAIl ensures:
- Accurate ingredient proportions
- Authentic cocktail names and recipes
- Proper mixing techniques
- Realistic flavor profiles

## 📋 Prerequisites

- Python 3.8+
- Ollama installed locally with Llama 3 model
- [Vector database setup - specify your choice]

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/jaredteoh/cocktail-ai.git
cd cocktail-ai
```

2. Install required dependencies:
```bash
pip install streamlit langchain langchain-community
# Add other dependencies based on your vector DB choice
```

3. Install and start Ollama with Llama 3:
```bash
ollama pull llama3
```

4. Set up the vector database:
```bash
# Add instructions for loading cocktail recipe embeddings
python setup_vector_db.py  # if applicable
```

## 💻 Usage

1. Start the Streamlit application:
```bash
streamlit run app.py
```

2. Open your browser to `http://localhost:8501`

3. **Build Your Inventory**:
   - Navigate to the "Inventory" tab
   - Select ingredients from each category
   - Click "Save Inventory"

4. **Get Recommendations**:
   - Switch to "Cocktail Suggestions" tab
   - Describe your mood or preference (e.g., "I want something fruity and tropical")
   - Choose your preferred unit (ml or oz)
   - Click "Suggest Cocktails"

5. View personalized cocktail recipes based on your available ingredients!

## 📁 Project Structure

```
cocktail-ai/
│
├── app.py                    # Main Streamlit application
├── llm_utils.py             # LLM initialization and chain building
├── inventory_utils.py       # Ingredient management utilities
├── vector_db/               # Cocktail recipe embeddings
│   └── cocktail_books.db    # Vector database file
├── data/
│   └── ingredients.json     # Ingredient categories and lists
├── requirements.txt         # Python dependencies
└── README.md               # Project documentation
```

## 🔑 Key Components

### `llm_utils.py`
- `get_llm()`: Initializes Ollama LLM with Llama 3
- `build_chain()`: Constructs LangChain with RAG retrieval and prompt templates

### `inventory_utils.py`
- `ingredient_section()`: Creates UI for ingredient category selection
- `dedupe_and_normalize()`: Handles ingredient name variations
- `convert_units()`: Converts between ml and oz measurements
- `display_inventory_by_category()`: Organizes and displays saved inventory

### Prompt Engineering
The system uses carefully crafted prompts to:
- Match cocktails to user's mood/preference description
- Filter recipes based on available ingredients
- Suggest creative variations when exact matches aren't possible
- Provide clear, step-by-step mixing instructions

## 🎨 Example Use Cases

**Use Case 1: Classic Cocktail**
- **Input**: "I want a strong, sophisticated drink"
- **Inventory**: Gin, Vermouth, Bitters
- **Output**: Classic Martini recipe with proper ratios and garnish suggestions

**Use Case 2: Mood-Based**
- **Input**: "Something sweet and tropical for a beach party"
- **Inventory**: Rum, Pineapple Juice, Coconut Cream, Lime
- **Output**: Piña Colada with variations based on available ingredients

**Use Case 3: Limited Inventory**
- **Input**: "What can I make that's refreshing?"
- **Inventory**: Vodka, Lime, Soda Water
- **Output**: Vodka Soda with lime, plus creative suggestions using similar ingredients

## 🚧 Future Enhancements

- [ ] Add image generation for cocktail visualization
- [ ] Implement user ratings and feedback system
- [ ] Expand vector database with more cocktail books and recipes
- [ ] Add dietary restriction filters (vegan, low-sugar, etc.)
- [ ] Include difficulty levels for cocktail preparation
- [ ] Add shopping list feature for missing ingredients
- [ ] Support batch cocktail scaling for parties
- [ ] Mobile-responsive design improvements

## 📚 Data Sources

- Cocktail recipe books embedded in vector database
- Standard ingredient classifications from bartending guides
- Community-contributed recipes (if applicable)

## 🤝 Contributing

Contributions are welcome! Please feel free to:
- Submit new cocktail recipes
- Improve ingredient categorization
- Enhance the recommendation algorithm
- Add new features

## 📄 License

This project is open source and available under the MIT License.

## 👤 Author

**Jared Teoh Jie Rui**
- LinkedIn: [linkedin.com/in/jaredteoh0725](https://www.linkedin.com/in/jaredteoh0725/)
- GitHub: [github.com/jaredteoh](https://github.com/jaredteoh)
- Email: teohjared@gmail.com

## 🙏 Acknowledgments

- LangChain for RAG framework
- Ollama for local LLM deployment
- Streamlit for rapid prototyping
- Classic cocktail recipe books for knowledge base

---

*Mixing AI with mixology* 🍹🤖

**Drink Responsibly!**

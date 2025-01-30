# Terraform AI Agent

An intelligent agent that generates Azure Terraform configurations using RAG (Retrieval Augmented Generation) and LangChain. The agent uses GPT-4 to understand infrastructure requirements and generate appropriate Terraform code based on validated templates.

## Features

- 🤖 AI-powered Terraform code generation
- 📝 RAG-based approach using curated templates
- ✅ Input validation and scope checking
- 💬 Interactive chat interface
- 🔍 Smart template selection
- 📦 Supports multiple Azure resources

### Supported Azure Resources

- Virtual Machines
- AKS (Azure Kubernetes Service)
- Storage Accounts
- Virtual Networks
- Load Balancers

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/terraform-ai-agent.git
cd terraform-ai-agent
```

2. Create and activate a virtual environment:
```bash
python -m venv terraform-agent-env
source terraform-agent-env/bin/activate  # On Unix/macOS
# OR
terraform-agent-env\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the project root with:
```
OPENAI_API_KEY=your_api_key_here
```

## Usage

1. Start the application:
```bash
streamlit run app/azure_terraform_agent.py
```

2. Enter your infrastructure requirements in natural language
3. Review the generated Terraform configuration
4. Download and use the generated configuration

## Example Queries

- "Create a virtual machine with 2 cores and attached storage"
- "Set up an AKS cluster with 3 nodes and a load balancer"
- "Deploy a storage account with private endpoints and network rules"
- "Create a virtual network with two subnets for web and database tiers"

## Project Structure

```
terraform-ai-agent/
├── app/
│   ├── azure_terraform_agent.py  # Main application
│   └── rag_engine.py            # RAG implementation
├── templates/
│   ├── vm.tf                    # VM template
│   ├── aks.tf                   # AKS template
│   ├── storage.tf               # Storage template
│   ├── vnet.tf                  # VNet template
│   └── lb.tf                    # Load Balancer template
├── terraform/
│   └── main.tf                  # Base Terraform configuration
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables
└── README.md                    # This file
```

## Technical Details

### RAG Implementation
- Uses LangChain for document processing and retrieval
- Implements semantic search with ChromaDB
- Template chunking with RecursiveCharacterTextSplitter
- OpenAI embeddings for similarity search

### Validation
- Input validation using GPT-4
- Scope checking against supported resources
- Template relevance scoring

## Dependencies

- Python 3.8+
- streamlit>=1.22
- langchain>=0.1.0
- langchain-openai>=0.0.2
- openai>=1.0
- python-dotenv>=0.19
- chromadb>=0.4.22
- tiktoken>=0.5.2

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - feel free to use this project for any purpose.

## Acknowledgments

- OpenAI for GPT-4
- LangChain for the RAG framework
- Streamlit for the UI framework 
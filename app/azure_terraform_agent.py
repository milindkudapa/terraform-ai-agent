import os
import streamlit as st
from dotenv import load_dotenv
from rag_engine import TerraformRAGEngine

# Set page config first
st.set_page_config(
    page_title="Azure Terraform Generator",
    page_icon="🌩️",
    layout="wide"
)

# Load environment variables
load_dotenv()

# Debug: Print the API key (first few characters)
api_key = os.getenv('OPENAI_API_KEY')
if api_key:
    st.sidebar.success(f"API Key loaded (first 10 chars): {api_key[:10]}...")
else:
    st.sidebar.error("No API key found in environment variables")

class AzureTerraformAgent:
    def __init__(self):
        # Ensure OpenAI API key is set
        if not os.getenv('OPENAI_API_KEY'):
            raise ValueError("Missing OPENAI_API_KEY environment variable")
            
        # Initialize RAG engine
        self.template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
        if not os.path.exists(self.template_dir):
            raise FileNotFoundError(f"Template directory not found: {self.template_dir}")
        
        self.rag_engine = TerraformRAGEngine(self.template_dir)

    def generate_terraform(self, user_input: str) -> str:
        """Generate Terraform configuration using RAG approach."""
        return self.rag_engine.generate_terraform(user_input)

# Streamlit UI Component
def azure_terraform_chat():
    st.title("Azure Terraform Generator")
    st.markdown("""
    This tool helps you generate Terraform configurations for Azure infrastructure using AI.
    Simply describe your infrastructure needs, and the AI will generate the appropriate Terraform code.
    
    **Supported Resources:**
    - Virtual Machines
    - AKS (Azure Kubernetes Service)
    - Storage Accounts
    - Virtual Networks
    - Load Balancers
    
    **Example Queries:**
    - "Create a virtual machine with 2 cores and attached storage"
    - "Set up an AKS cluster with 3 nodes and a load balancer"
    - "Deploy a storage account with private endpoints and network rules"
    - "Create a virtual network with two subnets for web and database tiers"
    """)
    
    try:
        agent = AzureTerraformAgent()
    except Exception as e:
        st.error(f"Failed to initialize Azure Terraform Agent: {str(e)}")
        st.stop()
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Describe your Azure infrastructure needs"):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.spinner("Processing your request..."):
            try:
                # Generate Terraform code
                terraform_code = agent.generate_terraform(prompt)
                
                # Display generated code
                with st.chat_message("assistant"):
                    st.markdown("### Generated Terraform Configuration")
                    st.code(terraform_code, language='hcl')
                    
                    # Add download button
                    st.download_button(
                        label="Download Terraform Configuration",
                        data=terraform_code,
                        file_name="main.tf",
                        mime="text/plain"
                    )
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"Generated Terraform Configuration:\n```hcl\n{terraform_code}\n```"
                    })
                    
                    st.info("""
                    To use this configuration:
                    1. Download the generated Terraform file
                    2. Initialize Terraform: `terraform init`
                    3. Review the plan: `terraform plan`
                    4. Apply the configuration: `terraform apply`
                    """)
                            
            except ValueError as e:
                with st.chat_message("assistant"):
                    st.warning(str(e))
                    st.markdown("""
                    Please ensure your query is related to Azure infrastructure deployment and includes supported resources:
                    - Virtual Machines
                    - AKS (Azure Kubernetes Service)
                    - Storage Accounts
                    - Virtual Networks
                    - Load Balancers
                    """)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"⚠️ {str(e)}"
                    })
            except Exception as e:
                st.error(f"Error generating Terraform configuration: {str(e)}")

if __name__ == "__main__":
    azure_terraform_chat() 
import os
from typing import List, Dict, Tuple
import streamlit as st
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

class TerraformRAGEngine:
    def __init__(self, template_dir: str):
        """Initialize the RAG engine with template directory."""
        self.template_dir = template_dir
        
        # Verify API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        
        try:
            self.embeddings = OpenAIEmbeddings()
            # Test the embeddings
            test_result = self.embeddings.embed_query("test")
            if not test_result:
                raise ValueError("Failed to generate embeddings")
        except Exception as e:
            raise ValueError(f"Failed to initialize OpenAI embeddings: {str(e)}")
            
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
        
        try:
            self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
        except Exception as e:
            raise ValueError(f"Failed to initialize ChatOpenAI: {str(e)}")
            
        self.vector_store = None
        self._initialize_vector_store()

    def _validate_query(self, query: str) -> Tuple[bool, str]:
        """
        Validate if the query is related to Azure infrastructure and within scope.
        Returns a tuple of (is_valid, reason).
        """
        validation_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a query validator for an Azure Infrastructure Generator.
            Determine if the user's query is about Azure infrastructure deployment and within the scope of these resources:
            - Virtual Machines
            - AKS (Azure Kubernetes Service)
            - Storage Accounts
            - Virtual Networks
            - Load Balancers

            Respond with only true or false, followed by a brief reason.
            Format: valid: <true/false>
            reason: <brief explanation>

            Examples of valid queries:
            - "Create a virtual machine with 2 cores"
            - "Set up a storage account with private endpoints"
            - "Deploy an AKS cluster with 3 nodes"

            Examples of invalid queries:
            - "What's the weather today?"
            - "Help me with my homework"
            - "How do I cook pasta?"
            """),
            ("human", "{query}")
        ])

        try:
            result = self.llm.invoke(validation_prompt.format(query=query))
            response_lines = result.content.strip().lower().split('\n')
            
            is_valid = False
            reason = "Invalid query format"
            
            for line in response_lines:
                if line.startswith('valid:'):
                    is_valid = 'true' in line.lower()
                elif line.startswith('reason:'):
                    reason = line[7:].strip()
            
            return is_valid, reason
        except Exception as e:
            return False, f"Error validating query: {str(e)}"

    def _load_templates(self) -> List[Document]:
        """Load all Terraform templates as documents."""
        documents = []
        for filename in os.listdir(self.template_dir):
            if filename.endswith('.tf'):
                file_path = os.path.join(self.template_dir, filename)
                with open(file_path, 'r') as f:
                    content = f.read()
                    # Store the template type in metadata
                    template_type = filename.replace('.tf', '')
                    doc = Document(
                        page_content=content,
                        metadata={"source": filename, "type": template_type}
                    )
                    documents.append(doc)
        return documents

    def _initialize_vector_store(self):
        """Initialize the vector store with chunked documents."""
        documents = self._load_templates()
        splits = self.text_splitter.split_documents(documents)
        self.vector_store = Chroma.from_documents(
            documents=splits,
            embedding=self.embeddings
        )

    def _get_relevant_templates(self, query: str) -> List[str]:
        """Get relevant template types based on the query."""
        try:
            template_prompt = ChatPromptTemplate.from_messages([
                ("system", """Analyze the user's infrastructure requirements and identify which Azure resource types are needed.
                Return a comma-separated list of resource types from these options only: virtual_machine, aks, storage, vnet, lb.
                Example: "storage,vnet" if user needs storage and networking."""),
                ("human", "{input}")
            ])
            
            chain = template_prompt | self.llm
            result = chain.invoke({"input": query})
            
            if not result.content:
                return ["virtual_machine", "storage"]  # Default to basic resources if no clear match
                
            return [t.strip() for t in result.content.split(',')]
            
        except Exception as e:
            st.error(f"Error in template selection: {str(e)}")
            return ["virtual_machine", "storage"]  # Default to basic resources on error

    def generate_terraform(self, query: str) -> str:
        """Generate Terraform configuration using RAG."""
        try:
            # First, validate the query
            is_valid, reason = self._validate_query(query)
            if not is_valid:
                raise ValueError(f"Query is out of scope: {reason}")

            # Get relevant template types
            relevant_types = self._get_relevant_templates(query)
            
            # Create a retriever that focuses on relevant templates
            retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={
                    "k": 5,
                    "filter": {"type": {"$in": relevant_types}}
                }
            )

            # Create the prompt for generating Terraform code
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a Terraform expert. Using the provided reference templates, generate a complete Terraform configuration for Azure.
                The configuration should:
                1. Include all necessary variable declarations
                2. Follow Terraform best practices
                3. Include helpful comments
                4. Be properly formatted
                5. Maintain consistency with the reference templates
                
                Context: {context}"""),
                ("human", "{input}")
            ])

            # Create a chain to combine documents
            document_chain = create_stuff_documents_chain(
                llm=self.llm,
                prompt=prompt,
            )

            # Create the retrieval chain
            retrieval_chain = create_retrieval_chain(
                retriever,
                document_chain
            )

            # Generate the response
            response = retrieval_chain.invoke({
                "input": query
            })

            if "answer" not in response:
                raise ValueError("No response generated from the model")

            return response["answer"]
            
        except ValueError as e:
            # Re-raise validation errors to be handled by the UI
            raise
        except Exception as e:
            st.error(f"Error in generate_terraform: {str(e)}")
            raise Exception(f"Failed to generate Terraform configuration: {str(e)}") 
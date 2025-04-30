from Models.gpt4omini import query_model  
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser

def llm_rephrase(query: str) -> str:
    template = ChatPromptTemplate.from_template("""
    Rephrase this user query to be more search-friendly for a vector database.
    In case there is query related to services, rephrase this query and search from 'servicesoffereds' collection.
    Query:'{query}'
 """
    )
    prompt = template.format(query=query)
    response = query_model(prompt)
    rewritten_query = StrOutputParser().parse(response)
    
    #return response.choices[0].message.content.strip()
    return rewritten_query.content.strip();
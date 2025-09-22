from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain_ollama import OllamaLLM
from langchain.schema import HumanMessage, AIMessage
from app.tools import get_order_status, get_product_info, get_warranty_policy
from app.db import save_message, get_last_messages
import re
import os

# Initialize LLM
llm = OllamaLLM(
    model="llama3.2:3b",
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    temperature=0.1,
)

tools = [get_order_status, get_product_info, get_warranty_policy]

# Memory configuration
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

system_prompt = """Kamu adalah customer service toko fashion Indonesia. Wajib jawab dalam bahasa Indonesia.

ATURAN:
1. Status pesanan: gunakan get_order_status
2. Info produk: gunakan get_product_info  
3. Kebijakan garansi: gunakan get_warranty_policy
4. DILARANG gunakan bahasa Inggris

Contoh jawaban:
- "Pesanan #2001 dikirim via JNE, tiba 25 September 2025"
- "Dress Summer seharga Rp 299.000, bahan katun premium"
- "Garansi 30 hari untuk semua produk fashion"""

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    memory=memory,
    verbose=False,
    max_iterations=2,
    early_stopping_method="generate",
    handle_parsing_errors=True,
    agent_kwargs={'system_message': system_prompt}
)

def classify_intent(message):
    """Classify user intent for efficient routing"""
    msg = message.lower()
    
    # Order status queries
    if any(pattern in msg for pattern in ["pesanan", "status", "dimana", "order"]) and re.search(r'\d+', msg):
        return "order_status"
    
    # Product info queries
    products = ["dress", "jaket", "kemeja", "celana", "produk", "info", "harga"]
    if any(prod in msg for prod in products):
        return "product_info"
    
    # Warranty queries
    warranty_terms = ["garansi", "retur", "tukar", "warranty", "claim"]
    if any(term in msg for term in warranty_terms):
        return "warranty"
    
    # Name introduction
    if "nama saya" in msg and not any(q in msg for q in ["siapa", "apa"]):
        return "introduction"
    
    # Memory queries
    memory_patterns = ["siapa nama", "nama saya siapa", "pertanyaan sebelum", "tanya tadi"]
    if any(pattern in msg for pattern in memory_patterns):
        return "memory_query"
    
    # Greeting patterns
    greetings = ["halo", "hai", "selamat", "hello"]
    if any(greet in msg for greet in greetings) and len(msg.split()) <= 4:
        return "greeting"
    
    return "general"

def extract_name(text):
    """Extract name from user introduction"""
    patterns = [
        r"nama saya (?:adalah )?(\w+)",
        r"saya (\w+)",
        r"perkenalkan.*?(\w+)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            return match.group(1).title()
    return None

def handle_memory_query(message, history):
    """Handle conversation memory queries efficiently"""
    msg = message.lower()
    
    # Name recall
    if "nama" in msg:
        for h in history:
            if h["role"] == "user":
                name = extract_name(h["message"])
                if name:
                    return f"Nama Anda adalah {name}."
        return "Saya belum mengetahui nama Anda dalam percakapan ini."
    
    # Previous question recall
    if "pertanyaan" in msg or "tanya" in msg:
        user_messages = [h["message"] for h in history if h["role"] == "user"]
        if len(user_messages) > 1:
            return f'Pertanyaan sebelumnya: "{user_messages[-2]}"'
        return "Ini pertanyaan pertama Anda."
    
    return "Maaf, saya tidak memahami pertanyaan tentang percakapan sebelumnya."

def direct_tool_call(intent, message):
    """Direct tool calling for deterministic responses"""
    
    if intent == "order_status":
        numbers = re.findall(r'\d+', message)
        if numbers:
            return get_order_status(numbers[0])
        return "Mohon berikan nomor pesanan yang valid."
    
    elif intent == "product_info":
        msg = message.lower()
        
        # Check if asking for ALL PRODUCTS
        if any(phrase in msg for phrase in ["apa saja", "tersedia", "semua produk", "daftar produk"]):
            from app.db import get_all_products
            products = get_all_products()
            if products:
                product_list = []
                for p in products:
                    harga = f"Rp {int(p['price']):,}".replace(',', '.')
                    product_list.append(f"* {p['name']} - {harga}")
                
                return f"""Produk yang tersedia di toko kami:

                {chr(10).join(product_list)}

                Mau info detail produk mana?"""
            else:
                return "Maaf, sedang tidak ada produk yang tersedia."
        
        # Specific product inquiry
        product_map = {
            "dress": "Dress Summer",
            "jaket": "Jaket Denim", 
            "kemeja": "Kemeja Formal",
            "celana": "Celana Jeans"
        }
        
        for keyword, product_name in product_map.items():
            if keyword in msg:
                return get_product_info(product_name)
        
        # Default -> show product list if no specific product found
        return direct_tool_call("product_info", "apa saja yang tersedia")
    
    elif intent == "warranty":
        return get_warranty_policy("")
    
    return None

def clean_response(response):
    """Basic Indonesian language enforcement"""
    replacements = {
        "order": "pesanan",
        "status": "status", 
        "being": "sedang",
        "currently": "saat ini",
        "shipped": "dikirim",
        "delivered": "diantarkan"
    }
    
    for eng, ind in replacements.items():
        response = response.replace(eng, ind)
    
    # Remove AI prefixes
    if response.startswith(("AI:", "Assistant:", "Bot:")):
        response = response.split(":", 1)[1].strip()
    
    return response

def run_chat(session_id: str, message: str) -> str:
    """Main chat processing with efficient intent routing"""
    try:
        # Load conversation history (3 interactions = 6 messages)
        history = get_last_messages(session_id, limit=3)
        
        # Update agent memory
        memory.clear()
        for h in history:
            if h["role"] == "user":
                memory.chat_memory.add_message(HumanMessage(content=h["message"]))
            else:
                memory.chat_memory.add_message(AIMessage(content=h["message"]))
        
        # Save current message
        save_message(session_id, "user", message)
        memory.chat_memory.add_message(HumanMessage(content=message))
        
        # Classify intent for efficient routing
        intent = classify_intent(message)
        reply = None
        
        # RULE-BASED responses for specific intents
        if intent == "greeting":
            reply = "Halo! Selamat datang di toko fashion kami. Ada yang bisa saya bantu?"
        
        elif intent == "introduction":
            name = extract_name(message)
            if name:
                reply = f"Halo {name}! Senang berkenalan. Ada yang ingin ditanyakan tentang produk fashion kami?"
            else:
                reply = "Halo! Senang berkenalan dengan Anda. Ada yang bisa saya bantu?"
        
        elif intent == "memory_query":
            reply = handle_memory_query(message, history)
        
        # DIRECT TOOL CALLS
        elif intent in ["order_status", "product_info", "warranty"]:
            reply = direct_tool_call(intent, message)
        
        # AGENT for complex/general queries
        if reply is None:
            try:
                result = agent.invoke({"input": message})
                reply = result.get("output", "")
                
                # Fallback if agent fails
                if not reply or len(reply.strip()) < 5:
                    reply = "Maaf, bisa dijelaskan lebih detail pertanyaannya?"
                
            except Exception as agent_error:
                # Direct LLM fallback
                indonesian_prompt = f"""Sebagai customer service toko fashion, jawab dalam bahasa Indonesia: 
                {message}
                Jawaban:"""
                reply = llm.invoke(indonesian_prompt)
        
        # Clean and validate response
        if reply:
            reply = clean_response(reply.strip())
        else:
            reply = "Maaf, ada masalah teknis. Silakan coba lagi."
        
        # Save and return
        save_message(session_id, "assistant", reply)
        return reply
        
    except Exception as e:
        error_msg = "Maaf, terjadi kesalahan. Silakan coba lagi."
        save_message(session_id, "assistant", error_msg)
        return error_msg
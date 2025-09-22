# Fashion Store Chatbot

Chatbot customer support untuk platform toko online fashion menggunakan LLM lokal dengan Ollama dan Llama3.2:3b.

## 🚀 Cara Instalasi & Requirements

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Git

### Option 1: Docker Setup (Recommended)

```bash
# Clone repository
git clone <repository-url>
cd chatbot-challenge

# Start services
docker-compose up --build -d

# Download model (first time only)
docker exec ollama-server ollama pull llama3.2:3b

# Test API
curl http://localhost:8000/
```

### Option 2: Local Development Setup

```bash
# Clone repository
git clone <repository-url>
cd chatbot-challenge

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install & start Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &
ollama pull llama3.2:3b

# Initialize database
python init_db.py

# Start FastAPI server
uvicorn main:app --reload --port 8000
```

## 🗄️ Desain Database

### ERD Overview
```
conversation_history          products                orders
├── id (PK)                  ├── id (PK)            ├── id (PK)
├── session_id               ├── name               ├── customer_name
├── role                     ├── description        ├── status
├── message                  ├── price              ├── shipping_provider
└── timestamp                ├── category           ├── eta
                             └── stock              └── total_amount
```

### Tabel `conversation_history`
Menyimpan history percakapan untuk memory system
- `session_id`: Identifier unik per user session
- `role`: 'user' atau 'assistant'
- `message`: Isi pesan
- `timestamp`: Waktu pesan (auto-generated)

### Tabel `products`
Katalog produk fashion
- `name`: Nama produk (Dress Summer, Jaket Denim, dll)
- `description`: Deskripsi detail produk
- `price`: Harga dalam Rupiah
- `category`: Kategori produk
- `stock`: Jumlah stok tersedia

### Tabel `orders`
Data pesanan customer
- `id`: Nomor pesanan (2001, 2002, 2003)
- `status`: Status pesanan (Dikirim, Dikemas, Menunggu Pembayaran)
- `shipping_provider`: Provider pengiriman (JNE, SiCepat)
- `eta`: Estimasi waktu tiba

## 📚 Library & Framework

### Core Dependencies
- **FastAPI**: Modern web framework untuk API
- **Uvicorn**: ASGI server untuk FastAPI
- **Langchain**: Framework untuk aplikasi LLM
- **Langchain-Ollama**: Ollama integration untuk Langchain
- **Pydantic**: Data validation dan serialization

### Infrastructure
- **SQLite**: Database ringan untuk development
- **Docker**: Containerization untuk deployment
- **Ollama**: Runtime untuk LLM lokal

## 🤖 Model LLM

**Model**: `llama3.2:3b`
- **Size**: ~2GB
- **Provider**: Ollama (local deployment)
- **Temperature**: 0.1 (konsisten responses)
- **Context**: Support conversation memory
- **Language**: Dioptimasi untuk Bahasa Indonesia

## 💬 Daftar Pertanyaan yang Dapat Dijawab

### 1. Status Pesanan
```
✅ "Status pesanan 2001 gimana?"
✅ "Dimana pesanan saya 2002?"
✅ "Pesanan 2003 udah sampai belum?"
❌ "Pesanan 9999" → Tidak ditemukan
```

### 2. Informasi Produk
```
✅ "Info tentang Dress Summer"
✅ "Jaket Denim bagaimana?"
✅ "Produk apa saja yang tersedia?"
✅ "Harga Kemeja Formal berapa?"
```

### 3. Kebijakan Garansi
```
✅ "Bagaimana cara claim garansi?"
✅ "Garansi berlaku berapa lama?"
✅ "Bisa retur tidak?"
✅ "Syarat tukar ukuran gimana?"
```

### 4. Conversation Memory
```
✅ "Nama saya Malinda" → Disimpan untuk recall
✅ "Siapa nama saya?" → "Nama Anda adalah Malinda"
✅ "Apa pertanyaan sebelumnya?" → Recall 3 interaksi terakhir
```

### 5. General Conversation
```
✅ "Halo" → Greeting response
✅ "Terima kasih" → Polite response
✅ "Selamat pagi" → Natural conversation
```

## 🛠️ Daftar Tool Calls

### `get_order_status(order_id)`
**Fungsi**: Mengecek status pesanan berdasarkan ID
**Input**: Nomor pesanan (2001, 2002, 2003)
**Output**: Status, provider pengiriman, dan ETA
```python
# Contoh usage
get_order_status("2001")
# Return: "Pesanan #2001 Dikirim via JNE, estimasi tiba 2025-09-25."
```

### `get_product_info(product_name)`
**Fungsi**: Mendapatkan informasi detail produk
**Input**: Nama produk (partial matching)
**Output**: Nama, deskripsi, harga, dan stok
```python
# Contoh usage
get_product_info("Dress Summer")
# Return: Detail lengkap dengan harga Rp 299.000
```

### `get_warranty_policy(question)`
**Fungsi**: Menampilkan kebijakan garansi dan retur
**Input**: Pertanyaan terkait garansi (optional)
**Output**: Policy lengkap 30 hari garansi
```python
# Contoh usage
get_warranty_policy("")
# Return: Kebijakan lengkap garansi & retur
```

## 🏗️ Architecture & Flow

### Request Flow
```
User Input → Intent Classification → Tool Selection → LLM Processing → Response
     ↓
Database ← Memory Loading ← Session Management ← Response Cleanup
```

### Intent Classification
- **Rule-based detection** untuk queries umum (greeting, introduction)
- **Keyword matching** untuk tool selection (pesanan, produk, garansi)
- **Agent processing** untuk complex queries
- **Memory queries** untuk conversation recall

### Memory System
- **3 interaksi terakhir** per session tersimpan
- **Automatic loading** dari database setiap request
- **Session isolation** antar user
- **Name extraction & recall** untuk personalisasi

## 🧪 Testing

### API Testing
```bash
# Health check
curl http://localhost:8000/

# Chat endpoint
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"session_id": "test", "message": "Halo!"}'
```

### Automated Testing
```bash
# Run test scenarios
python test/test_scenarios.py
```

### Test Coverage
- ✅ All 3 core requirements (pesanan, produk, garansi)
- ✅ Memory functionality (3 interaksi)
- ✅ Error handling (invalid inputs)
- ✅ Session isolation
- ✅ Tool integration

## 🐳 Docker Deployment

### Services Architecture
```yaml
ollama:          # Official Ollama image
  - Port: 11434
  - Model: llama3.2:3b
  
chatbot:         # Custom Python application
  - Port: 8000
  - FastAPI + Langchain
  - Database: SQLite volume
```

### Commands
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild after changes
docker-compose up --build
```

## 🔧 Development

### Local Development
```bash
# Start only Ollama in Docker
docker-compose up ollama -d

# Run chatbot locally with hot reload
uvicorn main:app --reload --port 8000
```

### Code Structure
```
chatbot-challenge/
├── app/
│   ├── chatbot.py      # Main chat logic
│   ├── db.py           # Database operations
│   └── tools.py        # LLM tools
├── data/
│   ├── schema.sql      # Database schema
│   └── *.db           # SQLite files
├── test/
│   └── test_scenarios.py
├── docker-compose.yaml
├── Dockerfile
├── main.py            # FastAPI app
└── requirements.txt
```
---

**Developed for Synapsis Jr. AI Engineer Challenge**
from langchain.tools import tool
from app.db import get_order_by_id, get_product_by_name
import re

@tool
def get_order_status(order_id) -> str:
    """Check status based on ID"""
    
    # Extract number from input
    order_id_str = str(order_id).strip()
    numbers = re.findall(r'\d+', order_id_str)
    
    if not numbers:
        return "Harap berikan nomor ID pesanan yang valid (contoh: 2001)"
    
    try:
        order_id_int = int(numbers[0])
    except (ValueError, IndexError):
        return "Format ID pesanan tidak valid"

    order = get_order_by_id(order_id_int)
    if order:
        return f"Pesanan #{order_id_int} sedang {order['status']} via {order['shipping_provider']}, estimasi tiba {order['eta']}."
    else:
        return f"Pesanan #{order_id_int} tidak ditemukan dalam sistem."

@tool
def get_product_info(product_name: str) -> str:
    """Take product info including desc and price"""
    product = get_product_by_name(product_name)
    
    if not product:
        return f"Maaf, produk '{product_name}' tidak ditemukan di katalog kami. Produk yang tersedia: Dress Summer, Jaket Denim, Kemeja Formal, Celana Jeans."
    
    # Price in rupiah
    harga = f"Rp {int(product['price']):,}".replace(',', '.')
    
    return f"""Informasi Produk: {product['name']}. {product['description']} Harganya {harga}. Saat ini tersedia {product['stock']} unit."""

@tool
def get_warranty_policy(question: str = "") -> str:
    """Information about warranty and return"""
    return """Kebijakan Garansi & Return:

- Garansi: 30 hari untuk semua produk fashion
- Syarat: Produk dalam kondisi asli dengan tag lengkap
- Proses: Hubungi customer service dengan nomor pesanan
- Waktu Proses: 3-5 hari kerja

Untuk klaim garansi, siapkan nomor pesanan dan foto produk."""
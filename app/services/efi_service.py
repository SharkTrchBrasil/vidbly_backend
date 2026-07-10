import os
from efipay import EfiPay
from ..core.config import settings

def get_efi_client():
    # Only initialize if credentials are provided to avoid crash in dev
    if not settings.EFI_CLIENT_ID or not settings.EFI_CLIENT_SECRET:
        return None
        
    options = {
        'client_id': settings.EFI_CLIENT_ID,
        'client_secret': settings.EFI_CLIENT_SECRET,
        'sandbox': True, # Change to False in production
        'certificate': settings.EFI_CERTIFICATE_PATH # Path to .pem file
    }
    return EfiPay(options)

def create_pix_charge(job_id: str, amount: float):
    efi = get_efi_client()
    if not efi:
        # Mock response for dev when no credentials
        return {
            "txid": "mock_txid_12345",
            "loc": {"id": 1},
            "status": "ATIVA",
            "valor": {"original": str(amount)}
        }
        
    body = {
        "calendario": {
            "expiracao": 3600 # 1 hour to pay
        },
        "valor": {
            "original": f"{amount:.2f}"
        },
        "chave": settings.PIX_KEY,
        "infoAdicionais": [
            {
                "nome": "Job ID",
                "valor": str(job_id)
            }
        ]
    }
    
    response = efi.pix_create_charge(body=body)
    return response

def generate_pix_qrcode(loc_id: int):
    efi = get_efi_client()
    if not efi:
        return {
            "qrcode": "mock_qrcode_string_base64",
            "imagemQrcode": "data:image/png;base64,mock"
        }
        
    params = {
        "id": loc_id
    }
    response = efi.pix_generate_QRCode(params=params)
    return response

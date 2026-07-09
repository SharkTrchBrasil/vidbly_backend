import stripe
from ..core.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_connect_account(email: str, first_name: str, last_name: str, cpf: str) -> str:
    """
    Cria uma conta conectada na Stripe (tipo Express) para o criador.
    """
    account = stripe.Account.create(
        type="express",
        country="BR",
        email=email,
        business_type="individual",
        individual={
            "first_name": first_name,
            "last_name": last_name,
            "id_number": cpf,
        },
        capabilities={
            "transfers": {"requested": True},
        },
    )
    return account.id

def generate_onboarding_link(account_id: str, return_url: str, refresh_url: str) -> str:
    """
    Gera o link temporário para a tela hospedada pela Stripe (Onboarding KYC).
    """
    account_link = stripe.AccountLink.create(
        account=account_id,
        refresh_url=refresh_url,
        return_url=return_url,
        type="account_onboarding",
    )
    return account_link.url

def check_onboarding_status(account_id: str) -> bool:
    """
    Verifica se o criador já terminou de preencher todos os dados exigidos.
    """
    account = stripe.Account.retrieve(account_id)
    # Se requirements.currently_due estiver vazio, ele forneceu tudo o que é necessário no momento
    if len(account.requirements.currently_due) == 0:
        return True
    return False

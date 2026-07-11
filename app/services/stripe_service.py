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

def transfer_to_creator(account_id: str, amount: float) -> str:
    """
    Transfere o valor pago para a conta conectada do criador.
    amount deve ser em reais (ex: 50.00). Stripe usa centavos, então multiplicamos por 100.
    """
    transfer = stripe.Transfer.create(
        amount=int(amount * 100),
        currency="brl",
        destination=account_id,
    )
    return transfer.id

def create_stripe_customer(email: str, name: str) -> str:
    """
    Creates a customer on Stripe for the brand.
    """
    customer = stripe.Customer.create(
        email=email,
        name=name
    )
    return customer.id

def create_checkout_session(customer_id: str, amount: float, currency: str, job_id: str, success_url: str, cancel_url: str) -> str:
    """
    Creates a Stripe Checkout session to pay for a job.
    """
    session = stripe.checkout.Session.create(
        customer=customer_id,
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': currency,
                'product_data': {
                    'name': f'Job Payment - {job_id}',
                },
                'unit_amount': int(amount * 100),
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            'job_id': job_id
        }
    )
    return session.url

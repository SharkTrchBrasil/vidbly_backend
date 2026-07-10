from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..database import get_db
from ..models.product import Product
from ..models.brand import BrandProfile
from ..models.user import User
from ..schemas.product import ProductCreate, ProductUpdate, ProductResponse
from ..core.dependencies import get_current_active_user

router = APIRouter()


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add a product to the brand's catalog."""
    brand = db.query(BrandProfile).filter(BrandProfile.user_id == current_user.id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand profile not found")
    
    product = Product(
        brand_id=brand.id,
        name=payload.name,
        description=payload.description,
        product_url=payload.product_url,
        photo_url=payload.photo_url,
        product_type=payload.product_type,
        requires_shipping=payload.requires_shipping
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/", response_model=List[ProductResponse])
def list_my_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all products in the brand's catalog."""
    brand = db.query(BrandProfile).filter(BrandProfile.user_id == current_user.id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand profile not found")
    
    products = db.query(Product).filter(Product.brand_id == brand.id).all()
    return products


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: UUID,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a product in the catalog."""
    brand = db.query(BrandProfile).filter(BrandProfile.user_id == current_user.id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand profile not found")
    
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.brand_id == brand.id
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)
    
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a product from the catalog."""
    brand = db.query(BrandProfile).filter(BrandProfile.user_id == current_user.id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand profile not found")
    
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.brand_id == brand.id
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(product)
    db.commit()

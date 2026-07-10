from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.creator_tag import CreatorTag
from ..schemas.creator_tag import CreatorTagBase, CreatorTagResponse
from ..core.dependencies import get_current_active_user

router = APIRouter()

# Pre-seeded tags based on Billo's structure
DEFAULT_TAGS = [
    # Ethnicity
    {"category": "Ethnicity", "title": "Caucasiano"},
    {"category": "Ethnicity", "title": "Negro"},
    {"category": "Ethnicity", "title": "Pardo"},
    {"category": "Ethnicity", "title": "Asiático"},
    {"category": "Ethnicity", "title": "Indígena"},
    {"category": "Ethnicity", "title": "Multirracial/Outro"},
    # Language
    {"category": "Language", "title": "Português Nativo"},
    {"category": "Language", "title": "Inglês"},
    {"category": "Language", "title": "Espanhol"},
    # Appearance
    {"category": "Appearance", "title": "Casual & Relatable"},
    {"category": "Appearance", "title": "Profissional"},
    {"category": "Appearance", "title": "Fitness"},
    # Lifestyle
    {"category": "Lifestyle", "title": "Dono de Pet"},
    {"category": "Lifestyle", "title": "Pai/Mãe"},
    {"category": "Lifestyle", "title": "Dono de Veículo"},
    {"category": "Lifestyle", "title": "Entusiasta da Natureza"},
    {"category": "Lifestyle", "title": "Gamer"},
    # Occupation
    {"category": "Occupation", "title": "Influenciador"},
    {"category": "Occupation", "title": "Ator/Atriz"},
    {"category": "Occupation", "title": "Fotógrafo/Videógrafo"},
    {"category": "Occupation", "title": "Chef/Cozinheiro"},
    {"category": "Occupation", "title": "Empreendedor"},
    {"category": "Occupation", "title": "Professor/Educador"},
    {"category": "Occupation", "title": "Marketing"},
    # Interests
    {"category": "Interests", "title": "Culinária"},
    {"category": "Interests", "title": "Skincare & Beleza"},
    {"category": "Interests", "title": "Tecnologia"},
    {"category": "Interests", "title": "DIY"},
    {"category": "Interests", "title": "Moda"},
    {"category": "Interests", "title": "Saúde & Bem-estar"},
    {"category": "Interests", "title": "Esportes"},
]


@router.get("/", response_model=List[CreatorTagResponse])
def list_tags(
    category: str = None,
    db: Session = Depends(get_db)
):
    """List all available creator tags, optionally filtered by category."""
    query = db.query(CreatorTag)
    if category:
        query = query.filter(CreatorTag.category == category)
    return query.all()


@router.post("/seed", response_model=dict)
def seed_default_tags(
    db: Session = Depends(get_db)
):
    """Seed the database with default tags (run once on setup)."""
    existing = db.query(CreatorTag).count()
    if existing > 0:
        return {"message": f"Tags already seeded ({existing} tags exist)"}
    
    for tag_data in DEFAULT_TAGS:
        tag = CreatorTag(category=tag_data["category"], title=tag_data["title"])
        db.add(tag)
    
    db.commit()
    return {"message": f"Seeded {len(DEFAULT_TAGS)} default tags"}


@router.get("/categories", response_model=List[str])
def list_categories(db: Session = Depends(get_db)):
    """List all unique tag categories."""
    results = db.query(CreatorTag.category).distinct().all()
    return [r[0] for r in results]

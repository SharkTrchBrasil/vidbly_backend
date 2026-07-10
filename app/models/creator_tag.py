from sqlalchemy import Column, String, Integer, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database import Base

creator_tag_association = Table(
    "creator_tag_association",
    Base.metadata,
    Column("creator_id", UUID(as_uuid=True), ForeignKey("creator_profiles.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("creator_tags.id", ondelete="CASCADE"), primary_key=True)
)

class CreatorTag(Base):
    __tablename__ = "creator_tags"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True) # Ethnicity, Language, Appearance, Lifestyle, Occupation, Interests
    title = Column(String, nullable=False)

"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List

# ----------------------
# Portfolio App Schemas
# ----------------------

class SocialLink(BaseModel):
    label: str = Field(..., description="Platform name, e.g., GitHub")
    url: HttpUrl
    icon: Optional[str] = Field(None, description="Lucide icon name, e.g., github")

class Portfolio(BaseModel):
    """
    Portfolio settings (single-document collection)
    Collection name: "portfolio"
    """
    hero_title: str = Field("Hey, I'm Alex — Creative Developer", description="Main headline")
    hero_subtitle: str = Field("I build playful, interactive web experiences.", description="Secondary headline")
    about: str = Field(
        "I love crafting modern, interactive interfaces that feel alive."
    )
    socials: List[SocialLink] = Field(default_factory=list)

class Project(BaseModel):
    """
    Projects collection
    Collection name: "project"
    """
    title: str
    description: str
    tags: List[str] = Field(default_factory=list)
    image_url: Optional[str] = None
    link: Optional[str] = None
    featured: bool = False
    order: int = 0

# Example schemas retained for reference (not used by the app):
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = None
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True

# Note: The Flames database viewer can read these via GET /schema if implemented.

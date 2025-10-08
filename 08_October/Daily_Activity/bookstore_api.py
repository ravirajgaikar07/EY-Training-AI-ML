from fastapi import FastAPI, HTTPException, Query
from typing import Optional
from pydantic import BaseModel, Field

class Book(BaseModel):
    id: int
    title: str
    author: str
    price: float = Field(ge=0)
    in_stock: bool

books=[
    {"id": 1, "title": "Deep Learning", "author": "Ian Goodfellow", "price": 1200,"in_stock": True },
    {"id": 2, "title": "Machine Learning", "author": "Rian Goffredo", "price": 1000,"in_stock": True },
    {"id": 3, "title": "Deep Learning", "author": "Cleve Posht", "price": 900,"in_stock": False}
]

app=FastAPI()
@app.get("/books")
def get_all_books():
    return books

@app.get("/books/available")
def get_all_books_available():
    result= [book for book in books if book["in_stock"]==True]
    return result

@app.get("/books/count")
def get_all_books_count():
    return {"count":len(books)}

@app.get("/books/search")
def search_books(author : Optional[str] = Query(None),
                 max_price : Optional[int] = Query(None)):
    results = books
    if author:
        results = [book for book in results if book["author"].lower() == author.lower()]
    if max_price:
        results = [book for book in results if book["price"]<=max_price]
    return results

@app.get("/books/{book_id}")
def get_book(book_id:int):
    for data in books:
        if data["id"] == book_id:
            return data
    raise HTTPException(status_code=404, detail="Book not found")

@app.post("/books")
def add_book(book : Book):
    books.append(book.dict())
    return {"message": "Book added", "Book": book}

@app.put("/books/{book_id}")
def update_book(book_id : int, book : Book):
    for i, data in enumerate(books):
        if data["id"] == book_id:
            books[i]=book.dict()
            return {"message": "Book updated", "Book": book}
    raise HTTPException(status_code=404, detail="Book not found")

@app.delete("/books/{book_id}")
def delete_book(book_id : int):
    for i, data in enumerate(books):
        if data["id"] == book_id:
            del books[i]
            return {"message": "Book deleted successfully"}
    raise HTTPException(status_code=404, detail="Book not found")


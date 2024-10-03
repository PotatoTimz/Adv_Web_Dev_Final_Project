from flask import Flask, abort, jsonify, request
import bcrypt
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import Column, DateTime, String, ForeignKey, Integer, Float, Date, Table, Time

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///pokemon.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)    

PEPPER = b"thisissomepepper"

class PokemonType(db.Model):
    __tablename__ = "pokemon_type"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True) 
    pokemon_id = Column("pokemon_id", Integer, ForeignKey("pokemon.id"))
    type_id = Column("type_id", Integer, ForeignKey("type.id"))      

class Account(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True) 
    username: Mapped[str] = mapped_column(nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    salt: Mapped[str] = mapped_column(String(200), nullable=True)

class Pokemon(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True) 
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    #movelist_id: Mapped["MoveList"] = mapped_column(ForeignKey("MoveList.id"), nullable=False)
    types = relationship("Type", secondary="pokemon_type")

class Type(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True) 
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    pokemons = relationship("Pokemon", secondary="pokemon_type")


# class MoveList(db.Model):
#     id: Mapped[int] = mapped_column(primary_key=True)
#     moves: Mapped[list["Move"]] = relationship("Move", back_populates="movelist")

class DamageCategory(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True) 
    category: Mapped[str] = mapped_column(unique=True, nullable=False)

# class Move(db.Model):
#     id: Mapped[int] = mapped_column(primary_key=True) 
#     name: Mapped[str] = mapped_column(unique=True, nullable=False)
#     power: Mapped[int] = mapped_column(nullable=True)
#     description: Mapped[str] = mapped_column(nullable=False)
#     accuracy: Mapped[int] = mapped_column(nullable=True)
#     pp: Mapped[int] = mapped_column(nullable=False)
#     type_id: Mapped[int] = mapped_column(ForeignKey("type.id"), nullable=False)
#     #damage_category_id: Mapped[int] = mapped_column(ForeignKey("damagecategory.id"), nullable=False)
#     move_list: Mapped["MoveList"] = relationship("MoveList", back_populates="moves")

def hash_password(password):
    salt = bcrypt.gensalt() 
    password_with_pepper = password.encode('utf-8') + PEPPER 
    hashed_password = bcrypt.hashpw(password_with_pepper, salt)
    
    return hashed_password, salt


@app.route("/type", methods=["GET", "POST"])
def manage_types():
    if request.method == "GET":
        types = Type.query.all()
        return jsonify([{"id": type.id, "name": type.name} for type in types])
    
    if request.method == "POST":
        data = request.json

        if not data or not data.get("name"):
            abort(400, "Invalid Input!")
        
        new_type = Type(name=data["name"])
        db.session.add(new_type)
        db.session.commit()
        return jsonify({"id": new_type.id, "name": new_type.name})

@app.route("/pokemon", methods=["GET", "POST"])
def manage_pokemon():
    if request.method == "GET":
        pokemons = Pokemon.query.all()
        return jsonify([{"id": pokemon.id, "name": pokemon.name} for pokemon in pokemons])

    if request.method == "POST":
        data = request.json

        if not data or not data.get("name") or not data.get("types"):
            abort(400, "Invalid Input!")
        
        types = []

        for type in data.get("types"):
            types.append(Type.query.filter_by(name=type).first())
        
        new_pokemon = Pokemon(name=data["name"])
        db.session.add(new_pokemon)
        db.session.commit()

        for curr_type in types:
            pokemon_type_relation = PokemonType(pokemon_id=new_pokemon.id, type_id=curr_type.id)
            db.session.add(pokemon_type_relation)
        
        db.session.commit()

        return jsonify({"id": new_pokemon.id, "name": new_pokemon.name})

@app.route("/pokemontype", methods=["GET"])  
def manage_pokemon_type():
    pokemons_type = PokemonType.query.all()
    return jsonify([{"id": relation.id, "pokemon_id": relation.pokemon_id, "type_id": relation.type_id} for relation in pokemons_type])

@app.route("/damagecategory", methods=["GET", "POST"])
def manage_damage_category():
    if request.method == "GET":
        damage_categories = DamageCategory.query.all()
        return jsonify({"id": category.id, "category": category.category} for category in damage_categories)
    
    if request.method == "POST":
        data = request.json

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data or not data.get("username") or not data.get("password"):
        abort(400, "Invalid Input")
    
    username = data.get("username")
    password = data.get("password")
    
    if Account.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists. Please enter a unique username!"}), 401
    
    hashed_password, salt = hash_password(password)
    
    new_account = Account(username=username, hashed_password=hashed_password, salt=salt)
    db.session.add(new_account)
    db.session.commit()
    
    return jsonify({"message": "User registred successfully!"}), 201
 
if __name__ == "__main__":
    app.run(debug=True)

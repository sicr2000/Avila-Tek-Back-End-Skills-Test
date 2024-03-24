from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    """Esto se refiere a un usuario que puede ser un comprador o conductor, 
    todo usuario debe tener la siguiente información:

    - Nombre
    - Apellido
    - Email
    - Password    
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    lastname = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    createdAt = db.Column(db.DateTime, nullable=False)

    def init(self, name, lastname, email, password):
        self.name = name
        self.lastname = lastname
        self.email = email
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "lastname": self.lastname,
            "email": self.email,
            # do not serialize the password, its a security breach
        }
    
class Products(db.Model):
    """Esto se refiere a un producto del inventario, 
    todo producto debe tener la siguiente información:

    - Nombre
    - Descripción
    - Imagen
    - Cantidad
    - Precio    
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    image = db.Column(db.String(1700), nullable=True)
    amount = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float(4,2), nullable=False)

    def __init__(self, name, price, image, amount=1, description=''):
        self.name = name
        self.description = description
        self.image = image
        self.amount = amount
        self.price = price

    @classmethod
    def create(cls, name, price, amount, image, description):
        new_product = cls(name=name, price=price, image=image, amount=amount, description=description)
        try:
            db.session.add(new_product)
            db.session.commit()
            return new_product
        except ValueError as err:
            print(err)
            return None
        
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "image_url": self.image,
            "quantity": self.amount,
            "price": self.price
        }
    
class Address(db.Model):
    """Esto se refiere a una dirección del comprador, 
    toda dirección debe tener la siguiente información:

    - País
    - Ciudad
    - Dirección   
    """

    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(80), nullable=False)
    city = db.Column(db.String(80), nullable=False)
    address = db.Column(db.String(80), nullable=False)

    def __init__(self, country, city, address):
        self.country = country
        self.city = city
        self.address = address

    def serialize(self):
        return {
            "id": self.id,
            "address": self.address,
        }

class Customer(User):
    """Esto se refiere a un conductor que es un usuario, 
    todo conductor debe tener la siguiente información:

    - Nombre
    - Apellido
    - Email
    - Password
    - País
    - Ciudad
    - Dirección   
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    delivery_address_id = db.Column(db.Integer, db.ForeignKey('address.id'))
    createdAt = db.Column(db.DateTime, nullable=False)
    salt = db.Column(db.String(128))

    delivery_address = db.relationship('Address')

    def __init__(self, email, password, address, salt, name, lastname, createdAt):
        super().__init__(email=email, password=password, salt=salt, name=name, lastname=lastname, createdAt=createdAt)
        self.delivery_address = address

    def serialize(self):
        return {
            "user": super().serialize(),
            "address": self.delivery_address.serialize()
        }
    
class Driver(User):
    """Esto se refiere a un conductor que es un usuario, 
    todo conductor debe tener la siguiente información:

    - Nombre
    - Apellido
    - Email
    - Password
    - Serial de Placa   
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    serial_plate = db.Column(db.String(10), nullable=False)
    createdAt = db.Column(db.DateTime, nullable=False)
    salt = db.Column(db.String(128))

    def __init__(self, email, password, serial_plate, salt, name, lastname, createdAt):
        super().__init__(email=email, password=password, salt=salt, name=name, lastname=lastname, createdAt=createdAt)
        self.serial_plate = serial_plate

    def serialize(self):
        return {
            "driver": super().serialize(),
            "serial_plate": self.serial_plate
        }

association_table = db.Table(
    "association_table_orders",
    db.Column("products", db.Integer ,db.ForeignKey("products.id")),
    db.Column("orders", db.Integer ,db.ForeignKey("orders.id")),
)

class Order(db.Model):
    """Esto se refiere a una orden que puede generar un usuario 
    para adquirir un producto, toda orden debe tener la siguiente 
    información:

    - Delivery ID
    - Comprador
    - Producto
    """
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)

    delivery_id = db.Column(db.Integer,db.ForeignKey('driver.id'))
    delivery = db.relationship("Driver")

    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    customer = db.relationship("Customer")

    products = db.relationship("Products", secondary=association_table)

    def __init__(self, delivery, customer):
        self.delivery = delivery
        self.customer = customer

    def serialize(self):
        return {
                "id": self.id,
                "customer_address": self.customer.delivery_address.serialize(),
                "items": [ pro.serialize() for pro in self.products]
            }
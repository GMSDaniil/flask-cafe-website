from flask import Flask, render_template, jsonify, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

with app.app_context():
    db.create_all()



class CafeForm(FlaskForm):
    cafe = StringField('Cafe name (required)', validators=[DataRequired()])
    location = StringField('Location name (required)', validators=[DataRequired()])
    map_url = StringField('Location on Google Maps (URL) (required)', validators=[DataRequired(), URL()])
    img_url = StringField('Cafe image (URL) (required)', validators=[DataRequired(), URL()])
    seats = StringField('How much seats are there? (required)', validators=[DataRequired()])
    coffee_price = StringField('Coffee price in £ (required)', validators=[DataRequired()])
    has_toilet = BooleanField('Has WC?')
    has_wifi = BooleanField('Has wifi?')
    has_sockets = BooleanField('Has sockets?')
    can_take_calls = BooleanField('Can you take calls there?')
    submit = SubmitField('Add new cafe')

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/cafes')
def cafes():
    all = db.session.execute(db.select(Cafe)).scalars()
    all_cafes = [item.to_dict() for item in all]
    return render_template('cafes.html', cafes = all_cafes)

@app.route('/add', methods=["GET", "POST"])
def add_cafe():
    form = CafeForm()
    if form.validate_on_submit():
        print('hi')
        new_cafe = Cafe(name=form.cafe.data,
                        map_url=form.map_url.data,
                        img_url=form.img_url.data,
                        location=form.location.data,
                        seats=form.seats.data,
                        coffee_price=form.coffee_price.data,
                        has_sockets=form.has_sockets.data,
                        has_wifi=form.has_wifi.data,
                        has_toilet=form.has_toilet.data,
                        can_take_calls=form.can_take_calls.data)
        try:
            db.session.add(new_cafe)
            db.session.commit()
        except:
            return render_template('add.html', form=form, error="Cafe with this name already exists")
        
        return redirect(url_for('cafes'))
    return render_template('add.html', form=form)


@app.route('/report_close/<int:cafe_id>', methods=["POST"])
def delete(cafe_id):
    try:
        cafe = db.get_or_404(Cafe, cafe_id)
    except:
        pass
    db.session.delete(cafe)
    db.session.commit()
    return redirect(url_for('cafes'))

if __name__ == "__main__":
    app.run(debug=True, port=3000)
    
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, DateField
from wtforms.validators import DataRequired
import config


class QueryForm(FlaskForm):
    event = SelectField("Event Label:", choices=config.EVENTS_MAP.values(), validators=[DataRequired()])
    start = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()])
    end = DateField('End Date', format='%Y-%m-%d', validators=[DataRequired()])
    data_source = SelectField("Data Source:", choices=config.DATA_SOURCES_GUI, validators=[DataRequired()])
    aggregation = SelectField("Aggregation:", choices=["Default", "Hourly", "Daily"], validators=[DataRequired()])
    submit = SubmitField("Generate Report 🔍")


class LoginForm(FlaskForm):
    username = StringField("Username:", validators=[DataRequired()])
    password = PasswordField("Password:", validators=[DataRequired()])
    submit = SubmitField("Log Me In 🙏")

from pony.orm import Database, Required, Json

from settings import DB_CONFIG

db = Database()
db.bind(**DB_CONFIG)
# TODO РЕР8
class UserState(db.Entity):
    user_id = Required(int, unique=True)
    scenario_name = Required(str)
    step_name = Required(str)
    context = Required(Json)

db.generate_mapping(create_tables=True)
import Database_interaction_functions

Database_interaction_functions.create_database()

Database_interaction_functions.add_candidate("Kandydat_A")
Database_interaction_functions.add_candidate("Kandydat_B")
from Database_interaction_functions import hash_value

# Only examples
hashed_jan_id = hash_value("Jan")
hashed_jan_password = hash_value("password1")
Database_interaction_functions.register_voter(hashed_jan_id, hashed_jan_password)

hashed_anna_id = hash_value("Anna")
hashed_anna_password = hash_value("password2")
Database_interaction_functions.register_voter(hashed_anna_id, hashed_anna_password)

hashed_kasia_id = hash_value("Kasia")
hashed_kasia_password = hash_value("password3")
Database_interaction_functions.register_voter(hashed_kasia_id, hashed_kasia_password)

hashed_julek_id = hash_value("Julek")
hashed_julek_password = hash_value("password4")
Database_interaction_functions.register_voter(hashed_julek_id, hashed_julek_password)

# Database_interaction_functions.cast_vote(1, 1)
# Database_interaction_functions.cast_vote(2, 2)

Database_interaction_functions.show_results()
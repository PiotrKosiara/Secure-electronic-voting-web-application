import Database_interaction_functions
from Database_interaction_functions import hash_value, encrypt_value

Database_interaction_functions.create_database()
Database_interaction_functions.add_candidate("Kandydat_A")
Database_interaction_functions.add_candidate("Kandydat_B")
Database_interaction_functions.add_candidate("Kandydat_C")


# Only examples
hashed_jan_id = hash_value("Jan")
hashed_jan_password = hash_value("password1")
encrypted_email_jan = encrypt_value("piotrek.kosiara@gmail.com")
Database_interaction_functions.register_voter(hashed_jan_id, hashed_jan_password, encrypted_email_jan)

hashed_anna_id = hash_value("Anna")
hashed_anna_password = hash_value("password2")
encrypted_email_ania = encrypt_value("binarnyk@gmail.com")
Database_interaction_functions.register_voter(hashed_anna_id, hashed_anna_password, encrypted_email_ania)

hashed_kasia_id = hash_value("Kasia")
hashed_kasia_password = hash_value("password3")
encrypted_email_kasia = encrypt_value("binkasia@gmail.com")
Database_interaction_functions.register_voter(hashed_kasia_id, hashed_kasia_password, encrypted_email_kasia)

hashed_julek_id = hash_value("Julek")
hashed_julek_password = hash_value("password4")
encrypted_email_julek = encrypt_value("bin21@gmail.com")
Database_interaction_functions.register_voter(hashed_julek_id, hashed_julek_password, encrypted_email_julek)

# Database_interaction_functions.cast_vote(1, 1)
# Database_interaction_functions.cast_vote(2, 2)

Database_interaction_functions.show_results()